import logging
import os
import hashlib
import requests
from typing import Literal

from src.settings import settings

LOGGER = logging.getLogger(__name__)

"""
The list of variables accepted by Daymet API.
- tmax (degrees C): Daily maximum 2-meter air temperature.
- tmin (degrees C): Daily minimum 2-meter air temperature.
- dayl (s/day): Duration of the daylight period for the day. This calculation is based on the period of the day during which the sun is above a hypothetical flat horizon.
- prcp (mm/day): Daily total precipitation, sum of all forms converted to water-equivalent.
- srad (W/m^2): Incident shortwave radiation flux density, taken as an average over the daylight period of the day.
- swe (kg/m^2): Snow water equivalent. The amount of water contained within the snowpack.
- vp (Pa): Water Vapor Pressure. Daily average partial pressure of water vapor.
"""
DAYMET_VARIABLES = Literal["dayl", "prcp", "srad", "swe", "tmax", "tmin", "vp"]


class DaymetDownloader:
    """
    Class to download data from Daymet Single Pixel Extraction Tool.
    https://daymet.ornl.gov/single-pixel/

    Will download the data from a single coordinate (lat, lon), using the whole range of dates from 1980 to 2025.
    By default, the variables tmax, tmin and prcp are returned, along with the elevation (meters) of the coordinate.
    """

    async def get_data(
        self,
        lat: float,
        lon: float,
        vars: list[DAYMET_VARIABLES] = ["tmax", "tmin", "prcp"],
    ):
        """
        Get the weather data from DayMet for a given point (lat, lon). Along
        with the elevation of the point. By default, the variables tmax, tmin, and prcp are read.

        Args:
            lat: The point latitude.
            lon: The point longitude.
            vars: The list of variables begin read.
                Optional. Default to tmax, tmin, and prcp.

        Returns:
            A tuple with the elevation and the weather data. The weather data
            is a dictionary with keys being the year and day of year (1 to 365),
            and the values are another dictionary, containing the keys "year", "day",
            and more one key for each of the requested variables. The variable values
            are floats and the other values are integers.
        """

        filename_str = f"lat_{lat}_lon_{lon}_vars_{'|'.join(sorted(vars))}"
        filename = f"{hashlib.md5(filename_str.encode()).hexdigest()}.csv"

        workdir = os.path.join(settings.workdir, "daymet", filename[0:2])
        os.makedirs(workdir, exist_ok=True)
        file_path = os.path.join(workdir, filename)

        if not os.path.exists(file_path):
            await self._download_data(lat, lon, vars, file_path)

        elevation: int | None = None
        headers: dict | None = None
        data: dict = {}

        with open(file_path, "r") as file:
            for line in file:

                # If elevation was not read yet, check to read it.
                if elevation is None:
                    if line.startswith("Elevation:"):
                        elevation = int("".join([c for c in line if c.isdigit()]))

                # If elevation was read, check if reached header.
                elif line.startswith("year,yday,"):
                    # Build the headers as a dict mapping the variable name to its column index.
                    headers = {
                        col.split(" ")[0]: idx
                        for idx, col in enumerate(line.split(","))
                    }

                # If header was reached, process line as data.
                elif headers is not None:
                    line_data = line.split(",")
                    data_dict = {"year": int(line_data[0]), "day": int(line_data[1])}

                    # For each variable, get its value.
                    for var in vars:
                        data_dict[var] = float(line_data[headers[var]])

                    data[f"{line_data[0]}_{line_data[1]}"] = data_dict

        return elevation, data

    async def _download_data(
        self, lat: float, lon: float, vars: list[DAYMET_VARIABLES], file_path: str
    ):
        """
        Download the DayMet data for a point and list of variables.

        Args:
            lat: The point latitude.
            lon: The point longitude.
            vars: The list of variables being read.
            file_path: The complete file path to save the file, including the name.
        """

        query_params = ["format=csv", "start=1980-01-01", "end=2025-12-31"]
        query_params += [f"lat={lat}", f"lon={lon}", f"vars={','.join(vars)}"]
        url = f"{settings.daymet_base_url}/api/data?{'&'.join(query_params)}"

        try:
            # Make a GET request to the URL, set stream=True for large files
            response = requests.get(url, stream=True)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            LOGGER.info(f"Downloading file {url} ")

            # Open the file in binary write mode ('wb') and write the content in chunks
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(
                    chunk_size=8192
                ):  # Iterate over chunks
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
        except requests.exceptions.HTTPError as httpError:
            LOGGER.error(f"An error occurred: {httpError}")
            raise Exception("Error downloading data from Daymet") from httpError
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"An error occurred: {e}")
            raise Exception("Error downloading data from Daymet") from e


if __name__ == "__main__":
    import asyncio

    asyncio.run(DaymetDownloader().get_data(40.5, -111.11))
