<template>
  <div class="d-flex flex-grow-1 position-relative">
    <arcgis-map id="parcels-map" basemap="streets-vector" class="h-auto w-100" popup-disabled="true">
      <arcgis-zoom slot="top-left"></arcgis-zoom>

      <div class="bg-white p-3 position-absolute shadow" style="top: 1em; right: 1em;" v-if="totalCarbonStock.length">
        <div>Average Carbon Stock:</div>
        <strong v-for="(tcs, idx) of totalCarbonStock" :key="idx" class="d-block">
          Simulation {{ simulations[idx].code }}: {{ tcs.toFixed(3) }} Mg C / ha
        </strong>
      </div>
    </arcgis-map>

    <arcgis-time-slider style="position: absolute; bottom: 0.75rem; left: 0.75rem; right: 0.75rem;" layout="compact"
      mode="instant" play-rate="1000" reference-element="parcels-map" time-zone="UTC"></arcgis-time-slider>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { onMounted, ref } from 'vue';
import LayerMerger from '../utils/layer-merger.mjs';

const route = useRoute();

const simulations = ref([{ id: route.params.id1, code: 'A' }]);
if (route.params.id2) simulations.value.push({ id: route.params.id2, code: 'B' });

const totalCarbonStock = ref([]);

const serviceIdResp = await fetch('/api/simulations/config/view_service_id');
const serviceId = await serviceIdResp.json();

const [
  FeatureLayer,
  Map,
  MapView,
  CustomContent,
  centroidOperator,
  SimpleRenderer,
  reactiveUtils
] = await $arcgis.import([
  "@arcgis/core/layers/FeatureLayer.js",
  "@arcgis/core/Map.js",
  "@arcgis/core/views/MapView.js",
  "@arcgis/core/popup/content/CustomContent.js",
  "@arcgis/core/geometry/operators/centroidOperator.js",
  "@arcgis/core/renderers/SimpleRenderer.js",
  "@arcgis/core/core/reactiveUtils.js"
]);

const numberLabelClass = {
  // Autocasts as a new LabelClass.
  symbol: {
    type: "text", // Autocasts as a new TextSymbol.
    color: "white",
    haloColor: "black",
    haloSize: "2px",
    font: {
      size: 12,
      family: "sans-serif",
      weight: "bold"
    }
  },
  // Use "center-center" for points or "always-horizontal" for polygons.
  labelPlacement: "center-center",
  // Use Arcade to pull the numeric attribute field from data.
  labelExpressionInfo: {
    expression: "Concatenate(Round($feature.carbon_stock, 3), ' Mg C / ha')"
  }
};

const colorVisualVariable = {
  type: "color", // Specifies a color gradient
  field: "carbon_stock", // The data field driving the gradient
  stops: [
    { value: 0, color: "#D7301F", label: "Low (0)" },
    // { value: 100, color: "#FDBB84", label: "Medium (100)" },
    { value: 2000, color: "#FFF7EC", label: "High (1,000)" }
  ]
};

const gradientRenderer = new SimpleRenderer({
  symbol: {
    type: "simple-fill",
    style: "solid",
    outline: { width: 1, color: "black" }
  },
  visualVariables: [colorVisualVariable] // Injects the gradient logic
});

const featureLayers = simulations.value.map(simulation => new FeatureLayer({
  portalItem: { id: serviceId },
  outFields: ["*"],
  // minScale: 500000,
  // maxScale: 1000,
  renderer: gradientRenderer,
  popupEnabled: true,
  definitionExpression: `simulation_id = '${simulation.id}'`,
  labelingInfo: [numberLabelClass],
  timeInfo: {
    startField: 'simulation_date',
    interval: { unit: 'years', value: 1 }
  }
}));

let diffLayer = null;
if (featureLayers.length > 1) {
  diffLayer = await LayerMerger.merge(featureLayers[0], featureLayers[1]);
  diffLayer.renderer = gradientRenderer;
  diffLayer.renderer.visualVariables[0].field = 'difference';
  diffLayer.timeInfo = {
    startField: 'simulation_date',
    interval: { unit: 'years', value: 1 }
  }
  diffLayer.labelingInfo = [{
    // Autocasts as a new LabelClass.
    symbol: {
      type: "text",
      color: "white",
      haloColor: "black",
      haloSize: "2px",
      font: {
        size: 12,
        family: "sans-serif",
        weight: "bold"
      }
    },
    labelPlacement: "always-horizontal",
    labelExpressionInfo: {
      expression: "Concatenate(Round($feature.difference, 3), ' Mg C / ha')"
    }
  }];
}

onMounted(async () => {
  const viewElement = document.querySelector("arcgis-map");

  viewElement.addEventListener("arcgisViewMouseWheel", (event) => {
    // Only allow zooming if the Ctrl key is held down
    if (!event.detail.native.ctrlKey) {
      event.detail.stopPropagation();
    }
  });

  // Wait for the properties to be ready.
  await viewElement.viewOnReady();

  // Use the map property to add the layers.
  viewElement.map.addMany(featureLayers); 
  // Wait for the layers to be usable.
  const views = await Promise.all(featureLayers.map(fl => viewElement.whenLayerView(fl)))

  if (diffLayer) {
    viewElement.map.add(diffLayer);
    await viewElement.whenLayerView(diffLayer);
  }

  // Zoom to the layer's full extent and customize the animation.
  const extentRespose = await featureLayers[0].queryExtent();
  await viewElement.goTo(extentRespose.extent, { animate: false, duration: 0 });

  // Constrain navigation to the layer's full extent.
  viewElement.constraints = { geometry: featureLayers[0].fullExtent };

  const timeSliderElement = document.querySelector("arcgis-time-slider");
  timeSliderElement.labelFormatFunction = (value, type, element, layout) => {
    if (Array.isArray(value)) value = value[0];
    element.innerText = `${new Date(value).getUTCFullYear()}`;
  };
  timeSliderElement.fullTimeExtent = featureLayers[0].timeInfo.fullTimeExtent;
  timeSliderElement.stops = { interval: { unit: 'years', value: 1 } };

  const queryTotals = async () => {
    Promise.all(views.map(async (view, idx) => {
      const statsQuery = view.layer.createQuery();
      statsQuery.timeExtent = timeSliderElement.timeExtent;
      statsQuery.outStatistics = [
        {
          onStatisticField: 'carbon_stock',
          outStatisticFieldName: 'TotalCarbonStock',
          statisticType: 'avg'
        }
      ];
      const queryResp = await view.queryFeatures(statsQuery);
      if (queryResp.features[0] && queryResp.features[0].attributes["TotalCarbonStock"]) {
        totalCarbonStock.value[idx] = Number(queryResp.features[0].attributes["TotalCarbonStock"]);
      }
    }));
  }

  reactiveUtils.when(
    () => views.every(v => !v.updating),
    queryTotals,
    { initial: false }
  );

  reactiveUtils.watch(
    () => timeSliderElement.timeExtent,
    queryTotals,
    { initial: true }
  );
});
</script>