import os
from typing import TextIO

from src.utils.management_options.ManagementOption import ManagementOption

class BuildScheduleFile:
    """
    Class to build the schedule files for the equilibrium, base, and simulation
    calculations.
    """

    dest_dir: str
    start_year: int
    end_year: int
    block_number: int = 1
    management: ManagementOption

    def __init__(self, dest_dir: str, start_year: int, end_year: int, management: ManagementOption):
        """
        Constructs the builder.

        Args:
            dest_dir: The directory to write the schedule file.
            start_year: The first year of this schedule.
            end_year: The last year of this schedule.
        """

        self.dest_dir = dest_dir
        self.start_year = start_year
        self.end_year = end_year
        self.management = management

    async def build(self):
        """
        Builds the schedule and write into the destination folder.
        """

        with open(os.path.join(self.dest_dir, "site.sch"), "w") as file:
            self._write_header(file)
            file.write("Year Month Option\n")
            self._write_blocks(file)

    def _write_header(self, file: TextIO):
        """
        Writes the header of the schedule file. Each schedule contains
        only one main header.

        Args:
            file: The file to write the header into.
        """

        lines = self.management.get_schedule_header()

        file.writelines(
            [f"{l[0]:<13} {l[1]}\n" if len(l) == 2 else f"{l[0]}\n" for l in lines]
        )
        file.write("\n")

    def _write_blocks(self, file: TextIO):
        """
        Writes a block into the schedule file. A schedule may have multiple blocks.
        Usually, the equilibrium and simulation schedules will have one block, and 
        the base layer schedule might have more.

        Args:
            file: The file to write the block into.
        """

        block_number = self.management.get_next_block_number()
        while block_number <= self.management.get_num_blocks():
            block_header = self.management.get_block_header()
            file.writelines(
                [f"{l[0]:<13} {l[1]}\n" if len(l) == 2 else f"{l[0]}" for l in block_header]
            )
            file.write("\n")

            block_content = self.management.get_block_content()
            block_content.append([-999, -999, 'X'])
            file.writelines(
                [
                    f"{' '.join(line)}\n"
                    for line in [[str(value) for value in line] for line in block_content]
                ]
            )
            file.write("\n")
            
            block_number = self.management.get_next_block_number()       
