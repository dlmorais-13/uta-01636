import soildb

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

        return response.to_dict()
