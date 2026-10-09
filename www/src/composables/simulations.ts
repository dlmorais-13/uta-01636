import type { SimulationFilters, SimulationParameters } from '@/types';
import Graphic from '@arcgis/core/Graphic';
import FeatureLayer from '@arcgis/core/layers/FeatureLayer';
import { ref, type Ref } from 'vue';
import { useAuth } from './auth';
import { useJobManager } from './job-manager';

const _serviceId = import.meta.env.VITE_AGOL_SIMULATIONS_LAYER_VIEW_ID;
const simTableRef = new FeatureLayer({
  portalItem: { id: _serviceId },
  layerId: 1
});

export function useSimulations() {

  const serviceId: Ref<string> = ref(_serviceId);
  const { user, waitForAuth } = useAuth();
  const jobManager = useJobManager();

  async function getSimulations() {
    const simulations = (await simTableRef.queryFeatures({
      where: '1=1',
      outFields: ['*']
    })).features;
    simulations.forEach(s => {
      s.attributes.filters = JSON.parse(s.attributes.filters || '[]');
      s.attributes.params = JSON.parse(s.attributes.params || '[]');
    })
    return simulations;
  }

  async function createSimulation(filters: Array<SimulationFilters>, parameters: Array<SimulationParameters>): Promise<number | false> {
    await waitForAuth();
    const resp = await simTableRef.applyEdits({
      addFeatures: [new Graphic({
        attributes: {
          'filters': JSON.stringify(filters),
          'params': JSON.stringify(parameters),
          'owner': user.value?.username,
          'status': 'created',
          'created_date': new Date().toISOString().split('.')[0] + 'Z',
        }
      })]
    });

    if (resp.addFeatureResults.length === 1 && !resp.addFeatureResults[0]?.error) {
      const simulationId = resp.addFeatureResults[0]?.objectId!;
      await jobManager.addJob({
        name: `jobs.process_created_simulation.ProcessCreatedSimulation:${simulationId}`,
        params: { 'simulation_id': simulationId }
      });

      return simulationId;
    }

    return false;
  }

  return { serviceId, getSimulations, createSimulation }
}