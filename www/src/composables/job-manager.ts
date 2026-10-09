import type { Job } from "@/types";
import Graphic from "@arcgis/core/Graphic";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer"

export function useJobManager() {
  const layer = new FeatureLayer({ portalItem: { id: import.meta.env.VITE_AGOL_QUEUE_FEATURE_ID } });

  async function addJob(job: Partial<Job>) : Promise<Number> {
    const features = [
      new Graphic({
        attributes: {
          'JOB_NAME': job.name,
          'JOB_PARAMS': JSON.stringify(job.params),
          'JOB_CREATE_DATE': new Date().toISOString().split('.')[0] + 'Z',
          'JOB_STATUS': 'CREATED',
        }
      })
    ];

    const resp = await layer.applyEdits({ addFeatures: features });

    if (resp.addFeatureResults.length === 1 && !resp.addFeatureResults[0]?.error) {
      return resp.addFeatureResults[0]?.objectId!;
    } else {
      console.error('Error while adding job.', resp.addFeatureResults);
      throw new Error('Error while adding job to queue.', { cause: resp.addFeatureResults });
    }
  }

  return { addJob }
}