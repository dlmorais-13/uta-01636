import os

class BuildClimateChangeFiles():
    """
    Builds the DayCent input files responsible for modeling climate change variables. The files are:

    - tminscale.dat: modifier for minimum temperature.
    - tmaxscale.dat: modifier for maximum temperature.
    - precscale.dat: modifier for precipitation.
    """

    dest_dir: str
    start_year: int
    end_year: int
    tmin_change: float
    tmax_change: float
    precipitation_change: float

    def __init__(self, dest_dir: str, start_year: int, end_year: int, tmax_change: float, tmin_change: float, precipitation_change: float):
        self.dest_dir = dest_dir
        self.start_year = start_year
        self.end_year = end_year
        self.tmax_change = tmax_change
        self.tmin_change = tmin_change
        self.precipitation_change = precipitation_change

    async def build(self):
        self.build_tminscale()
        self.build_tmaxscale()
        self.build_precscale()

    def build_tminscale(self):
        values = [self.tmin_change for _ in range(12)]
        lines = [
            [y, *values]
            for y in range(self.start_year, self.end_year + 1)
        ]
        self._write_file('tminscale.dat', lines)

    def build_tmaxscale(self):
        values = [self.tmax_change for _ in range(12)]
        lines = [
            [y, *values]
            for y in range(self.start_year, self.end_year + 1)
        ]
        self._write_file('tmaxscale.dat', lines)

    def build_precscale(self):
        values = [self.precipitation_change for _ in range(12)]
        lines = [
            [y, *values]
            for y in range(self.start_year, self.end_year + 1)
        ]
        self._write_file('precscale.dat', lines)

    def _write_file(self, filename: str, lines: list):
        file_path = os.path.join(self.dest_dir, filename)
        with open(file_path, 'w') as file:
            for line in lines:
                file.write("\t".join([f'{v}' for v in line]))
                file.write('\n')

if __name__ == '__main__':
    if os.path.exists('/tmp/tminscale.100'):
        os.unlink('/tmp/tminscale.100')
    if os.path.exists('/tmp/tmaxscale.100'):
        os.unlink('/tmp/tmaxscale.100')
    if os.path.exists('/tmp/precscale.100'):
        os.unlink('/tmp/precscale.100')

    builder = BuildClimateChangeFiles(
        dest_dir='/tmp',
        start_year=2021,
        end_year=2030,
        tmax_change=.022,
        tmin_change=.02,
        precipitation_change=.999
    )

    import asyncio
    asyncio.run(builder.build())
