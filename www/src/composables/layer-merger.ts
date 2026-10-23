import type Graphic from "@arcgis/core/Graphic";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer";
import type { QueryProperties } from "@arcgis/core/rest/support/Query";
import { PromisePool } from "@supercharge/promise-pool";

export function useLayerMerger() {

  async function merge(layer1: FeatureLayer, layer2: FeatureLayer) {
    const [features1, features2] = await Promise.all([
      getAllAtLayer(layer1),
      getAllAtLayer(layer2)
    ]);

    const mergedFeatures = features1.map(f => {
      const clone = f.clone();
      const featureOnLayer2 = features2.find(f2 =>
        clone.attributes.tract === f2.attributes.tract
        && clone.attributes.simulation_date === f2.attributes.simulation_date
      );

      if (featureOnLayer2) {
        clone.setAttribute('carbon_stock2', featureOnLayer2.attributes.carbon_stock);
        clone.setAttribute('difference', clone.attributes.carbon_stock - featureOnLayer2.attributes.carbon_stock);
      } else {
        console.log(`Feature not found at ${layer2.id}: Tract ${clone.attributes.tract}, Date ${clone.attributes.simulation_date}.`);
      }

      return clone;
    });

    return new FeatureLayer({
      title: 'Comparison Layer',
      source: mergedFeatures,
      fields: [
        ...layer1.fields,
        { name: 'carbon_stock2', alias: 'carbon_stock2', type: 'double' },
        { name: 'difference', alias: 'difference', type: 'double' }
      ],
      outFields: ["*"],
      objectIdField: 'OBJECTID',
      geometryType: layer1.geometryType,
      spatialReference: layer1.spatialReference
    });
  }

  async function getAllAtLayer(layer: FeatureLayer): Promise<Array<Graphic>> {
    const count = await layer.queryFeatureCount({ where: layer.definitionExpression });
    console.debug(`Layer ${layer.id} has ${count} features with filter "${layer.definitionExpression}".`);

    const query: QueryProperties = {
      where: layer.definitionExpression,
      outFields: ["*"],
      returnGeometry: true,
      start: 0,
      num: 1000
    };

    const features: Array<Graphic> = [];
    const featPerQuery = 1000;
    const splits = Math.ceil(count / featPerQuery);
    await PromisePool
      .for(Array.from({ length: splits }, (_, i) => i))
      .withConcurrency(10)
      .process(async i => {
        const resp = await layer.queryFeatures({
          ...query,
          start: i * featPerQuery
        });

        features.push(...resp.features);
      });

    return features;
  }

  return { merge }

}