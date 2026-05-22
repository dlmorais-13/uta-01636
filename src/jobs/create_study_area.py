from src.jobs.job import Job
from src.apis.agol_api import AgolAPI
from arcgis.features import FeatureSet
from src.settings import settings
import logging

LOGGER = logging.getLogger(__name__)

class CreateStudyArea(Job):
    
    async def logic(self, params: dict):
        api = AgolAPI()

        usa_census_counties_layer_ref = api.get_layer_ref(settings.usa_census_counties_layer_id)
        counties = ', '.join(map(lambda c: f"'{c} County'", api.get_config('STUDY_AREA_COUNTIES').split(',')))
        filter = f"STATE_NAME = 'Utah' AND NAME IN ({counties})"
        study_area_featureset: FeatureSet = usa_census_counties_layer_ref.query(
            where=filter, return_all_records=True, return_geometry=True)
        LOGGER.info(f'Study area size: {len(study_area_featureset)} counties.')

        study_area_layer_ref = api.get_layer_ref(settings.agol_study_area_layer_id)
        study_area_layer_ref.delete_features(where="1=1")
        study_area_layer_ref.edit_features(adds=study_area_featureset)
