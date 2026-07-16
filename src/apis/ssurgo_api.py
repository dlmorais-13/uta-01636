import soildb
from pandas import DataFrame
from src.apis.crop_unit_to_lbs_converter import crop_unit_to_lbs


class Ssurgo_API:
    """
    Class to fetch data from SSURGO using soildb.
    """

    async def get_map_unit_data(self, map_unit_ids: list[str]):
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
            self.sort_biggest_potential_crop_yield(mu)

        return mapunits

    def sort_biggest_potential_crop_yield(self, map_unit):
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
        comp_response = await soildb.fetch_by_keys(
            keys=[mapunit_key],
            table="component",
            key_column="mukey",
            columns=["mukey", "cokey", "comppct_r", "majcompflag"] + extra_columns,
        )
        comp_df = comp_response.to_dataframe()
        return comp_df[comp_df["majcompflag"] == "Yes"]

    async def get_ssurgo_chorizon(self, components: DataFrame) -> DataFrame:
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
