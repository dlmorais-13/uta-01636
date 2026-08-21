from src.utils.management_options.ManagementOption import ManagementOption


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

    def get_schedule_content(self):
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
