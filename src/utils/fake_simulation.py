from arcgis.features import Feature
import random

from src.apis.agol_api import AgolAPI, AgolAPI_Injector
from src.models.parcel_repository import ParcelRepository
from src.models.simulation_repository import SimulationRepository, SimulationColumns
from src.jobs.process_created_simulation import ProcessCreatedSimulation
from src.settings import settings

print("Creating a fake simulation")

api: AgolAPI = AgolAPI_Injector()
parcel_repository: ParcelRepository = ParcelRepository()
simulation_repository: SimulationRepository = SimulationRepository()

filters = [{"type": "text", "name": "County", "value": "Cache"}]
parameters = []
# parameters = [
#     {
#         "type": "target",
#         "name": "Crop Target",
#         "column": "crop",
#         "value": "Flaxseed",
#         "target": 0.4,
#     },
#     {
#         "type": "target",
#         "name": "Crop Target",
#         "column": "crop",
#         "value": "Durum Wheat",
#         "target": 0.4,
#     },
# ]

simulation = simulation_repository.create_simulation(
    filters=filters,
    parameters=parameters,
)

process_created_simulation = ProcessCreatedSimulation()
where = process_created_simulation._build_where_clause_from_filters(filters)

parcels = parcel_repository.get_parcels(where, return_geometry=True)

features = []
for p in parcels:
    for year in range(2026, 2026 + 50):
        features.append(
            Feature(
                geometry=p.geometry,
                attributes=dict(
                    parcel_key=p.attributes["parcel_key"],
                    simulation_id=simulation[SimulationColumns.OBJECTID.value],
                    simulation_date=f"{year}-01-01",
                    carbon_stock=random.uniform(100, 1000),
                ),
            )
        )
api.batch_edit(settings.agol_simulations_layer_id, features_to_add=features)
