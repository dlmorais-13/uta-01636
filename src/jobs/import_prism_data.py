import os
import json
import logging
from typing import get_args
from arcgis.features import FeatureSet, Feature, FeatureLayer, Table
from geopandas import gpd, GeoDataFrame
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from rasterstats import zonal_stats
import rasterio
from rasterio.mask import mask
import xarray

# from concurrent.futures import ProcessPoolExecutor
# import numpy as np
# import pandas as pd

from src.jobs.job import Job
from src.settings import settings
from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.apis.prism_downloader import (
    PrismDownloader,
    PRISM_VARIABLES,
    PRISM_WS_VARIABLES,
    PRISM_TYPES,
    PRISM_INTERVALS,
    PRISM_RESOLUTIONS,
)

# from src.utils.agol_geopandas_converter import AgolGeopandasConverter

LOGGER = logging.getLogger(__name__)


class ImportPrismData(Job):
    """
    Class to import the prism data into AGOL.
    Will download the data from prism, intersect with the study area,
    and upload to AGOL.

    Usage:
    job = ImportPrismData()
    await job.logic({
        'resolution': '800m'
    })

    Resolution must be either '800m' or '4km'.
    """

    agol_api: AgolAPI

    async def logic(self, params: dict):
        resolution: PRISM_RESOLUTIONS = params["resolution"]
        interval: PRISM_INTERVALS = params["interval"]
        type: PRISM_TYPES = params["type"]
        startDate: dt = params["startDate"]
        endDate: dt = params["endDate"]

        self.agol_api = AgolAPI_Injector()

        mesh_data_table_ref = self.agol_api.get_table_ref(
            settings.agol_prism_data_layer_id
        )

        mesh_layer_ref = self.agol_api.get_layer_ref(
            settings.agol_prism_mesh_layer_id, resolution
        )
        mesh_layer_feature_set: FeatureSet = mesh_layer_ref.query(
            where="1=1", return_geometry=True, out_sr=settings.agol_default_crs
        )

        if len(mesh_layer_feature_set.features) == 0:
            raise Exception("Mesh layer is empty.")

        # Instantiate a GeoDataFrame from the layer.
        mesh_gdf = gpd.GeoDataFrame.from_features(
            json.loads(mesh_layer_feature_set.to_geojson),
            crs=f"EPSG:{settings.agol_default_crs}",
        )
        LOGGER.info("Retrieved mesh feature layer from AGOL.")

        if type == "normals":
            await self.import_normals(
                mesh_gdf,
                mesh_layer_ref,
                mesh_data_table_ref,
                startDate,
                endDate,
                resolution,
                interval,
            )
        elif type == "time_series":
            await self.import_timeseries(
                mesh_gdf, mesh_data_table_ref, startDate, endDate, resolution, interval
            )

    async def import_timeseries(
        self,
        mesh_gdf: GeoDataFrame,
        mesh_data_table_ref: Table,
        startDate: dt,
        endDate: dt,
        resolution: PRISM_RESOLUTIONS,
        interval: PRISM_INTERVALS,
    ):
        mesh_gdf = mesh_gdf.drop(columns=["county", "row", "col", "GlobalID"])
        mesh_gdf = mesh_gdf.rename(columns={"OBJECTID": "mesh_unit_id"})

        prism_downloader = PrismDownloader()

        current_dt = startDate
        while current_dt <= endDate:
            for variable in get_args(PRISM_WS_VARIABLES):
                LOGGER.info(
                    f'Extracting PRISM data for "{current_dt}|{resolution}|time_series|{interval}|{variable}"'
                )
                data_path = prism_downloader.get_data_path(
                    resolution, "time_series", variable, interval, current_dt
                )
                if data_path is not None:
                    nc_file_name = next(
                        f for f in os.listdir(data_path) if f.endswith(".nc")
                    )
                    nc_full_path = os.path.join(data_path, nc_file_name)
                    nc_data = xarray.open_dataset(nc_full_path)

                    for idx in mesh_gdf.index:
                        lat = mesh_gdf.loc[idx, "lat"]
                        lon = mesh_gdf.loc[idx, "lon"]
                        mesh_gdf.at[idx, variable] = nc_data.sel(
                            lat=lat, lon=lon, method="nearest"
                        )["Band1"].values.item()
                    LOGGER.info(
                        f"Added variable {variable} to {len(mesh_gdf)} mesh units of resolution {resolution}."
                    )

            print(mesh_gdf.head())

            features_to_add, features_to_edit = self.create_features_list_from_mesh_gdf(
                mesh_data_table_ref,
                mesh_gdf,
                current_dt,
                "time_series",
                interval,
                resolution,
            )
            self.agol_api.batch_edit(
                mesh_data_table_ref, features_to_add, features_to_edit
            )

            current_dt += relativedelta(months=+1)

    async def import_normals(
        self,
        mesh_gdf: GeoDataFrame,
        mesh_layer_ref: FeatureLayer,
        mesh_data_table_ref: Table,
        startDate: dt,
        endDate: dt,
        resolution: PRISM_RESOLUTIONS,
        interval: PRISM_INTERVALS,
    ):
        mesh_gdf = mesh_gdf.drop(columns=["county", "lat", "lon", "GlobalID"])
        mesh_gdf = mesh_gdf.rename(columns={"OBJECTID": "mesh_unit_id"})

        mesh_min_max_query = mesh_layer_ref.query(
            out_statistics=[
                {
                    "statisticType": "MIN",
                    "onStatisticField": "row",
                    "outStatisticFieldName": "min_row",
                },
                {
                    "statisticType": "MAX",
                    "onStatisticField": "row",
                    "outStatisticFieldName": "max_row",
                },
                {
                    "statisticType": "MIN",
                    "onStatisticField": "col",
                    "outStatisticFieldName": "min_col",
                },
                {
                    "statisticType": "MAX",
                    "onStatisticField": "col",
                    "outStatisticFieldName": "max_col",
                },
            ]
        )
        min_row = mesh_min_max_query.features[0].attributes["min_row"]
        max_row = mesh_min_max_query.features[0].attributes["max_row"]
        min_col = mesh_min_max_query.features[0].attributes["min_col"]
        max_col = mesh_min_max_query.features[0].attributes["max_col"]

        prism_downloader = PrismDownloader()
        raster_data_cache: dict = {}

        current_dt = startDate
        while current_dt <= endDate:
            for variable in get_args(PRISM_VARIABLES):
                LOGGER.info(
                    f'Extracting PRISM data for "{current_dt}|{resolution}|normals|{interval}|{variable}"'
                )
                data_path = prism_downloader.get_data_path(
                    resolution, "normals", variable, interval, current_dt
                )
                if data_path is not None:
                    tif_file_name = next(
                        f for f in os.listdir(data_path) if f.endswith(".tif")
                    )
                    raster_full_path = os.path.join(data_path, tif_file_name)
                    raster_data = await self.get_raster_data(
                        raster_data_cache,
                        raster_full_path,
                        min_row,
                        max_row,
                        min_col,
                        max_col,
                    )

                    for idx in mesh_gdf.index:
                        row = mesh_gdf.loc[idx, "row"]
                        col = mesh_gdf.loc[idx, "col"]
                        mesh_gdf.at[idx, variable] = raster_data[row][col]
                    LOGGER.info(
                        f"Added variable {variable} to {len(mesh_gdf)} mesh units of resolution {resolution}."
                    )

            print(mesh_gdf.head())

            features_to_add, features_to_edit = self.create_features_list_from_mesh_gdf(
                mesh_data_table_ref,
                mesh_gdf,
                current_dt,
                "normals",
                interval,
                resolution,
            )
            self.agol_api.batch_edit(
                mesh_data_table_ref, features_to_add, features_to_edit
            )

            current_dt += relativedelta(months=+1)

    def create_features_list_from_mesh_gdf(
        self,
        mesh_data_table_ref: FeatureLayer,
        gdf: GeoDataFrame,
        date: dt,
        type: PRISM_TYPES,
        interval: PRISM_INTERVALS,
        resolution: PRISM_RESOLUTIONS,
    ):
        LOGGER.info(f"Building list of features to save in AGOL.")

        date_string = date.strftime("%Y-%m-%d")
        current_features = mesh_data_table_ref.query(
            return_all_records=True,
            where=f"""
            measure_date = '{date_string}'
            AND measure_type = '{type}'
            AND resolution = '{resolution}'
            AND measure_interval = '{interval}'
            """,
        )
        LOGGER.info(f"Found {len(current_features)} features already saved in AGOL.")

        current_features = {
            f.attributes["mesh_unit_id"]: f.attributes
            for f in current_features.features
        }

        features_to_add = []
        features_to_edit = []

        for _, row in gdf.iterrows():
            feature_attrs = row.drop(
                ["geometry", "Shape__Area", "Shape__Length", "col", "row"]
            ).to_dict()
            current_feature = (
                current_features[row["mesh_unit_id"]]
                if row["mesh_unit_id"] in current_features
                else None
            )

            if current_feature is not None:
                features_to_edit.append(
                    Feature(attributes=current_feature | feature_attrs)
                )
            else:
                feature_attrs["measure_date"] = date_string
                feature_attrs["measure_type"] = type
                feature_attrs["resolution"] = resolution
                feature_attrs["measure_interval"] = interval
                features_to_add.append(Feature(attributes=feature_attrs))

        LOGGER.info(
            f"Found {len(features_to_add)} to add and {len(features_to_edit)} to update."
        )
        return features_to_add, features_to_edit

    async def get_raster_data(
        self,
        cache: dict,
        raster_path: str,
        min_row: int,
        max_row: int,
        min_col: int,
        max_col: int,
    ):
        if raster_path not in cache.keys():
            data = {}
            with rasterio.open(raster_path) as src:
                band = src.read(1)
                for r in range(min_row, max_row + 1):
                    data[r] = {}
                    for c in range(min_col, max_col + 1):
                        data[r][c] = band[r, c]
            cache[raster_path] = data
        return cache[raster_path]

    async def clip_raster_file(self, data_path: str, study_area_gdf: GeoDataFrame):
        tif_file_name = [
            f
            for f in os.listdir(data_path)
            if f.endswith(".tif") and f != "clipped.tif"
        ][0]
        raster_full_path = os.path.join(data_path, tif_file_name)

        with rasterio.open(raster_full_path) as src:
            if study_area_gdf.crs != src.crs:
                study_area_gdf = study_area_gdf.to_crs(src.crs)

            geometries = study_area_gdf.geometry.values
            clipped_image, clipped_transform = mask(src, geometries, crop=True)

            out_meta = src.meta.copy()
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": clipped_image.shape[1],
                    "width": clipped_image.shape[2],
                    "transform": clipped_transform,
                }
            )

        with rasterio.open(
            os.path.join(data_path, "clipped.tif"), "w", **out_meta
        ) as dest:
            dest.write(clipped_image)


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        ImportPrismData().logic(
            {
                "delete": True,
                "resolution": "4km",
                # 'resolution': '800m',
                # 'type': 'normals',
                "type": "time_series",
                "interval": "monthly",
                "startDate": dt.strptime("202001", "%Y%m"),
                # 'endDate': dt.strptime('202012', '%Y%m'),
                "endDate": dt.strptime("202001", "%Y%m"),
            }
        )
    )
