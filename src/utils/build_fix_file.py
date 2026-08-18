import os
from functools import reduce


class BuildFixFile:
    """
    Class to build the fix.100 file for Daycent execution.
    """

    dest_dir: str
    soil_layer_data: list[list[float]]

    def __init__(self, dest_dir: str, soil_layer_data: list[list[float]]):
        """
        Constructs the builder instance.

        Args:
            dest_dir: The folder to write the file.
            soil_layer_data: The data used to write the file "soils.in".
        """
        self.dest_dir = dest_dir
        self.soil_layer_data = soil_layer_data

    async def build(self):
        """
        Builds the file fix.100 in the destination folder. For this builder,
        the file fix.100 already exists and it is modified as necessary
        according to the available variables.
        """

        depth_list = self._build_depth_list()
        lines = self._read_current_file()

        for depthIdx in range(0, len(depth_list)):
            for line in lines:
                if line[1] == f"'ADEP({depthIdx + 1})'":
                    line[0] = f"{depth_list[depthIdx]:.3f}"
                    break

        # TODO Check variables 'AWTL(X)'

        lines = [f"{l[0]:<14}{l[1]}\n" for l in lines]
        with open(os.path.join(self.dest_dir, "fix.100"), "w") as file:
            file.writelines(lines)

    def _build_depth_list(self) -> list[float]:
        """
        Build the depth list as a grouping of at least thickness 15 using
        the data from soils layer.

        Returns:
            A list of floats with the depth of each layer, in order.
        """

        next_thickness = 0
        depth_list = []

        for layer in self.soil_layer_data:
            next_thickness += layer[0]

            if next_thickness >= 15:
                depth_list.append(next_thickness)
                next_thickness = 0

        # If control variable > 0, add as the last layer.
        if next_thickness > 0:
            depth_list.append(next_thickness)

        # If more than 10 layers, it is necessary to combine until length <= 10.
        while len(depth_list) > 10:
            smallest_pair = -1
            smallest_pair_depth = 9999

            # Find the smallest pair of layers that are next to each other.
            for idx in range(0, len(depth_list) - 2):
                if smallest_pair_depth > depth_list[idx] + depth_list[idx + 1]:
                    smallest_pair_depth = depth_list[idx] + depth_list[idx + 1]
                    smallest_pair = idx

            # Combine the smallest pair.
            depth_list[smallest_pair] = smallest_pair_depth
            del depth_list[smallest_pair + 1]

        return depth_list

    def _read_current_file(self) -> list[list[str]]:
        """
        Reads the content of the current file into a list, removing
        any commented out line and building tuples out of the available
        content.

        Returns:
            The content of the current file as a list. Each list
            element is a tuple with the variable value and name, respectively.
        """

        lines = []
        with open(os.path.join(self.dest_dir, "fix.100"), "r") as file:
            for l in file:
                if not l.startswith("#"):
                    lines.append(
                        [
                            s.replace("\n", "").replace("\t", "")
                            for s in l.split(" ")
                            if s and s != "\n"
                        ]
                    )
        return lines
