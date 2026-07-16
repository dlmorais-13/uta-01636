import logging
import tempfile
from arcgis.geometry.filters import intersects
from arcgis.geometry import Geometry
from arcgis.features import Feature
from datetime import datetime as dt, timedelta

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.apis.prism_downloader import PRISM_RESOLUTIONS, PRISM_INTERVALS, PRISM_TYPES
from src.apis.daymet import DaymetDownloader
from src.settings import settings

LOGGER = logging.getLogger(__name__)


class BuildWeatherFile:
    """
    Class to build the site.wth file for Daycent executions.

    It will create the file using the PRISM data saved in ArcGIS Online.
    The file will be created as a temporary file and it's path is returned.
    """

    agol_api: AgolAPI

    def __init__(self):
        self.agol_api = AgolAPI_Injector()

    async def build_daymet(self, parcel: Feature):
        daymet = DaymetDownloader()
        parcel_centroid = Geometry(parcel.geometry).centroid
        elevation, daymet_data = await daymet.get_data(
            lat=parcel_centroid[1],
            lon=parcel_centroid[0],
            vars=["tmax", "tmin", "prcp"],
        )

        start_date = dt.strptime("19800101", "%Y%m%d")
        end_date = dt.strptime("20251231", "%Y%m%d")
        with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as tmp_file:
            current_date = start_date
            while current_date <= end_date:
                day_of_month = current_date.day
                month = current_date.month
                year = current_date.year
                day_of_year = current_date.timetuple().tm_yday

                date_data = daymet_data[f"{year}_{min(365, day_of_year)}"]
                tmax = "{:.3f}".format(date_data["tmax"])
                tmin = "{:.3f}".format(date_data["tmin"])
                # Set precipitation in cm in DayCent (DayMet returns in mm)
                ppt = "{:.3f}".format(date_data["prcp"] / 10)
                tmp_file.write(
                    f"{day_of_month}\t{month}\t{year}\t{day_of_year}\t{tmax}\t{tmin}\t{ppt}\n"
                )

                current_date += timedelta(days=1)

            tmp_file.flush()
            file_name = tmp_file.name

        return elevation, file_name

    async def build_prism(
        self,
        parcel: Feature,
        resolution: PRISM_RESOLUTIONS,
        interval: PRISM_INTERVALS,
        type: PRISM_TYPES,
    ):
        mesh_id = await self.get_mesh_grid_id(
            parcel.attributes["parcel_key"], resolution
        )
        prism_data = await self.get_prism_data_for_mesh_unit(
            mesh_id, resolution, interval, type
        )

        if type == "normals":
            start_date = dt.strptime("19910101", "%Y%m%d")
            end_date = dt.strptime("20201231", "%Y%m%d")

        with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as tmp_file:
            current_date = start_date
            while current_date <= end_date:
                data = (
                    prism_data[current_date.strftime("2020-%m-01")]
                    if type == "normals"
                    else prism_data[current_date.strftime("%Y-%m-%d")]
                )

                day_of_month = current_date.day
                month = current_date.month
                year = current_date.year
                day_of_year = current_date.timetuple().tm_yday
                tmax = "{:.3f}".format(data["tmax"])
                tmin = "{:.3f}".format(data["tmin"])
                ppt = "{:.3f}".format(data["ppt"])
                tmp_file.write(
                    f"{day_of_month}\t{month}\t{year}\t{day_of_year}\t{tmax}\t{tmin}\t{ppt}\n"
                )

                current_date += timedelta(days=1)

            tmp_file.flush()
            file_name = tmp_file.name

        return None, file_name

    async def get_mesh_grid_id(self, parcel_key: int, resolution: PRISM_RESOLUTIONS):
        LOGGER.info(f"Retrieving PRISM mesh unit id from AGOL.")
        base_layer_ref = self.agol_api.get_layer_ref(settings.agol_base_layer_id)
        parcel = base_layer_ref.query(
            where=f"parcel_key = {parcel_key}", return_geometry=True
        ).features[0]
        LOGGER.info(f"Parcel loaded from AGOL base layer.")

        mesh_layer_ref = self.agol_api.get_layer_ref(
            settings.agol_prism_mesh_layer_id, resolution
        )
        intersecting_mesh_units = mesh_layer_ref.query(
            geometry_filter=intersects(
                geometry=parcel.geometry, sr=parcel.geometry["spatialReference"]
            ),
            return_geometry=True,
        )
        LOGGER.info(
            f"Found {len(intersecting_mesh_units.features)} intersecting mesh unit(s) found."
        )

        parcel_shape_geom = Geometry(parcel.geometry)

        mesh_units_intersection_with_area = []
        for feature in intersecting_mesh_units.features:
            shapely_target_geom = Geometry(feature.geometry)
            intersection_area = parcel_shape_geom.intersect(shapely_target_geom).area
            mesh_units_intersection_with_area.append(
                {"feature": feature, "intersection_area": intersection_area}
            )

        mesh_units_intersection_with_area.sort(
            key=lambda x: x["intersection_area"], reverse=True
        )
        mesh_unit = mesh_units_intersection_with_area[0]["feature"]
        mesh_unit_id = mesh_unit.attributes["OBJECTID"]
        LOGGER.info(f"Found mesh unit with id {mesh_unit_id}")
        return mesh_unit_id

    async def get_prism_data_for_mesh_unit(
        self,
        mesh_unit_id,
        resolution: PRISM_RESOLUTIONS,
        interval: PRISM_INTERVALS,
        type: PRISM_TYPES,
    ):
        LOGGER.info(
            f"Retrieving PRISM data for {mesh_unit_id}|{resolution}|{interval}|{type}"
        )
        prism_data_ref = self.agol_api.get_table_ref(settings.agol_prism_data_layer_id)
        query_res = prism_data_ref.query(
            where=f"measure_type = '{type}' AND resolution = '{resolution}' AND mesh_unit_id = {mesh_unit_id}",
            return_all_records=True,
        )
        LOGGER.info(f"Found {len(query_res.features)} records.")
        return {f.attributes["measure_date"]: f.attributes for f in query_res.features}
