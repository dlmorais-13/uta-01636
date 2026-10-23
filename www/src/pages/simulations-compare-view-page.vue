<template>
  <div class="d-flex flex-grow-1 position-relative">
    <arcgis-map ref="mapRef" id="parcels-map" basemap="streets-vector" class="h-auto w-100" popup-disabled="true"
      @arcgisViewReadyChange="handleMapReady">
      <arcgis-zoom slot="top-left"></arcgis-zoom>

      <div class="bg-white p-3 position-absolute shadow" style="top: 1em; right: 1em;">
        <div>Average Carbon Stock:</div>
        <strong class="d-block">
          <span>Simulation A: </span>
          <span v-if="totalCarbonStockA">{{ totalCarbonStockA.toFixed(3) }} Mg C / ha</span>
          <span v-else>n/a</span>
        </strong>
        <strong class="d-block">
          <span>Simulation B: </span>
          <span v-if="totalCarbonStockB">{{ totalCarbonStockB.toFixed(3) }} Mg C / ha</span>
          <span v-else>n/a</span>
        </strong>
      </div>
    </arcgis-map>

    <arcgis-time-slider style="position: absolute; bottom: 0.75rem; left: 0.75rem; right: 0.75rem;" layout="compact"
      mode="instant" play-rate="1000" reference-element="parcels-map" time-zone="UTC"></arcgis-time-slider>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { ref, type Ref } from 'vue';
import { useLayerMerger } from '@/composables/layer-merger';
import SimpleRenderer from '@arcgis/core/renderers/SimpleRenderer';
import FeatureLayer from '@arcgis/core/layers/FeatureLayer';
import { useSimulations } from '@/composables/simulations';
import type { ColorVariableProperties } from '@arcgis/core/renderers/visualVariables/ColorVariable';
import type { LabelClassProperties } from '@arcgis/core/layers/support/LabelClass';
import type { ViewMouseWheelEvent } from '@arcgis/core/views/input/types';
import type { ArcgisMap } from '@arcgis/map-components/components/arcgis-map';
import '@arcgis/map-components/components/arcgis-map';
import '@arcgis/map-components/components/arcgis-zoom';
import '@arcgis/map-components/components/arcgis-time-slider';
import type { ArcgisTimeSlider } from '@arcgis/map-components/components/arcgis-time-slider';
import TimeInterval from '@arcgis/core/time/TimeInterval';
import MapViewConstraints from '@arcgis/core/views/2d/MapViewConstraints';
import * as reactiveUtils from "@arcgis/core/core/reactiveUtils.js";
import type Graphic from '@arcgis/core/Graphic';

const { merge } = useLayerMerger();
const route = useRoute();

const simulations = ref<Array<{ id: string, code: string }>>([
  { id: route.params.id1 as string, code: 'A' },
  { id: route.params.id2 as string, code: 'B' }
]);

const totalCarbonStockA: Ref<number | undefined> = ref();
const totalCarbonStockB: Ref<number | undefined> = ref();

const { serviceId, getSimulation } = useSimulations();

// const simulationsData = (await Promise.all(
//   simulations.value
//     .map(s => getSimulation(Number(s.id)))
// )).reduce<Record<string, Graphic>>((acc, sd) => {
//   if (sd)
//     acc[sd.attributes.OBJECTID] = sd
//   return acc;
// }, {});

const numberLabelClass: LabelClassProperties = {
  symbol: {
    type: "text",
    color: "white",
    haloColor: "black",
    haloSize: "1px",
    font: {
      size: 12,
      family: "Josefin Slab",
      weight: "bold"
    }
  },
  labelPlacement: "center-center",
  // labelPlacement: "always-horizontal",
  labelExpressionInfo: {
    expression: "Text(DefaultValue($feature.difference, 0), '#,###')"
  }
};

const colorVisualVariable: ColorVariableProperties & { type: 'color' } = {
  type: "color",
  field: "carbon_stock",
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
  visualVariables: [colorVisualVariable]
});

const featureLayers = simulations.value.map(simulation => {
  return new FeatureLayer({
    portalItem: { id: serviceId.value },
    outFields: ['carbon_stock', 'simulation_date'],
    // minScale: 1000000,
    // maxScale: 1000,
    // renderer: gradientRenderer,
    // popupEnabled: true,
    definitionExpression: `simulation_id = '${simulation.id}' and tract is not null`,
    // labelingInfo: [numberLabelClass],
    // timeInfo: {
    //   startField: 'simulation_date',
    //   interval: {
    //     unit: 'years',
    //     value: 1,
    //   }
    // },
  })
});

const diffLayer: FeatureLayer = await merge(featureLayers[0]!, featureLayers[1]!);
diffLayer.renderer = gradientRenderer;
diffLayer.renderer.visualVariables![0]!.field = 'difference';
diffLayer.timeInfo = {
  startField: 'simulation_date',
  interval: { unit: 'years', value: 1 }
}
diffLayer.labelingInfo = [numberLabelClass];

const mapRef: Ref<ArcgisMap | null> = ref(null);
async function handleMapReady() {
  const viewElement = mapRef.value;
  console.debug('viewElement', viewElement);
  if (!viewElement) return;
  console.debug('viewElement.map', viewElement.map);
  if (!viewElement.map) return;
  console.debug('featureLayers[0]', featureLayers[0]);
  if (!featureLayers[0]) return;

  viewElement.addEventListener("arcgisViewMouseWheel", (event: CustomEvent<ViewMouseWheelEvent>) => {
    // Only allow zooming if the Ctrl key is held down
    if (!event.detail.native.ctrlKey) {
      event.detail.stopPropagation();
    }
  });

  // Wait for the properties to be ready.
  await viewElement.viewOnReady();

  // Use the map property to add the layers.
  viewElement.map.add(diffLayer);
  // Wait for the layers to be usable.
  const view = await viewElement.whenLayerView(diffLayer);

  // Zoom to the layer's full extent and customize the animation.
  const extentRespose = await diffLayer.queryExtent();
  if (extentRespose && extentRespose.extent)
    await viewElement.goTo(extentRespose.extent, { animate: false, duration: 0 });

  // Constrain navigation to the layer's full extent.
  if (diffLayer.fullExtent)
    viewElement.constraints = new MapViewConstraints({
      geometry: diffLayer.fullExtent
    });

  const timeSliderElement = document.querySelector("arcgis-time-slider") as ArcgisTimeSlider;
  timeSliderElement.labelFormatFunction = (value, _, element) => {
    if (Array.isArray(value)) value = value[0];
    element.innerText = `${new Date(value).getUTCFullYear()}`;
  };
  console.debug('diffLayer', diffLayer);
  if (diffLayer.timeInfo) {
    timeSliderElement.fullTimeExtent = diffLayer.timeInfo.fullTimeExtent;
    timeSliderElement.fullTimeExtent?.end?.setFullYear(timeSliderElement.fullTimeExtent?.end?.getFullYear() - 1);
    timeSliderElement.stops = { interval: new TimeInterval({ unit: 'years', value: 1 }) };
  }

  const queryTotals = async () => {
    const statsQuery = view.layer.createQuery();
    statsQuery.timeExtent = timeSliderElement.timeExtent;
    statsQuery.outStatistics = [
      {
        onStatisticField: 'carbon_stock',
        outStatisticFieldName: 'TotalCarbonStockA',
        statisticType: 'avg'
      },
      {
        onStatisticField: 'carbon_stock2',
        outStatisticFieldName: 'TotalCarbonStockB',
        statisticType: 'avg'
      }
    ];
    const queryResp = await view.queryFeatures(statsQuery);
    if (queryResp.features[0]) {
      totalCarbonStockA.value = Number(queryResp.features[0].attributes["TotalCarbonStockA"]);
      totalCarbonStockB.value = Number(queryResp.features[0].attributes["TotalCarbonStockB"]);
    }
  }

  reactiveUtils.when(
    () => !view.updating,
    queryTotals,
    { initial: false }
  );

  reactiveUtils.watch(
    () => timeSliderElement.timeExtent,
    queryTotals,
    { initial: true }
  );
};
</script>