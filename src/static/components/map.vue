<template>
    <arcgis-map basemap="streets-vector" class="h-auto w-100" popup-disabled>
        <arcgis-zoom slot="top-left"></arcgis-zoom>
        <arcgis-popup slot="popup" dock-enabled="false"></arcgis-popup>
    </arcgis-map>
</template>

<script setup>
import { onMounted } from 'vue'

const serviceIdResp = await fetch('/api/parcels/config/view_service_id')
const serviceId = await serviceIdResp.json()
const [
    FeatureLayer,
    Map,
    MapView
] = await $arcgis.import([
    "@arcgis/core/layers/FeatureLayer.js",
    "@arcgis/core/Map.js",
    "@arcgis/core/views/MapView.js"
]);

onMounted(async () => {
    const viewElement = document.querySelector("arcgis-map");
    const popupComponent = document.querySelector("arcgis-popup");

    viewElement.addEventListener("arcgisViewMouseWheel", (event) => {
        // Only allow zooming if the Ctrl key is held down
        if (!event.detail.native.ctrlKey) {
            event.detail.stopPropagation();
        }
    });

    viewElement.addEventListener("arcgisViewClick", async (event) => {
        await popupComponent.fetchFeatures(event.detail);
        popupComponent.open = true;
    });

    await viewElement.viewOnReady(); // Wait for the properties to be ready.

    const featureLayer = new FeatureLayer({ 
        portalItem: { id: serviceId },
        popupEnabled: true,
        popupTemplate: {
            title: "Parcel {OBJECTID}",
            expressionInfos: [
                {
                    name: 'AreaAcres',
                    title: 'Acres',
                    expression: '$feature.Shape__Area / 4046.865'
                }
            ],
            content: [
                {
                    type: 'text',
                    text: 'Parcel located in {County} County and part of {Basin} Basin'
                },
                {
                    type: 'fields',
                    title: 'Area',
                    description: 'Parcel Area in square meters (m²) and acres',
                    fieldInfos: [
                        {
                            fieldName: "Shape__Area",
                            label: "Square meters (m²)",
                            fieldFormat: {
                                type: "number",
                                useGrouping: "always",
                                maximumFractionDigits: 2
                            }
                        },
                        {
                            fieldName: "expression/AreaAcres",
                            label: "Acres",
                            fieldFormat: {
                                type: "number",
                                useGrouping: "always",
                                maximumFractionDigits: 2
                            }
                        }
                    ]
                }
            ],
        }
    });

    viewElement.map.add(featureLayer); // Use the map property to add the layer.
    await viewElement.whenLayerView(featureLayer); // Wait for the layer to be usable.

    // Zoom to the layer's full extent and customize the animation.
    await viewElement.goTo(featureLayer.fullExtent, { animate: true, duration: 2500 });

    // Constrain navigation to the layer's full extent.
    viewElement.constraints = { geometry: featureLayer.fullExtent };
});
</script>
