from abc import ABC, abstractmethod

from src.utils.management_options.BearRiverBasinEq import BearRiverBasinEq


class ManagementOption(ABC):
    """
    Abstract class to model different management options
    for the simulations.
    """

    name: str
    params: dict

    def __init__(self, params: dict = {}):
        self.name = self.__class__.__name__
        self.params = params

    @abstractmethod
    def get_schedule_content(self):
        pass


def get_equilibrium_management_by_basin(basin: str) -> ManagementOption:
    """
    Function to get a management option according to a basin.

    Args:
      basin: The basin name.

    Returns:
      The instance of the equilibrium management to use for the basin.
    """

    match basin:
        case "Bear River":
            return BearRiverBasinEq()
        case "Columbia River":
            return BearRiverBasinEq()
        case "Jordan River":
            return BearRiverBasinEq()
        case "Sevier River":
            return BearRiverBasinEq()
        case "Uintah":
            return BearRiverBasinEq()
        case "Utah Lake":
            return BearRiverBasinEq()
        case "Weber River":
            return BearRiverBasinEq()
        case "West Colorado River":
            return BearRiverBasinEq()
        case "West Desert":
            return BearRiverBasinEq()
        case _:
            return BearRiverBasinEq()
