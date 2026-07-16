import os
from pandas import DataFrame, Series

from src.apis.ssurgo_api import Ssurgo_API


class BuildSoilsin:
    """
    Class used to build the soils.in file for Daycent.

    This class will fetch the SSURGO mapunit data using soildb and will create the file
    in the designated folder.

    Will return the number of layers defined in soils.in file.

    Usage:
        build_soilsin = BuildSoilsin()
        await build_soilsin.build(tmpdir, mapunit_key))
    """

    ssurgo_api: Ssurgo_API
    dir: str

    def __init__(self, tmpdir: str):
        self.dir = tmpdir
        self.ssurgo_api = Ssurgo_API()

    async def build(
        self,
        mapunit_key: int,
        components: DataFrame = None,
        chorizons: DataFrame = None,
    ):
        components, chorizons = await self.load_components_and_chorizons(
            mapunit_key, components, chorizons
        )
        soilsin_data = self.get_mapunit_soilsin_data(mapunit_key, components, chorizons)

        file_path = os.path.join(self.dir, "soils.in")
        with open(file_path, "w") as f:
            for layer in soilsin_data:
                f.write(
                    "".join(
                        [
                            f"{l:<6.3f}" if isinstance(l, float) else f"{l:<6}"
                            for l in layer[1:]
                        ]
                    )
                )
                f.write("\n")

        return soilsin_data

    async def load_components_and_chorizons(
        self,
        mapunit_key: int,
        components: DataFrame = None,
        chorizons: DataFrame = None,
    ):
        """
        Load the data from SSURGO, if the arguments are None.
        If the data is already loaded, simply returns it.
        """

        components = (
            components
            if components is not None
            else (await self.ssurgo_api.get_ssurgo_components(mapunit_key))
        )
        chorizons = (
            chorizons
            if chorizons is not None
            else (await self.ssurgo_api.get_ssurgo_chorizon(components))
        )
        return components, chorizons

    def get_layer_data_from_horizon(
        self, upper_depth: int, lower_depth: int, horizon: dict
    ) -> list[float]:
        layer_data: list[float] = []

        # Thickness
        layer_data.append(lower_depth - upper_depth)

        # Upper depth
        layer_data.append(upper_depth)

        # Lower depth
        layer_data.append(lower_depth)

        # Bulk density
        layer_data.append(float(horizon["bulk_density"]))

        # Field capacity
        field_capacity = float(horizon["field_capacity"])
        layer_data.append(
            field_capacity if field_capacity <= 1 else field_capacity / 100
        )

        # Wilting point
        # TODO This value cannot be zero. Check what to do in case it's zero in SSURGO.
        wilting_point = float(horizon["wilting_point"])
        layer_data.append(
            max(wilting_point if wilting_point <= 1 else wilting_point / 100, 0.01)
        )

        # Evap Coefficient
        # Not used according to documentation.
        layer_data.append(0.0)

        # Frac. Roots
        # Cannot be defined as zero.
        # TODO Check value to use.
        layer_data.append(0.001)

        # Sand Fraction
        layer_data.append(float(horizon["sand"]) / 100)

        # Clay Fraction
        layer_data.append(float(horizon["clay"]) / 100)

        # Organic Matter Fraction
        layer_data.append(float(horizon["organic_matter_fraction"]) / 100)

        # Δmin
        layer_data.append(0.0)

        # ksat
        layer_data.append(float(horizon["ksat"]) / 10000)

        # pH
        layer_data.append(float(horizon["ph"]))

        # Round every float to 3 decimal places.
        layer_data[:] = [round(v, 3) for v in layer_data]
        return layer_data

    def combine_horizons(self, horizons: DataFrame, components: DataFrame):
        # Max depth in the horizon
        max_depth = int(horizons["hzdepb_r"].max())

        curr_depth = 0
        combined_layers: list[dict] = []

        # Special depths are recommended by DayCent.
        special_depths = [[0, 2], [2, 5], [5, 10]]

        # Iterate over the horizon depth.
        while curr_depth < max_depth - 1:

            # Check if iteration is in a special depth.
            special_depth = next(
                (d for d in special_depths if d[0] == curr_depth), None
            )

            # If part of a special depth, uses its boundaries.
            if special_depth is not None:
                range_end = special_depth[1]
            # Else, uses the next bottom depth defined in a layer.
            else:
                range_end = int(
                    horizons[horizons["hzdepb_r"].gt(curr_depth)].iloc[0]["hzdepb_r"]
                )

            # Find the layers within the range being computed.
            range_layers = horizons.loc[
                horizons["hzdept_r"].lt(range_end) & horizons["hzdepb_r"].ge(curr_depth)
            ]

            # Transform each layer into a regular dictionary.
            layers = [dict(layer[1]) for layer in range_layers.iterrows()]

            # Compute the total percentage of the soil composed by the components of the layers.
            total_comp_perc = 0
            for layer in layers:
                comp = next(
                    (
                        c
                        for c in components.itertuples()
                        if c.cokey == int(layer["cokey"])
                    ),
                    None,
                )
                total_comp_perc += float(comp.comppct_r)

            new_layer = dict(
                depth_top=curr_depth,
                depth_bottom=range_end,
                sand=0,
                clay=0,
                silt=0,
                bulk_density=0,
                field_capacity=0,
                wilting_point=0,
                organic_matter_fraction=0,
                ph=0,
                ksat=0,
                awc=0,
            )

            # For each layer, add its weighted value into the computed layer.
            for layer in layers:
                comp = next(
                    (
                        c
                        for c in components.itertuples()
                        if c.cokey == int(layer["cokey"])
                    ),
                    None,
                )
                comp_perc = float(comp.comppct_r)
                comp_part = comp_perc / total_comp_perc

                new_layer["sand"] += layer["sandtotal_r"] * comp_part
                new_layer["clay"] += layer["claytotal_r"] * comp_part
                new_layer["silt"] += layer["silttotal_r"] * comp_part
                new_layer["bulk_density"] += layer["dbthirdbar_r"] * comp_part
                new_layer["field_capacity"] += layer["wthirdbar_r"] * comp_part
                new_layer["wilting_point"] += layer["wfifteenbar_r"] * comp_part
                new_layer["organic_matter_fraction"] += layer["om_r"] * comp_part
                new_layer["ph"] += layer["ph1to1h2o_r"] * comp_part
                new_layer["ksat"] += layer["ksat_r"] * comp_part
                new_layer["awc"] += layer["awc_r"] * comp_part

            combined_layers.append(new_layer)

            # Continue iteration from the computed layer bottom depth.
            curr_depth = range_end

        return combined_layers

    def get_mapunit_soilsin_data(
        self, mukey: int, components: DataFrame, chorizon: DataFrame
    ):
        mu_comps: DataFrame = components[components["mukey"] == mukey]
        mu_chorizon: DataFrame = chorizon[
            chorizon["cokey"].isin(mu_comps["cokey"].tolist())
        ]
        mu_chorizon = mu_chorizon.sort_values(by=["hzdept_r", "hzdepb_r"])

        combined_layers = self.combine_horizons(mu_chorizon, mu_comps)

        soilsin_data: list[list[float]] = []

        for layer in combined_layers:
            soilsin_item = self.get_layer_data_from_horizon(
                layer["depth_top"], layer["depth_bottom"], layer
            )
            soilsin_data.append(soilsin_item)

        return soilsin_data


if __name__ == "__main__":
    import asyncio

    build_soilsin = BuildSoilsin("/tmp")
    mukey = 482665

    cmp, hor = asyncio.run(build_soilsin.load_components_and_chorizons(mukey))
    hor = hor.sort_values(by=["hzdept_r", "hzdepb_r"])
    data1 = build_soilsin.combine_horizons(hor, cmp)
    data2 = build_soilsin.get_mapunit_soilsin_data(mukey, cmp, hor)
    from tabulate import tabulate

    print(tabulate(data1, headers="keys", tablefmt="grid"))

    asyncio.run(build_soilsin.build(mukey, cmp, hor))
