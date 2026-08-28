from src.utils.management_options.BearRiverBasinEq import BearRiverBasinEq
from src.utils.management_options.ManagementOption import ManagementOption


def get_equilibrium_management_by_basin(
    basin: str, start_year: int, end_year: int, params: dict = {}
) -> ManagementOption:
    """
    Function to get a management option according to a basin.

    Args:
      basin: The basin name.

    Returns:
      The instance of the equilibrium management to use for the basin.
    """

    # TODO Only BearRiver "implemented". Implement the other basins.
    match basin:
        case "Bear River":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "Columbia River":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "Jordan River":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "Sevier River":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "Uintah":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "Utah Lake":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "Weber River":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "West Colorado River":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case "West Desert":
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
        case _:
            return BearRiverBasinEq("equilibrium", start_year, end_year, params)
