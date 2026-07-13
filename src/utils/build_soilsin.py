import os
from pandas import DataFrame, Series

from src.apis.ssurgo_api import Ssurgo_API


class BuildSoilsin():
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

    async def build(self, mapunit_key: int, components: DataFrame = None, chorizons: DataFrame = None):
        components = components if components is not None else (await self.ssurgo_api.get_ssurgo_components(mapunit_key))
        chorizons = chorizons if chorizons is not None else (await self.ssurgo_api.get_ssurgo_chorizon(components))

        soilsin_data = self.get_mapunit_soilsin_data(mapunit_key, components, chorizons)
        
        file_path = os.path.join(self.dir, 'soils.in')
        with open(file_path, 'w') as f:
            for layer in soilsin_data:
                f.write(''.join([
                    f'{l:<6.3f}' if isinstance(l, float) else f'{l:<6}'
                    for l in layer[1:]]
                ))
                f.write('\n')

        return soilsin_data


    def get_layer_data_from_horizon(self, upper_depth: int, lower_depth: int, horizon: Series) -> list[float]:
        layer_data: list[float] = []
        
        # Thickness
        layer_data.append(lower_depth - upper_depth)
        
        # Upper depth
        layer_data.append(upper_depth)
        
        # Lower depth
        layer_data.append(lower_depth)
        
        # Bulk density
        layer_data.append(float(horizon.at['dbthirdbar_r']))
        
        # Field capacity
        field_capacity = float(horizon.at['wthirdbar_r'])
        layer_data.append(field_capacity if field_capacity <= 1 else field_capacity / 100)
        
        # Wilting point
        # TODO This value cannot be zero. Check what to do in case it's zero in SSURGO.
        wilting_point = float(horizon.at['wfifteenbar_r'])
        layer_data.append(max(wilting_point if wilting_point <= 1 else wilting_point / 100, 0.01))
        
        # Evap Coefficient
        # Not used according to documentation.
        layer_data.append(0.0)
        
        # Frac. Roots
        layer_data.append(0.001)
        
        # Sand Fraction
        layer_data.append(float(horizon.at['sandtotal_r']) / 100)
        
        # Clay Fraction
        layer_data.append(float(horizon.at['claytotal_r']) / 100)
        
        # Organic Matter Fraction
        layer_data.append(float(horizon.at['om_r']) / 100)
        
        # Δmin
        layer_data.append(0.0)
        
        # ksat
        layer_data.append(float(horizon['ksat_r']) / 10000)
        
        # pH
        layer_data.append(float(horizon['ph1to1h2o_r']))

        # Round every float to 3 decimal places.
        layer_data[:] = [round(v, 3) for v in layer_data]
        return layer_data
    
    def combine_horizons(self, horizons: DataFrame, components: DataFrame):
        max_depth = int(horizons['hzdepb_r'].max())
        
        curr_depth = 0
        combined_layers: list[dict] = []

        special_depths = [[0, 2], [2, 5], [5, 10]]

        while curr_depth < max_depth - 1:

            special_depth = next((
                d
                for d in special_depths
                if d[0] == curr_depth
            ), None)

            if special_depth is not None:
                range_end = special_depth[1]
            else:
                range_end = int(horizons[horizons['hzdepb_r'].gt(curr_depth)].iloc[0]['hzdepb_r'])

            range_layers = horizons.loc[
                horizons['hzdept_r'].lt(range_end)
                & horizons['hzdepb_r'].ge(curr_depth)
            ]

            layers = [dict(layer[1]) for layer in range_layers.iterrows()]

            total_comp_perc = 0
            for layer in layers:
                comp = next((c for c in components.itertuples() if c.cokey == int(layer['cokey'])), None)
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
                awc=0
            )

            for layer in layers:
                comp = next((c for c in components.itertuples() if c.cokey == int(layer['cokey'])), None)
                comp_perc = float(comp.comppct_r)
                comp_part = comp_perc / total_comp_perc

                new_layer['sand'] += layer['sandtotal_r'] * comp_part
                new_layer['clay'] += layer['claytotal_r'] * comp_part
                new_layer['silt'] += layer['silttotal_r'] * comp_part
                new_layer['bulk_density'] += layer['dbthirdbar_r'] * comp_part
                new_layer['field_capacity'] += layer['wthirdbar_r'] * comp_part
                new_layer['wilting_point'] += layer['wfifteenbar_r'] * comp_part
                new_layer['organic_matter_fraction'] += layer['om_r'] * comp_part
                new_layer['ph'] += layer['ph1to1h2o_r'] * comp_part
                new_layer['ksat'] += layer['ksat_r'] * comp_part
                new_layer['awc'] += layer['awc_r'] * comp_part

            combined_layers.append(new_layer)   
            curr_depth = range_end

        print(combined_layers)
        return combined_layers

    def get_mapunit_soilsin_data(self, mukey: int, components: DataFrame, chorizon: DataFrame):
        mu_comps: DataFrame = components[components['mukey'] == mukey]
        mu_chorizon: DataFrame = chorizon[chorizon['cokey'].isin(mu_comps['cokey'].tolist())]
        mu_chorizon = mu_chorizon.sort_values(by=['hzdept_r', 'hzdepb_r'])

        combined_layers = self.combine_horizons(mu_chorizon, mu_comps)

        soilsin_data: list[list[float]] = []

        for static_layer in [[0, 2], [2, 5], [5, 10]]:
            
            layer_horizons = mu_chorizon.loc[
                mu_chorizon['hzdepb_r'].ge(static_layer[0])
                & mu_chorizon['hzdept_r'].lt(static_layer[1])
            ]

            # TODO Combine multiple horizons into one.
            combined_horizon = layer_horizons.iloc[0] if len(layer_horizons) == 1 else layer_horizons.iloc[0]
            soilsin_data.append(self.get_layer_data_from_horizon(static_layer[0], static_layer[1], combined_horizon))

        for _, layer in mu_chorizon.iterrows():
            # Ignore the horizons used fully in the static layers.
            if int(layer.at['hzdepb_r']) <= 10:
                continue

            top_depth = max(int(layer.at['hzdept_r']), 10)
            soilsin_data.append(self.get_layer_data_from_horizon(top_depth, int(layer['hzdepb_r']), layer))

        return soilsin_data


if __name__ == '__main__':
    import asyncio
    asyncio.run(BuildSoilsin('/tmp').build(482665))
