from abc import ABC, abstractmethod
from typing import Literal

ExecType = Literal["equilibrium", "base", "simulation"]


class ManagementOption(ABC):
    """
    Abstract class to model different management options
    for the simulations.
    """

    name: str
    start_year: int
    end_year: int
    params: dict
    block_number: int = 0

    def __init__(self, start_year: int, end_year: int, params: dict = {}):
        self.name = self.__class__.__name__
        self.start_year = start_year
        self.end_year = end_year
        self.params = params

    def get_schedule_header(self) -> list[list[int | str]]:
        """
        Gets the schedule header for the management option.
        """

        lines: list[tuple] = []

        lines.append([self.start_year, "Starting year"])
        lines.append([self.end_year, "Last year"])
        lines.append(["site.100", "Site file name"])

        # Labeling type
        # TODO Check what value to use.
        lines.append([0, "Labeling type"])
        lines.append([-1, "Labeling year"])

        # Microcosm (Deprecated)
        lines.append([-1, "Microcosm"])

        # CO² Systems
        # TODO Check what value to use
        lines.append([-1, "CO2 Systems"])

        # Soil pH shift option
        # TODO Check what value to use - Mostly likely not used.
        lines.append([-1, "pH shift"])

        # Soil warming
        # Not used in the simulations.
        lines.append([-1, "Soil warming"])

        # Nitrogen input scalar option
        # TODO Check what value to use
        lines.append([0, "N input scalar option"])

        # Organic Matter Addition scalar option
        # TODO Check what value to use
        lines.append([0, "OMAD scalar option"])

        # Climate scalar option
        # 0: do not use any climate scalars
        # 1: use climate scalars in tminscale.dat to adjust minimum air temperature only
        # 2: use climate scalars in tmaxscale.dat to adjust maximum air temperature only
        # 3: use climate scalars in tminscale.dat to adjust minimum air temperature and in tmaxscale.dat to adjust maximum air temperature
        # 4: use climate scalars in precscale.dat to adjust precipitation only
        # 5: use climate scalars in tminscale.dat to adjust minimum air temperature, in tmaxscale.dat to adjust maximum air temperature, and in precscale.dat to adjust precipitation
        if self.get_type() == "simulation":
            lines.append([5, "# Climate scalar option"])
            # TODO Maybe this date should be variable.
            lines.append([f"{max(self.start_year, 2026)}"])
        else:
            lines.append([0, "# Climate scalar option"])

        # Initial system
        # TODO This will vary for equilibrium, base and simulation runs.
        # 1: for croplands or grasslands
        # 2: for forests
        # 3: for savanna
        management_initial_system = self.get_initial_system()
        if management_initial_system is not None:
            for l in management_initial_system:
                lines.append(l)
        else:
            lines.append([1, "Initial system"])
            lines.append(["GI3", "Initial crop"])
            lines.append(["", "Initial tree"])

        return lines

    def get_next_block_number(self):
        self.block_number += 1
        return self.block_number

    @abstractmethod
    def get_type(self) -> ExecType:
        raise RuntimeError("Method not implemented by subclass.")

    def get_num_blocks(self) -> int:
        """
        Returns the number of blocks mapped in this management option.
        By default returns 1.
        """

        return 1

    @abstractmethod
    def get_block_header(self) -> list[list[int | str]]:
        """
        Gets the header for the current block in this management option.
        """

        pass

    @abstractmethod
    def get_block_content(self) -> list[list[int | str]]:
        """
        Gets the content for the current block for the management option.
        """

        pass

    def get_initial_system(self) -> list[list[int | str]] | None:
        """
        Gets the value for "initial system", "initial crop", and "initial tree"
        for the management option.
        """

        return None
