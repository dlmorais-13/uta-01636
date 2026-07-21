<template>
  <div class="d-flex flex-grow-1 position-relative">
    <arcgis-map id="parcels-map" basemap="streets-vector" class="h-auto w-100" popup-disabled="true">
      <arcgis-zoom slot="top-left"></arcgis-zoom>

      <div class="bg-white p-3 position-absolute shadow" style="top: 1em; right: 1em;" v-if="totalCarbonStock !== null">
        <div>Total Carbon Stock:</div>
        <strong>{{ Number(totalCarbonStock).toFixed(3) }} Mg C / ha</strong>
      </div>
    </arcgis-map>

    <arcgis-time-slider style="position: absolute; bottom: 0.75rem; left: 0.75rem; right: 0.75rem;" layout="compact"
      mode="instant" play-rate="1000" reference-element="parcels-map" time-zone="UTC"></arcgis-time-slider>
  </div>
</template>

<script setup>
import ParcelsMap from '../components/parcels-map.vue';
import { useRoute } from 'vue-router';
import { onMounted, ref } from 'vue';

const route = useRoute();
const id1 = route.params.id1;
const id2 = route.params.id2;

const totalCarbonStock = ref(null);

const serviceIdResp = await fetch('/api/studies/config/view_service_id');
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

let definitionExpression = `study_id = ${id1}`
if (id2) definitionExpression += ` or study_id = ${id2}`

// 1. Define the labeling behavior and styling.
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
    { value: 0, color: "#FFF7EC", label: "Low (0)" },
    { value: 100, color: "#FDBB84", label: "Medium (100)" },
    { value: 1000, color: "#D7301F", label: "High (1,000)" }
  ]
};

const gradientRenderer = new SimpleRenderer({
  symbol: {
    type: "simple-fill", // Use simple-marker for points, simple-line for paths
    style: "solid",
    outline: { width: 0.5, color: "white" }
  },
  visualVariables: [colorVisualVariable] // Injects the gradient logic
});

const featureLayer = new FeatureLayer({
  portalItem: { id: serviceId },
  outFields: ["*"],
  // minScale: 500000,
  // maxScale: 1000,
  renderer: gradientRenderer,
  popupEnabled: true,
  definitionExpression,
  labelingInfo: [numberLabelClass],
  timeInfo: {
    startField: 'simulation_date',
    interval: { unit: 'years', value: 1 }
  }
});

onMounted(async () => {
  const viewElement = document.querySelector("arcgis-map");

  viewElement.addEventListener("arcgisViewMouseWheel", (event) => {
    // Only allow zooming if the Ctrl key is held down
    if (!event.detail.native.ctrlKey) {
      event.detail.stopPropagation();
    }
  });

  await viewElement.viewOnReady(); // Wait for the properties to be ready.

  viewElement.map.add(featureLayer); // Use the map property to add the layer.
  const view = await viewElement.whenLayerView(featureLayer); // Wait for the layer to be usable.

  // Zoom to the layer's full extent and customize the animation.
  const extentRespose = await featureLayer.queryExtent();
  await viewElement.goTo(extentRespose.extent, { animate: false, duration: 0 });

  // Constrain navigation to the layer's full extent.
  viewElement.constraints = { geometry: featureLayer.fullExtent };

  const timeSliderElement = document.querySelector("arcgis-time-slider");
  timeSliderElement.labelFormatFunction = (value, type, element, layout) => {
    if (Array.isArray(value)) value = value[0];
    element.innerText = `${new Date(value).getUTCFullYear()}`;
  };
  timeSliderElement.fullTimeExtent = featureLayer.timeInfo.fullTimeExtent;
  timeSliderElement.stops = { interval: { unit: 'years', value: 1 } };

  const queryTotal = async () => {
    const statsQuery = view.layer.createQuery();
    statsQuery.timeExtent = timeSliderElement.timeExtent;
    statsQuery.outStatistics = [
      {
        onStatisticField: 'carbon_stock',
        outStatisticFieldName: 'TotalCarbonStock',
        statisticType: 'sum'
      }
    ];
    const queryResp = await view.queryFeatures(statsQuery);
    if (queryResp.features[0]) {
      totalCarbonStock.value = queryResp.features[0].attributes["TotalCarbonStock"];
    }
  }

  reactiveUtils.when(
    () => !view.updating,
    queryTotal,
    { initial: false }
  );

  reactiveUtils.watch(
    () => timeSliderElement.timeExtent,
    queryTotal,
    { initial: true }
  );
});
</script>