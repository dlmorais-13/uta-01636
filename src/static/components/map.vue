<template>
    <arcgis-map basemap="hybrid" class="h-auto">
        <arcgis-zoom slot="top-left"></arcgis-zoom>
        <!-- <arcgis-layer-list slot="top-right"></arcgis-layer-list>
        <arcgis-legend slot="bottom-left"></arcgis-legend> -->
    </arcgis-map>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(async () => {
    console.log('map.vue : onMounted');

    const FeatureLayer = await $arcgis.import("@arcgis/core/layers/FeatureLayer.js");
    const viewElement = document.querySelector("arcgis-map");

    viewElement.addEventListener("arcgisViewMouseWheel", (event) => {
        // Only allow zooming if the Ctrl key is held down
        if (!event.detail.native.ctrlKey) {
            event.detail.stopPropagation();
        }
    });

    await viewElement.viewOnReady(); // Wait for the properties to be ready.

    const featureLayer = new FeatureLayer({
        url: "https://services1.arcgis.com/WTeo28TIuKuIFAJu/arcgis/rest/services/UTA01636_Study_Area_view/FeatureServer/0",
    });

    viewElement.map.add(featureLayer); // Use the map property to add the layer.
    await viewElement.whenLayerView(featureLayer); // Wait for the layer to be usable.

    // Zoom to the layer's full extent and customize the animation.
    await viewElement.goTo(featureLayer.fullExtent, { animate: true, duration: 2500 });

    // Constrain navigation to the layer's full extent.
    viewElement.constraints = { geometry: featureLayer.fullExtent };
});
</script>
