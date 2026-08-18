import logging
import tempfile
from arcgis.geometry import Geometry
from arcgis.features import Feature
from datetime import datetime as dt, timedelta

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.apis.daymet import DaymetDownloader

LOGGER = logging.getLogger(__name__)


class BuildWeatherFile:
    """
    Class to build the site.wth file for Daycent executions.

    It will create the file using the DayMet data accessed for the
    centroid of the parcel. The file will be created as a temporary
    file and it's path is returned.
    """

    agol_api: AgolAPI

    def __init__(self):
        """
        Constructs the builder.
        """

        self.agol_api = AgolAPI_Injector()

    async def build(self, parcel: Feature):
        """
        Builds the weather file and return its path.

        Args:
            parcel: The parcel to build the weather file for.
        """

        daymet = DaymetDownloader()
        parcel_centroid = Geometry(parcel.geometry).centroid
        elevation, daymet_data = await daymet.get_data(
            lat=parcel_centroid[1],
            lon=parcel_centroid[0],
            vars=["tmax", "tmin", "prcp"],
        )

        start_date = dt.strptime("19800101", "%Y%m%d")
        # TODO The end_date should be variable.
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
