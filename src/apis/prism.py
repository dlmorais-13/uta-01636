import logging
import os
import hashlib
import requests
import json
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from typing import Literal

from src.settings import settings

LOGGER = logging.getLogger(__name__)

PRISM_VARIABLES = Literal[
    "ppt", "tmin", "tmean", "tmax", "vpdmin", "vpdmax", "tdmean", "soltotal", "solslope"
]

PRISM_FIRST_YEAR = 1895
PRISM_LAST_YEAR = 2025

PRISM_API_URL = settings.prism_api_url
PRISM_API_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7,ja-JP;q=0.6,ja;q=0.5",
    "connection": "keep-alive",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "host": "prism.oregonstate.edu",
    "origin": "https://prism.oregonstate.edu",
    "referer": "https://prism.oregonstate.edu/explorer/",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
PRISM_API_DEFAULT_DATA = {
    "spares": "4km",
    "interp": "idw",
    # "stats": "ppt tmin tmax",
    "units": "si",
    "range": "monthly",
    "start": "189501",
    "end": "202512",
    "stability": "Unlikely to change",
    # "lon": "-111.8412",
    # "lat": "41.7419",
    "elev": "1400",
    "call": "pp/monthly_timeseries",
    "proc": "gridserv",
}


class PrismAPI:
    """
    Class to download Prism data from a single point using the API
    used in Prism Data Explorer. Only queries monthly time series.
    """

    async def get_data(
        self,
        lat: float,
        lon: float,
        vars: list[PRISM_VARIABLES] = ["tmax", "tmin", "ppt"],
    ):
        """
        Get the weather data from Prism for a given point (lat, lon). Along
        with the elevation of the point. By default, the variables tmax, tmin, and ppt are read.

        Args:
            lat: The point latitude.
            lon: The point longitude.
            vars: The list of variables begin read.
                Optional. Default to tmax, tmin, and ppt.

        Returns:
            A dictionary with the weather data. The dictionary has keys
            being the year and month of year, and the values are another
            dictionary, containing the keys "year", "day", and more one 
            key for each of the requested variables. The variable values
            are floats and the other values are integers.
        """

        filename_str = f"lat_{lat}_lon_{lon}_vars_{'|'.join(sorted(vars))}"
        filename = f"{hashlib.md5(filename_str.encode()).hexdigest()}.json"

        workdir = os.path.join(settings.workdir, "prism", "api", filename[0:2])
        os.makedirs(workdir, exist_ok=True)
        file_path = os.path.join(workdir, filename)

        if not os.path.exists(file_path):
            await self._download_data(lat, lon, vars, file_path)

        data: dict = {}
        with open(file_path, "r") as file:
            json_data = json.load(file)

            for v in vars:
                var_data = json_data["result"]["data"][v]

                current_dt = dt.strptime(f"{PRISM_FIRST_YEAR}01", "%Y%m")
                for value in var_data:
                    date_string = current_dt.strftime("%Y_%m")

                    if date_string not in data:
                        data[date_string] = {
                            "year": current_dt.strftime("%Y"),
                            "month": current_dt.strftime("%m"),
                        }

                    data[date_string][v] = float(value)
                    current_dt += relativedelta(months=+1)

        return data

    async def _download_data(
        self, lat: float, lon: float, vars: list[PRISM_VARIABLES], file_path: str
    ):
        """
        Download the Prism data for a point and list of variables.

        Args:
            lat: The point latitude.
            lon: The point longitude.
            vars: The list of variables being read.
            file_path: The complete file path to save the file, including the name.
        """

        try:
            response = requests.post(
                url=PRISM_API_URL,
                headers=PRISM_API_HEADERS,
                data={
                    **PRISM_API_DEFAULT_DATA,
                    "lat": f"{lat}",
                    "lon": f"{lon}",
                    "stats": " ".join(vars),
                },
            )
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

        except requests.exceptions.HTTPError as httpError:
            LOGGER.error(f"An error occurred: {httpError}")
            raise Exception("Error downloading data from Prism") from httpError
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"An error occurred: {e}")
            raise Exception("Error downloading data from Prism") from e


if __name__ == "__main__":
    import asyncio

    data = asyncio.run(PrismAPI().get_data(40.5, -111.11))
    print(data)
