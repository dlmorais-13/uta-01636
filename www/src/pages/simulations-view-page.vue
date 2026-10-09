<template>
  <div class="d-flex flex-grow-1 position-relative">
    <arcgis-map ref="mapRef" id="parcels-map" basemap="streets-vector" class="h-auto w-100" popup-disabled="true"
      @arcgisViewReadyChange="handleMapReady">
      <arcgis-zoom slot="top-left"></arcgis-zoom>

      <div class="bg-white p-3 position-absolute shadow" style="top: 1em; right: 1em;" v-if="totalCarbonStock.length">
        <div>Average Carbon Stock:</div>
        <strong v-for="(tcs, idx) of totalCarbonStock" :key="idx" class="d-block">
          Simulation {{ simulations[idx]?.code }}: {{ tcs.toFixed(3) }} Mg C / ha
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

const { merge } = useLayerMerger();
const route = useRoute();

const simulations = ref([{ id: route.params.id1, code: 'A' }]);
if (route.params.id2) simulations.value.push({ id: route.params.id2, code: 'B' });

const totalCarbonStock: Ref<number[]> = ref([]);

const { serviceId } = useSimulations();

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
  labelExpressionInfo: {
    expression: "Text($feature.carbon_stock, '#,###')"
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

const featureLayers = simulations.value.map(simulation => new FeatureLayer({
  portalItem: { id: serviceId.value },
  outFields: ["*"],
  minScale: 1000000,
  maxScale: 1000,
  renderer: gradientRenderer,
  popupEnabled: true,
  definitionExpression: `simulation_id = '${simulation.id}'`,
  labelingInfo: [numberLabelClass],
  timeInfo: {
    startField: 'simulation_date',
    interval: { unit: 'years', value: 1 }
  },

  featureReduction: {
    type: "cluster",
    clusterMinSize: 24,
    maxScale: 10000,
    fields: [
      {
        name: "carbon_stock",
        onStatisticField: "carbon_stock",
        statisticType: "avg"
      }
    ],
    renderer: {
      type: "simple",
      symbol: {
        type: "simple-marker",
        color: [0, 122, 255, 0.8],
        size: "24px",
        outline: {
          color: "white",
          width: 1.5
        }
      },
      visualVariables: [colorVisualVariable]
    },
    labelingInfo: [
      {
        deconflictionStrategy: "none",
        ...numberLabelClass
      },
    ],
  }
}));

let diffLayer: FeatureLayer | null = null;
if (featureLayers.length > 1) {
  diffLayer = await merge(featureLayers[0]!, featureLayers[1]!);
  diffLayer.renderer = gradientRenderer;
  diffLayer.renderer.visualVariables![0]!.field = 'difference';
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
  viewElement.map.addMany(featureLayers);
  // Wait for the layers to be usable.
  const views = await Promise.all(featureLayers.map(fl => viewElement.whenLayerView(fl)))

  if (diffLayer) {
    viewElement.map.add(diffLayer);
    await viewElement.whenLayerView(diffLayer);
  }

  // Zoom to the layer's full extent and customize the animation.
  const extentRespose = await featureLayers[0].queryExtent();
  if (extentRespose && extentRespose.extent)
    await viewElement.goTo(extentRespose.extent, { animate: false, duration: 0 });

  // Constrain navigation to the layer's full extent.
  if (featureLayers[0].fullExtent)
    viewElement.constraints = new MapViewConstraints({
      geometry: featureLayers[0].fullExtent
    });

  const timeSliderElement = document.querySelector("arcgis-time-slider") as ArcgisTimeSlider;
  timeSliderElement.labelFormatFunction = (value, _1, element, _2) => {
    if (Array.isArray(value)) value = value[0];
    element.innerText = `${new Date(value).getUTCFullYear()}`;
  };
  console.debug('featureLayers[0]', featureLayers[0]);
  if (featureLayers[0].timeInfo) {
    timeSliderElement.fullTimeExtent = featureLayers[0].timeInfo.fullTimeExtent;
    timeSliderElement.stops = { interval: new TimeInterval({ unit: 'years', value: 1 }) };
  }

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
};
</script>