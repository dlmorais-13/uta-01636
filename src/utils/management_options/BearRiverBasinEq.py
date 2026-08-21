from src.utils.management_options.ManagementOption import ManagementOption


class BearRiverBasinEq(ManagementOption):
    """
    Management option to calculate the equilibrium of parcels
    located in the bear river basin.

    TODO Correct the schedule, current content is only a 
      temporary copied from sample.
    """

    def get_schedule_content(self):
        lines: list[list[int | str]] = []
        lines.append([1, 75, "CROP GI3"])
        lines.append([1, 75, "FRST"])
        lines.append([1, 106, "GRAZ GM"])
        lines.append([1, 136, "GRAZ GM"])
        lines.append([1, 167, "GRAZ GM"])
        lines.append([1, 197, "GRAZ GM"])
        lines.append([1, 228, "GRAZ GM"])
        lines.append([1, 259, "GRAZ GM"])
        lines.append([1, 289, "LAST"])
        lines.append([1, 289, "SENM"])
        lines.append([2, 75, "FRST"])
        lines.append([2, 106, "GRAZ GM"])
        lines.append([2, 136, "GRAZ GM"])
        lines.append([2, 167, "GRAZ GM"])
        lines.append([2, 197, "GRAZ GM"])
        lines.append([2, 228, "GRAZ GM"])
        lines.append([2, 259, "GRAZ GM"])
        lines.append([2, 289, "LAST"])
        lines.append([2, 289, "SENM"])
        lines.append([3, 75, "FRST"])
        lines.append([3, 106, "GRAZ GM"])
        lines.append([3, 136, "GRAZ GM"])
        lines.append([3, 167, "GRAZ GM"])
        lines.append([3, 197, "GRAZ GM"])
        lines.append([3, 228, "FIRE M"])
        lines.append([3, 289, "LAST"])
        lines.append([3, 289, "SENM"])
        return lines
