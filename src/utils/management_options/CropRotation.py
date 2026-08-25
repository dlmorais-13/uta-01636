from src.utils.management_options.ManagementOption import ManagementOption, ExecType


class CropRotation(ManagementOption):
    """
    Management option for crop rotation.
    Will create a schedule where the crops from the
    arguments are cycled through each year.

    Params:
        fert: Type of fertilization events to use. If not defined,
            no fertilization events are added to the schedule.
        crop: Type of the crops for the rotation.
        cult: Type of the cultivation/tillage event. If not defined,
            no cultivation/tillage event is added to the schedule.
        harv: Type of the harvesting event.

    TODO Add parameters for the days of the events.
    """

    def get_type(self) -> ExecType:
        # TODO This can be both simulation or base
        return "base"

    def get_block_header(self):
        lines: list[list[int | str]] = []
        lines.append([self.block_number, "Block #"])
        lines.append([self.end_year, "Last year"])
        lines.append([len(self.params["crop"]), "Repeats # years"])

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

        crops: list[str] = self.params["crop"]

        ferts = self._get_param_as_list("fert")
        cults = self._get_param_as_list("cult")
        harvs = self._get_param_as_list("harv")

        for index, crop in enumerate(crops):
            year_index = index + 1

            if ferts is not None:
                lines.append([year_index, 127, "FERT", ferts[index]])

            lines.append([year_index, 135, "CROP", crop])
            lines.append([year_index, 135, "PLTM"])

            if "cult" in self.params:
                lines.append([year_index, 135, "CULT", cults[index]])

            lines.append([year_index, 285, "LAST"])
            lines.append([year_index, 289, "HARV", harvs[index]])

        return lines

    def _get_param_as_list(self, name) -> list[str] | None:
        if name in self.params:
            if isinstance(self.params[name], list):
                return self.params[name]
            else:
                return [self.params[name]] * len(self.params["crop"])
        return None
