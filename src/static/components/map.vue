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
    MapView,
    CustomContent
] = await $arcgis.import([
    "@arcgis/core/layers/FeatureLayer.js",
    "@arcgis/core/Map.js",
    "@arcgis/core/views/MapView.js",
    "@arcgis/core/popup/content/CustomContent.js"
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

    const tableLayer = new FeatureLayer({
        portalItem: { id: serviceId },
        layerId: 1
    });

    let historyDataWidget = new CustomContent({
        outFields: ["*"],
        creator: async (event) => {
            const parcel_key = event.graphic.attributes.parcel_key;
            
            const queryParams = tableLayer.createQuery();
            queryParams.where = `parcel_key = '${parcel_key}'`;
            const queryResult = await tableLayer.queryFeatures(queryParams);
            const historyFeatures = queryResult.features.sort(
                (a, b) => b.attributes.survey_year - a.attributes.survey_year
            );
            
            const originalFeatureQueryResponse = await featureLayer.queryFeatures({
                where: `OBJECTID = ${event.graphic.attributes.OBJECTID}`,
                outFields: ["*"],
                returnGeometry: true
            });
            const originalFeature = originalFeatureQueryResponse.features[0];
            const parcelArea = originalFeature.attributes.Shape__Area;
            
            return `<div style="width: 100%; font-size: 12px;">
                
                <h3 style="font-size: 20px; color: #4A4A4A; font-weight: 400; margin-bottom: .25rem;">
                    Land Use History
                </h3>
                
                <table style="width: 100%;">
                    <thead>
                        <tr>
                            <th style="border-bottom: 1px solid black; padding: 6px 8px;">
                                Survey Year
                                <br />
                                Area (m²) / %
                            </th>
                            <th style="border-bottom: 1px solid black; padding: 6px 8px;">
                                Land Use
                                <br />
                                Irrigation Type
                                <br />
                                Crop
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        ${historyFeatures.map((feature, idx) => `
                            <tr style="background-color: ${idx % 2 === 0 ? '#f2f2f2' : '#ffffff'}">
                                <td style="padding: 6px 8px;">
                                    <strong>${feature.attributes.survey_year}</strong>
                                    <br />
                                    ${Math.min(Number(feature.attributes.area), parcelArea).toLocaleString('en-US', {
                                        minimumFractionDigits: 2, 
                                        maximumFractionDigits: 2
                                    })}
                                    / ${Math.min(100, Number(feature.attributes.area) / parcelArea * 100).toLocaleString('en-US', {
                                        minimumFractionDigits: 2, 
                                        maximumFractionDigits: 2
                                    })}%
                                </td>
                                <td style="padding: 6px 8px;">
                                    ${feature.attributes.land_use} (${feature.attributes.land_use_code})
                                    <br />
                                    ${feature.attributes.irr_type}
                                    ${feature.attributes.crop ? '<br />' + feature.attributes.crop : ''}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`
        }
    });
    
    const featureLayer = new FeatureLayer({ 
        portalItem: { id: serviceId },
        minScale: 50000,
        maxScale: 1000,
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
                },
                historyDataWidget
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
