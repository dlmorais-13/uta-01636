from src.utils.management_options.ManagementOption import ManagementOption


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

    def get_schedule_content(self):
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
