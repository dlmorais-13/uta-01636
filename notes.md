# Notes

* Manual page 29: DDCentEVI versions have eliminated the "sitepar.in" file and moved these parameters to site.100.
  * Running the model without file "sitepar.in" changes the final results.
  * The variables in "sitepar.in" are not present in \<site\>.100 file, at least when searching by name.
  * Apparently this removal of file "sitepar.in" applies only to Nitrification/Denitrification data.

* Spinup
  * Equilibrium: Simulate natural conditions of the area before human intervention.
  * Base: Simulate the past cropping, grazing, and/or woodland history prior to time frame of interest.

# Ideas

## DayCent Execution Service

Host a multipurpose DayCent service to facilitate the execution (live and background) of the DayCent model. Considering that this system would be executed in a containerized K8s environment, it would require relative low resources, since the actual executions would be ran as jobs, effectively using zero resources when idle.
  
  ### Components

  * **Management Website**: Allows users to preconfigure DayCent scenarios, which contains predetermined input variables. Also allow users to manually trigger executions.
  * **Webservice**: Allows systems to trigger the execution of the DayCent model by indicating a preconfigured scenario and passing the additional necessary variables. Execution result will be provided by either email (attached or added to a box/drive) or made available as an ArcGIS layer.
  * **Job Runner**: Executes jobs that are going to effectively execute the DayCent models.