import FeatureLayer from "@arcgis/core/layers/FeatureLayer";

export function useLayerMerger() {

  async function merge(layer1: FeatureLayer, layer2: FeatureLayer) {
    await Promise.all([layer1.load(), layer2.load()]);

    const queryParams = { where: "1=1", outFields: ["*"], returnGeometry: true };
    const [result1, result2] = await Promise.all([
      layer1.queryFeatures(queryParams),
      layer2.queryFeatures(queryParams)
    ]);

    const mergedFeatures = result1.features.map(f => {
      const clone = f.clone();
      const featureOnLayer2 = result2.features.find(f2 =>
        clone.attributes.parcel_key === f2.attributes.parcel_key
        && clone.attributes.simulation_date === f2.attributes.simulation_date
      );

      if (featureOnLayer2) {
        clone.attributes.difference = clone.attributes.carbon_stock - featureOnLayer2.attributes.carbon_stock;
      }

      return clone;
    });

    return new FeatureLayer({
      title: 'Comparison Layer',
      source: mergedFeatures,
      fields: [
        ...layer1.fields,
        { name: 'difference', alias: 'difference', type: 'double' }
      ],
      objectIdField: 'OBJECTID',
      geometryType: layer1.geometryType,
      spatialReference: layer1.spatialReference
    });
  }

  return { merge }

}