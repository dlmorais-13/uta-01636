import os
import numpy as np
from arcgis.features import Feature
from arcgis.geometry import Geometry
from pandas import DataFrame

from src.apis.agol_api import AgolAPI, AgolAPI_Injector


class BuildSiteFile:
    """
    Class to build the site.100 file for Daycent execution.
    """

    agol_api: AgolAPI
    dest_dir: str
    parcel: Feature
    nlayers: int
    components: DataFrame

    def __init__(
        self,
        dest_dir: str,
        parcel: Feature,
        nlayers: int,
        elevation: int,
        components: DataFrame,
    ):
        self.agol_api = AgolAPI_Injector()
        self.dest_dir = dest_dir
        self.nlayers = nlayers
        self.parcel = parcel
        self.elevation = elevation
        self.components = components

    async def build(self):
        file_lines = ["X     Archived"]
        file_lines += self.get_climate_lines()
        file_lines += self.get_site_control_lines()
        file_lines += self.get_external_nutrients_lines()
        file_lines += self.get_organic_matter_initial_lines()
        file_lines += self.get_forest_organic_matter_initial_lines()
        file_lines += self.get_mineral_initial_values()
        file_lines += self.get_water_initial_values()

        file_path = os.path.join(self.dest_dir, "site.100")
        with open(file_path, "w") as file:
            file.writelines([f"{l}\n" for l in file_lines])

    def get_climate_lines(self):
        """
        Return the lines for the climate parameters.
        TODO CHECK:: A single line with climate statistics is enough for Daycent to compute this section automatically.
        """

        return ["*** Climate statistics site.wth"]

    def get_site_control_lines(self):
        lines = []
        lines.append("*** Site and control parameters")

        # IVAUTO | 0, 1, 2 or 3
        # Use Burke's equations to initialize soil C pools.
        # 0 = the user has supplied the initial values
        # 1 = initialize using the grass soil parameters
        # 2 = initialize using the crop soil parameters
        # 3 = initialize using the forest soil parameters
        ivauto = 0
        lines.append(f"{ivauto:<18} IVAUTO")

        # NELEM | 1, 2 or 3
        # Number of elements (besides C) to be simulated: 1 = simulate N only; 2 = simulate N, P; 3 = simulate N, P, S
        nelem = 1
        lines.append(f"{nelem:<18} NELEM")

        # SITLAT & SITLNG | decimal degrees
        # Latitude and Longitude
        # Obs.: Longitude is inverted (*-1)
        parcel_centroid = Geometry(self.parcel.geometry).centroid
        lines.append(f"{parcel_centroid[1]:<18.3f} SITLAT")
        lines.append(f"{(parcel_centroid[0] * -1):<18.3f} SITLNG")

        # ELEV | meters
        # Elevation
        lines.append(f"{self.elevation:<18} ELEV")

        # SITSLP | degrees
        # Site slope
        # Here calculated as the weighted average slope of all components
        self.components["slope_deg"] = np.degrees(
            np.arctan(self.components["slope_r"] / 100)
        )
        slope_deg = (
            self.components["slope_deg"] * self.components["comppct_r"]
        ).sum() / self.components["comppct_r"].sum()
        lines.append(f"{int(slope_deg):<18.0f} SITSLP")

        # ASPECT | degrees
        # Site aspect
        # TODO Check what value to use - Might be possible to use 'aspectrep' from SSURGO component.
        lines.append(f"{0:<18} ASPECT")

        # EHORIZ | degrees
        # Site east horizon
        # TODO Check what value to use
        lines.append(f"{0:<18} EHORIZ")

        # WHORIZ | degrees
        # Site west horizon
        # TODO Check what value to use
        lines.append(f"{0:<18} WHORIZ")

        # NLAYER | count | 1 - 9
        # Number of soil layers in water model (maximum of 9);used only to calculated the amount of water available forsurvival of the plant.
        nlayer = min(9, self.nlayers)
        lines.append(f"{nlayer:<18} NLAYER")

        # NLAYPG | count | 1 - NLAYER
        # Number of soil layers in the top level of the water model; determines avh2o(1), used for plant growth and rootdeath.
        # Overwritten by values ofclaypg or tlaypg in thecrop.100 or tree.100 files.
        # Max = NLAYER
        # TODO Check what value to use
        lines.append(f"{min(nlayer, 0):<18} NLAYPG")

        # DRAIN | fraction | 0.0 – 1.0
        # The fraction of excess water lost by drainage; indicates whether a soil is sensitive for anaerobiosis (drain=0) or not (drain=1).
        # Anaerobic conditions (high soil water content) cause decomposition to decrease.
        # (DRAIN=1 for well drained sandy soils and DRAIN=0 for a poorly drained clay soil)
        # TODO Check what value to use
        lines.append(f"{.5:<18.2f} DRAIN")

        # BASEF | fraction | 0.0 – 1.0
        # Fraction of the soil water content of layer nlayer + 1 whichis lost via base flow.
        # TODO Check what value to use
        lines.append(f"{.5:<18.2f} BASEF")

        # STORMF, PRECRO, FRACRO, SWFLAG, PH - Not used by Daycent
        lines.append(f"{0:<18.5f} STORMF")
        lines.append(f"{0:<18.5f} PRECRO")
        lines.append(f"{0:<18.5f} FRACRO")
        lines.append(f"{0:<18} SWFLAG")

        # PSLSRB | ?
        # Slope term which controls the fraction of mineral P that islabile
        # TODO Check what value to use
        lines.append(f"{1:<18.1f} PSLSRB")

        # SORPMX | ?
        # Maximum P sorption potential for a soil
        # TODO Check what value to use
        lines.append(f"{5:<18.1f} SORPMX")

        return lines

    def get_external_nutrients_lines(self):
        lines = []
        lines.append("*** External nutrient input parameters")

        # EPNFA(1) | g N m⁻² yr⁻¹
        # Intercept value for determining the effect of annual precipitation on atmospheric N fixation (wet and drydeposition)
        # TODO Check what value to use
        lines.append(f"{0:<18.2f} EPNFA(1)\t0.21 9/1/11 billp")

        # EPNFA(2) | g N m⁻² yr⁻¹ | 0.0 – 1.0
        # Slope values for determining the effect of annual precipitation on atmospheric N fixation (wet and drydeposition)
        # TODO Check what value to use
        lines.append(f"{0:<18.2f} EPNFA(2)\t0.0028 9/1/11 billp")

        # EPNFS(1) | g N m⁻² yr⁻¹
        # Intercept value for determining the effect of annual precipitation on non-symbiotic soil N fixation; not used iffix.100 value nsnfix = 1
        # TODO Check what value to use
        lines.append(f"{30:<18.4f} EPNFS(1)")

        # EPNFS(2) | g N m⁻² yr⁻¹ | 0.0 – 1.0
        # Slope value for determining the effect of annual precipitation on non-symbiotic soil N fixation; not used iffix.100 value nsnfix = 1
        # TODO Check what value to use
        lines.append(f"{.01:<18.4f} EPNFS(2)")

        # SATMOS(1) | g S m⁻² yr⁻¹ cm⁻¹
        # Intercept value for atmospheric S inputs as a linearfunction of annual precipitation
        # TODO Check what value to use
        lines.append(f"{0:<18.1f} SATMOS(1)")

        # SATMOS(2) | g S m⁻² yr⁻¹ cm⁻¹ | 0.0 – 1.0
        # Slope value for atmospheric S inputs as a linear function ofannual precipitation
        # TODO Check what value to use
        lines.append(f"{0:<18.1f} SATMOS(2)")

        # SIRRI | mg S L⁻¹ | 0.0 – 1000.0
        # S concentration in irrigation water
        # TODO Check what value to use
        lines.append(f"{0:<18.1f} SIRRI")

        return lines

    def get_organic_matter_initial_lines(self):
        """
        The values in this section are disconsidered when running a simulation
        that extends a spinup simulation. Since we are setting up equilibrium and
        base simulations before the future simulation, we can just set all values to
        any number > 0.
        """

        lines = []
        lines.append("*** Organic matter initial values")
        variables = [
            "SOM1CI(1,1)",
            "SOM1CI(1,2)",
            "SOM1CI(2,1)",
            "SOM1CI(2,2)",
            "SOM2CI(1,1)",
            "SOM2CI(1,2)",
            "SOM2CI(2,1)",
            "SOM2CI(2,2)",
            "SOM3CI(1)",
            "SOM3CI(2)",
            "RCES1(1,1)",
            "RCES1(1,2)",
            "RCES1(1,3)",
            "RCES1(2,1)",
            "RCES1(2,2)",
            "RCES1(2,3)",
            "RCES2(1,1)",
            "RCES2(1,2)",
            "RCES2(1,3)",
            "RCES2(2,1)",
            "RCES2(2,2)",
            "RCES2(2,3)",
            "RCES3(1)",
            "RCES3(2)",
            "RCES3(3)",
            "CLITTR(1,1)",
            "CLITTR(1,2)",
            "CLITTR(2,1)",
            "CLITTR(2,2)",
            "RCELIT(1,1)",
            "RCELIT(1,2)",
            "RCELIT(1,3)",
            "RCELIT(2,1)",
            "RCELIT(2,2)",
            "RCELIT(2,3)",
            "AGLCIS(1)",
            "AGLCIS(2)",
            "AGLIVE(1)",
            "AGLIVE(2)",
            "AGLIVE(3)",
            "BGLCIS(1)",
            "BGLCIS(2)",
            "BGLIVE(1)",
            "BGLIVE(2)",
            "BGLIVE(3)",
            "STDCIS(1)",
            "STDCIS(2)",
            "STDEDE(1)",
            "STDEDE(2)",
            "STDEDE(3)",
        ]
        lines += [f"{0.1:<18.1f} {v}" for v in variables]
        return lines

    def get_forest_organic_matter_initial_lines(self):
        """
        The values in this section are disconsidered when running a simulation
        that extends a spinup simulation. Since we are setting up equilibrium and
        base simulations before the future simulation, we can just set all values to
        any number > 0.
        """

        lines = []
        lines.append("*** Forest organic matter initial parameters")
        variables = [
            "RLVCIS(1)",
            "RLVCIS(2)",
            "RLEAVE(1)",
            "RLEAVE(2)",
            "RLEAVE(3)",
            "FBRCIS(1)",
            "FBRCIS(2)",
            "FBRCHE(1)",
            "FBRCHE(2)",
            "FBRCHE(3)",
            "RLWCIS(1)",
            "RLWCIS(2)",
            "RLWODE(1)",
            "RLWODE(2)",
            "RLWODE(3)",
            "FRTCIS(1)",
            "FRTCIS(2)",
            "FROOTE(1)",
            "FROOTE(2)",
            "FROOTE(3)",
            "CRTCIS(1)",
            "CRTCIS(2)",
            "CROOTE(1)",
            "CROOTE(2)",
            "CROOTE(3)",
            "WD1CIS(1)",
            "WD1CIS(2)",
            "WD2CIS(1)",
            "WD2CIS(2)",
            "WD3CIS(1)",
            "WD3CIS(2)",
        ]
        lines += [f"{0.1:<18.1f} {v}" for v in variables]
        return lines

    def get_mineral_initial_values(self):
        """
        The values in this section are disconsidered when running a simulation
        that extends a spinup simulation. Since we are setting up equilibrium and
        base simulations before the future simulation, we can just set all values to
        any number > 0.
        """

        lines = []
        lines.append("*** Mineral initial parameters")
        variables = [
            "MINERL(1,1)",
            "MINERL(2,1)",
            "MINERL(3,1)",
            "MINERL(4,1)",
            "MINERL(5,1)",
            "MINERL(6,1)",
            "MINERL(7,1)",
            "MINERL(8,1)",
            "MINERL(9,1)",
            "MINERL(10,1)",
            "MINERL(1,2)",
            "MINERL(2,2)",
            "MINERL(3,2)",
            "MINERL(4,2)",
            "MINERL(5,2)",
            "MINERL(6,2)",
            "MINERL(7,2)",
            "MINERL(8,2)",
            "MINERL(9,2)",
            "MINERL(10,2)",
            "MINERL(1,3)",
            "MINERL(2,3)",
            "MINERL(3,3)",
            "MINERL(4,3)",
            "MINERL(5,3)",
            "MINERL(6,3)",
            "MINERL(7,3)",
            "MINERL(8,3)",
            "MINERL(9,3)",
            "MINERL(10,3)",
            "PARENT(1)",
            "PARENT(2)",
            "PARENT(3)",
            "SECNDY(1)",
            "SECNDY(2)",
            "SECNDY(3)",
            "OCCLUD",
        ]
        lines += [f"{0.1:<18.1f} {v}" for v in variables]
        return lines

    def get_water_initial_values(self):
        """
        The values in this section are disconsidered when running a simulation
        that extends a spinup simulation. Since we are setting up equilibrium and
        base simulations before the future simulation, we can just set all values to
        any number > 0.
        """

        lines = []
        lines.append("*** Water initial parameters")

        variables = [
            "RWCF(1)",
            "RWCF(2)",
            "RWCF(3)",
            "RWCF(4)",
            "RWCF(5)",
            "RWCF(6)",
            "RWCF(7)",
            "RWCF(8)",
            "RWCF(9)",
            "RWCF(10)",
            "SNLQ",
            "SNOW",
        ]
        lines += [f"{0.1:<18.1f} {v}" for v in variables]

        # SNWINS | index | 0 or 1
        # Snow effect on soil surface temp
        # 0 = not insulating, 1 = insulating
        # TODO Check what value to use - Not necessary if using file sitepar.in (variable SnowFlag)
        lines.append(f"{0:<18} SNWINS")

        return lines


if __name__ == "__main__":
    if os.path.exists("/tmp/site.100"):
        os.unlink("/tmp/site.100")

    builder = BuildSiteFile(dest_dir="/tmp", parcel_id=211091, nlayers=10)

    import asyncio

    asyncio.run(builder.build())
