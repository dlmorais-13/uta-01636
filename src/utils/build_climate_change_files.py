import os
import statistics
from functools import reduce
from collections import defaultdict
from scipy.stats import theilslopes

TotalizedData = dict[str, dict[str, dict[str, float | int]]]

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
    wth_file: str

    def __init__(self, dest_dir: str, start_year: int, end_year: int, wth_file: str):
        self.dest_dir = dest_dir
        self.start_year = max(start_year, 2026)
        self.end_year = end_year
        self.wth_file = wth_file

    async def build(self):
        wth_data = self.read_wth_file()
        totalized_values_per_month = self.calculate_totalized_values_per_month(wth_data)
        self.calculate_theilslopes(totalized_values_per_month)
        self.calculate_perc_ppt(totalized_values_per_month)

        self._write_file(
            'tmaxscale.dat',
            [float(totalized_values_per_month[month]['theilslope_tmax'].slope) for month in totalized_values_per_month]
        )

        self._write_file(
            'tminscale.dat',
            [float(totalized_values_per_month[month]['theilslope_tmin'].slope) for month in totalized_values_per_month]
        )

        # "perc_ppt" represents the percentual (0..1) difference of precipitation in each month.
        self._write_file(
            'precscale.dat',
            [1 + float(totalized_values_per_month[month]['perc_ppt']) for month in totalized_values_per_month]
        )

    def read_wth_file(self):
        wth_data: list[list[float | int]] = []
        with open(self.wth_file, 'r') as file:
            for line in file:
                values = [
                    int(s.split('.')[0]) if float(s).is_integer() else float(s)
                    for s in line.split()
                ]
                wth_data.append(values)
        return wth_data

    def calculate_totalized_values_per_month(self, wth_data: list[list[float | int]]) -> TotalizedData:
        totalized_per_month_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        month_count = 0
        current_month = 0

        for line in wth_data:
            month, year = line[1:3]

            # First iteration, initialize the current_month control variable.
            if current_month == 0:
                current_month = f'{month}-{year}'
                
            # If changed month, compute previous month mean values.
            elif current_month != f'{month}-{year}':
                cMonth, cYear = [int(s) for s in current_month.split('-')]
                
                totalized_per_month_data[cMonth][cYear]['tmax'] = totalized_per_month_data[cMonth][cYear]['tmax'] / month_count
                totalized_per_month_data[cMonth][cYear]['tmin'] = totalized_per_month_data[cMonth][cYear]['tmin'] / month_count
                totalized_per_month_data[cMonth][cYear]['days'] = month_count

                month_count = 0
                current_month = f'{month}-{year}'
            
            month_count += 1
            totalized_per_month_data[month][year]['tmax'] += line[4]
            totalized_per_month_data[month][year]['tmin'] += line[5]
            totalized_per_month_data[month][year]['ppt'] += line[6]

        # Calculate the mean temp for the last month in the iteration
        totalized_per_month_data[month][year]['tmax'] = totalized_per_month_data[month][year]['tmax'] / month_count
        totalized_per_month_data[month][year]['tmin'] = totalized_per_month_data[month][year]['tmin'] / month_count
        totalized_per_month_data[month][year]['days'] = month_count

        return totalized_per_month_data

    def calculate_theilslopes(self, wth_data: TotalizedData):
        for month in wth_data:
            for var in ['tmax', 'tmin', 'ppt']:
                wth_data[month][f'theilslope_{var}'] = theilslopes(
                    y=[wth_data[month][year][var] for year in wth_data[month] if isinstance(year, int)],
                    x=[year for year in wth_data[month] if isinstance(year, int)]
                )

    def calculate_perc_ppt(self, wth_data: TotalizedData):
        for month in wth_data:
            wth_data[month]['perc_ppt'] = (
                float(wth_data[month]['theilslope_ppt'].slope)
                / statistics.mean([wth_data[month][year]['ppt'] for year in wth_data[month] if isinstance(year, int)])
            )
    
    def _write_file(self, filename: str, values: list[float]):
        lines = [
            [y, *[f'{v:.6f}' for v in values]]
            for y in range(self.start_year, self.end_year + 1)
        ]

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
