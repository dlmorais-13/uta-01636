import soildb
from pandas import DataFrame
from src.apis.crop_unit_to_lbs_converter import crop_unit_to_lbs


class Ssurgo_API:
    """
    Class to fetch data from SSURGO using soildb.
    """

    async def get_map_unit_data(self, map_unit_ids: list[str]) -> dict:
        """
        Returns the data relative to a list of map units in SSURGO.

        Args:
            map_unit_ids: The IDs of the map units, named "mukey" in SSURGO.

        Returns:
            A list of dictionaries with the data for each map unit. In each
            dictionary, the keys present are mukey (map unit key), muname (map
            unit name), and crop_yield, with a list of the potential crops and
            their respective name (cropname), amount (irryield_r), and measurement
            unit (yldunits).
        """

        if not map_unit_ids:
            return []

        response = await soildb.fetch_by_keys(
            keys=map_unit_ids,
            table="mapunit",
            key_column="mukey",
            columns=["mukey", "muname"],
        )

        crop_yield_response = await soildb.fetch_by_keys(
            keys=map_unit_ids,
            table="mucropyld",
            key_column="mukey",
            columns=["mukey", "cropname", "yldunits", "irryield_r"],
        )

        mapunits = response.to_dict()
        crop_yield = crop_yield_response.to_dict()
        for mu in mapunits:
            mu["crop_yield"] = [
                cy for cy in crop_yield if str(cy["mukey"]) == str(mu["mukey"])
            ]
            self._sort_biggest_potential_crop_yield(mu)

        return mapunits

    def _sort_biggest_potential_crop_yield(self, map_unit: dict):
        """
        Sorts inplace the list of crop yield in the map unit
        data decrementally according to the potential yield in lbs.

        Args:
            map_unit: Map unit dict to have the crop yield sorted.
        """

        if map_unit["crop_yield"]:
            map_unit["crop_yield"].sort(
                key=lambda x: crop_unit_to_lbs(
                    x["cropname"], x["yldunits"], x["irryield_r"]
                ),
                reverse=True,
            )

    async def get_ssurgo_components(
        self, mapunit_key: int, extra_columns: list[str] = []
    ) -> DataFrame:
        """
        Gets the components of a SSURGO map unit. Only the major
        components are returned (majcompflag is "Yes").

        Args:
            mapunit_key: The SSURGO map unit key.
            extra_columns: A list of columns to be returned from the
                components. Optional. Defaults to an empty list.

        Returns:
            The found components as a Pandas Dataframe, containing
            the columns of map unit key (mukey), component key (cokey),
            component area percentage of map unit (comppct_r), flag
            indicating it is a major component (majcompflag, always
            "Yes"), along with all the extra columns from the arguments.
        """

        comp_response = await soildb.fetch_by_keys(
            keys=[mapunit_key],
            table="component",
            key_column="mukey",
            columns=["mukey", "cokey", "comppct_r", "majcompflag"] + extra_columns,
        )
        comp_df = comp_response.to_dataframe()
        return comp_df[comp_df["majcompflag"] == "Yes"]

    async def get_ssurgo_chorizon(self, components: DataFrame) -> DataFrame:
        """
        Gets from SSURGO the soil horizon (list of layers) of a list of components.

        Args:
            components: The list of components to get their horizon.

        Returns:
            A Pandas Dataframe with the soil horizon data of all the
            components. The list of layers is not separated by component.
            The following columns are returned.
            - chkey: ID of the layer.
            - cokey: ID of the soil component.
            - hzdept_r: Distance from the top of the layer to the soil.
            - hzdepb_r: Distance from the bottom of the layer to the soil.
            - sandtotal_r: Percentage of sand in the layer.
            - claytotal_r: Percentage of clay in the layer.
            - silttotal_r: Percentage of silt in the layer.
            - dbthirdbar_r: The oven dry weight of the less than 2 mm soil
                material per unit volume of soil at a water tension of 1/3 bar.
                Used for column "bulk density" of soils.in.
            - wthirdbar_r: The volumetric content of soil water retained at
                a tension of 1/3 bar (33 kPa), expressed as a percentage of
                the whole soil. Used for column "field capacity" of soils.in.
            - wfifteenbar_r: The volumetric content of soil water retained at
                a tension of 15 bars (1500 kPa), expressed as a percentage of
                the whole soil. Used for column "wilting_point" of soils.in.
            - om_r: The amount by weight of decomposed plant and animal residue
                expressed as a weight percentage of the less than 2 mm soil
                material. Used for column "organic matter fraction of soils.in.
            - ph1to1h2o_r: The negative logarithm to the base 10, of the
                hydrogen ion activity in the soil using the 1:1 soil-water
                ratio method. A numerical expressionof the relative acidity or
                alkalinity of a soil sample. Used for column "ph" of soils.in.
            - ksat_r: The amount of water that would move vertically through
                a unit area of saturated soil in unit time under unit hydraulic
                gradient. Used for column "ksat" of soils.in.
            - awc_r: The amount of water that an increment of soil depth,
                inclusive of fragments, can store that is available to plants.
                Used for column "awc" of soils.in.
        """

        hz_response = await soildb.fetch_by_keys(
            keys=components["cokey"].tolist(),
            table="chorizon",
            key_column="cokey",
            columns=[
                "chkey",
                "cokey",
                "hzdept_r",
                "hzdepb_r",
                "sandtotal_r",
                "claytotal_r",
                "silttotal_r",
                "dbthirdbar_r",
                "wthirdbar_r",
                "wfifteenbar_r",
                "om_r",
                "ph1to1h2o_r",
                "ksat_r",
                "awc_r",
            ],
        )
        return hz_response.to_dataframe()
