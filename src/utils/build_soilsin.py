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

    async def build(self, mapunit_key: int):
        components = await self.ssurgo_api.get_ssurgo_components(mapunit_key)
        chorizons = await self.ssurgo_api.get_ssurgo_chorizon(components)
        soilsin_data = self.get_mapunit_soilsin_data(mapunit_key, components, chorizons)
        
        file_path = os.path.join(self.dir, 'soils.in')
        with open(file_path, 'w') as f:
            for layer in soilsin_data:
                f.write(' '.join([f'{l}' for l in layer]))
                f.write('\n')

        return len(soilsin_data)


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
        wilting_point = float(horizon.at['wfifteenbar_r'])
        layer_data.append(wilting_point if wilting_point <= 1 else wilting_point / 100)
        # Evap Coefficient
        layer_data.append(0.0)
        # Frac. Roots
        layer_data.append(0.0)
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
    
    def get_mapunit_soilsin_data(self, mukey: int, components: DataFrame, chorizon: DataFrame):
        mu_comps: DataFrame = components[components['mukey'] == mukey]
        mu_chorizon: DataFrame = chorizon[chorizon['cokey'].isin(mu_comps['cokey'].tolist())]
        mu_chorizon = mu_chorizon.sort_values(by='hzdept_r')

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
