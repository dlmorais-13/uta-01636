from src.utils.management_options.ManagementOption import ManagementOption, ExecType


class BearRiverBasinEq(ManagementOption):
    """
    Management option to calculate the equilibrium of parcels
    located in the bear river basin.

    TODO Correct the schedule, current content is only a temporary copied from sample.
    """

    def get_type(self) -> ExecType:
        return "equilibrium"

    def get_block_header(self):
        lines: list[list[int | str]] = []
        lines.append([self.block_number, "Block #"])
        lines.append([self.end_year, "Last year"])
        lines.append([3, "Repeats # years"])

        # TODO These should change for equilibrium and base.
        lines.append([self.start_year, "Output starting year"])
        lines.append([12, "Output month"])
        lines.append(["1.0", "Output interval"])

        # TODO Check if it is necessary to vary this input.
        lines.append(["F", "Weather choice"])
        lines.append(["site.wth"])

        return lines

    def get_block_content(self):
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

    def get_initial_system(self):
        lines: list[list[int | str]] = []
        lines.append([3, "Initial system"])
        lines.append(["GI3", "Initial crop"])
        lines.append(["TMDF", "Initial tree"])
        lines.append(["+100 12/31 ACEQ A"])
        return lines