import os
from typing import TextIO


class BuildScheduleFile:

    dest_dir: str
    start_year: int
    end_year: int
    block_number: int = 1

    def __init__(self, dest_dir: str, start_year: int, end_year: int):
        self.dest_dir = dest_dir
        self.start_year = start_year
        self.end_year = end_year

    async def build(self):
        with open(os.path.join(self.dest_dir, "site.sch"), "w") as file:
            self.write_header(file)
            file.write("Year Month Option\n")
            self.write_block(file)

    def write_header(self, file: TextIO):
        lines: list[tuple] = []

        lines.append([self.start_year, "Starting year"])
        lines.append([self.end_year, "Last year"])
        lines.append(["site.100", "Site file name"])

        # Labeling type
        # TODO Check what value to use.
        lines.append([0, "Labeling type"])
        lines.append([-1, "Labeling year"])

        # Microcosm (Deprecated)
        # TODO Check if necessary.
        lines.append([-1, "Microcosm"])

        # CO² Systems
        # TODO Check what value to use
        lines.append([-1, "CO2 Systems"])

        # Soil pH shift option
        # TODO Check what value to use
        lines.append([-1, "pH shift"])

        # Soil warming
        # TODO Check what value to use
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
        lines.append([5, "# Climate scalar option"])
        lines.append([f"{max(self.start_year, 2026)}"])

        # Initial system
        # TODO This will vary for equilibrium, base and simulation runs.
        # 1: for croplands or grasslands
        # 2: for forests
        # 3: for savanna
        lines.append([1, "Initial system"])

        # Initial crop
        # TODO Get the initial crop from the current crop in the parcel.
        lines.append(["ALF", "Initial crop"])

        # Initial tree
        # TODO Might be necessary to input value for equilibrium calculations.
        lines.append(["", "Initial tree"])

        file.writelines(
            [f"{l[0]:<13} {l[1]}\n" if len(l) == 2 else f"{l[0]}\n" for l in lines]
        )
        file.write("\n")

    def write_block(self, file: TextIO):
        self.write_block_header(file)

        # TODO Implement this part. Right now is only setting the crop as Alfalfa
        lines: list[list[int | str]] = []
        lines.append([1, 127, "FERT", "(16.5N,1.0F)"])
        lines.append([1, 135, "CROP", "ALF"])
        lines.append([1, 135, "PLTM"])
        lines.append([1, 135, "CULT", "CTIL"])
        lines.append([1, 285, "LAST"])
        lines.append([1, 289, "HARV", "G"])
        lines.append([-999, -999, "X"])

        file.writelines(
            [
                f"{' '.join(line)}\n"
                for line in [[str(value) for value in line] for line in lines]
            ]
        )
        file.write("\n")

    def write_block_header(self, file: TextIO):
        lines: list[tuple] = []
        lines.append([++self.block_number, "Block #"])
        lines.append([self.end_year, "Last year"])
        lines.append([1, "Repeats # years"])

        # TODO These should change for equilibrium and base.
        lines.append([self.start_year, "Output starting year"])
        lines.append([12, "Output month"])
        lines.append(["1.0", "Output interval"])

        lines.append(["F", "Weather choice"])
        lines.append(["site.wth"])

        file.writelines(
            [f"{l[0]:<13} {l[1]}\n" if len(l) == 2 else f"{l[0]}" for l in lines]
        )
        file.write("\n")
