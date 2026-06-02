import soildb
from src.apis.crop_unit_to_lbs_converter import crop_unit_to_lbs

class Ssurgo_API:

    async def get_map_unit_data(self, map_unit_ids: list[str]):
        if not map_unit_ids:
            return []

        response = await soildb.fetch_by_keys(
            keys=map_unit_ids,
            table="mapunit",
            key_column="mukey",
            columns=['mukey', 'muname']
        )

        crop_yield_response = await soildb.fetch_by_keys(
            keys=map_unit_ids,
            table="mucropyld",
            key_column="mukey",
            columns=['mukey', 'cropname', 'yldunits', 'irryield_r']
        )

        mapunits = response.to_dict()
        crop_yield = crop_yield_response.to_dict()
        for mu in mapunits:
            mu['crop_yield'] = [cy for cy in crop_yield if str(cy['mukey']) == str(mu['mukey'])]
            self.sort_biggest_potential_crop_yield(mu)

        return mapunits

    def sort_biggest_potential_crop_yield(self, map_unit):
        if map_unit['crop_yield']:
            map_unit['crop_yield'].sort(
                key=lambda x: crop_unit_to_lbs(x['cropname'], x['yldunits'], x['irryield_r']),
                reverse=True
            )
