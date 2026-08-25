from src.utils.management_options.ManagementOption import ManagementOption, ExecType


class Monoculture(ManagementOption):
    """
    Management option for continuous crop (monoculture).
    Will create a schedule where every season the same crop is
    planted and harvested.

    Params:
        fert: Type of fertilization event to use. If not defined,
            no fertilization event is added to the schedule.
        crop: Type of the crop for the monoculture.
        cult: Type of the cultivation/tillage event. If not defined,
            no cultivation/tillage event is added to the schedule.
        harv: Type of the harvesting event.

    TODO Add parameters for the days of the events.
    """

    def get_type(self) -> ExecType:
        return "simulation"

    def get_block_header(self):
        lines: list[list[int | str]] = []
        lines.append([self.block_number, "Block #"])
        lines.append([self.end_year, "Last year"])
        lines.append([1, "Repeats # years"])

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

        if "fert" in self.params:
            lines.append([1, 127, "FERT", self.params["fert"]])

        lines.append([1, 135, "CROP", self.params["crop"]])
        lines.append([1, 135, "PLTM"])

        if "cult" in self.params:
            lines.append([1, 135, "CULT", self.params["cult"]])

        lines.append([1, 285, "LAST"])
        lines.append([1, 289, "HARV", self.params["harv"]])

        return lines
