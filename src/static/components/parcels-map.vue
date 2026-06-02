<template>
    <arcgis-map basemap="streets-vector" class="h-auto w-100" popup-disabled>
        <arcgis-zoom slot="top-left"></arcgis-zoom>
        <arcgis-popup slot="popup"></arcgis-popup>
    </arcgis-map>
</template>

<script setup>
import { onMounted } from 'vue'

const props = defineProps({
    onParcelSelected: {
        type: Function,
        default: () => console.log('on-parcel-selected callback not defined.')
    }
});

const serviceIdResp = await fetch('/api/parcels/config/view_service_id')
const serviceId = await serviceIdResp.json()
const [
    FeatureLayer,
    Map,
    MapView,
    CustomContent,
    centroidOperator
] = await $arcgis.import([
    "@arcgis/core/layers/FeatureLayer.js",
    "@arcgis/core/Map.js",
    "@arcgis/core/views/MapView.js",
    "@arcgis/core/popup/content/CustomContent.js",
    "@arcgis/core/geometry/operators/centroidOperator"
]);
const { watch } = await $arcgis.import("@arcgis/core/core/reactiveUtils.js");
const locator = await $arcgis.import("@arcgis/core/rest/locator.js");
const locatorUrl = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer";

let historyDataWidgetCache = {};
let historyDataWidget = new CustomContent({
    outFields: ["*"],
    creator: async (event) => {
        const parcel_key = event.graphic.attributes.parcel_key;
        if (!historyDataWidgetCache[parcel_key]) {
            historyDataWidgetCache[parcel_key] = new Promise(async (resolve) => {
                const queryParams = tableLayer.createQuery();
                queryParams.where = `parcel_key = '${parcel_key}'`;
                const queryResult = await tableLayer.queryFeatures(queryParams);
                const historyFeatures = queryResult.features.sort(
                    (a, b) => {
                        if (a.attributes.survey_year === b.attributes.survey_year) {
                            return b.attributes.area - a.attributes.area;
                        }
                        return b.attributes.survey_year - a.attributes.survey_year;
                    }
                );
                
                const originalFeatureQueryResponse = await featureLayer.queryFeatures({
                    where: `OBJECTID = ${event.graphic.attributes.OBJECTID}`,
                    outFields: ["*"],
                    returnGeometry: true
                });
                const originalFeature = originalFeatureQueryResponse.features[0];
                const parcelArea = originalFeature.attributes.Shape__Area;
                
                return resolve(`<div style="width: 100%; font-size: 12px;">
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
                </div>`);
            });
        }
        return await historyDataWidgetCache[parcel_key];
    }
});

let soilDataWidgetCache = {};
let soilDataWidget = new CustomContent({
    outFields: ["*"],
    creator: async (event) => {
        const parcel_key = event.graphic.attributes.parcel_key;
        if (!soilDataWidgetCache[parcel_key]) {
            soilDataWidgetCache[parcel_key] = new Promise(async (resolve) => {
                const soilData = JSON.parse(event.graphic.attributes.map_unit_data).sort((a, b) => b.area - a.area);
                const soilIdsParam = soilData.map(s => `map_unit_ids=${s.id}`).join('&');
        
                const soilsResp = await fetch(`/api/soils/basic_data?${soilIdsParam}`);
                const soils = await soilsResp.json();
                
                const originalFeatureQueryResponse = await featureLayer.queryFeatures({
                    where: `OBJECTID = ${event.graphic.attributes.OBJECTID}`,
                    outFields: ["*"],
                    returnGeometry: true
                });
                const originalFeature = originalFeatureQueryResponse.features[0];
                const parcelArea = originalFeature.attributes.Shape__Area;
                
                return resolve(`<div style="width: 100%; font-size: 12px;">
                    <h3 style="font-size: 20px; color: #4A4A4A; font-weight: 400; margin-bottom: .25rem;">
                        Soil Composition
                    </h3>
        
                    <table style="width: 100%;">
                        <thead>
                            <tr>
                                <th style="border-bottom: 1px solid black; padding: 6px 8px;">
                                    Description
                                </th>
                                <th style="border-bottom: 1px solid black; padding: 6px 8px;">
                                    Area (m²) / %
                                </th>
                                <th style="border-bottom: 1px solid black; padding: 6px 8px; width: 39%;">
                                    Potential Crop Yields (per acre)
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            ${soilData.map((s, idx) => `
                                <tr style="background-color: ${idx % 2 === 0 ? '#f2f2f2' : '#ffffff'}">
                                    <td style="padding: 6px 8px;">
                                        ${soils.find(soil => `${soil.mukey}` === s.id).muname ?? s.id}
                                    </td>
                                    <td style="padding: 6px 8px;">
                                        ${s.area.toLocaleString('en-US', {
                                            minimumFractionDigits: 2, 
                                            maximumFractionDigits: 2
                                        })}
                                        / ${Math.min(100, Number(s.area) / parcelArea * 100).toLocaleString('en-US', {
                                            minimumFractionDigits: 2, 
                                            maximumFractionDigits: 2
                                        })}%
                                    </td>
                                    <td style="padding: 6px 8px;">
                                        ${soils
                                            .find(soil => `${soil.mukey}` === s.id)
                                            .crop_yield
                                            .map(scy => `<div>${scy.cropname}: ${scy.irryield_r} ${scy.yldunits}</div>`)
                                            .join('')
                                        }
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`);
            });
        }
        
        return await soilDataWidgetCache[parcel_key];
    }
});

let addressWidgetCache = {};
let addressWidget = new CustomContent({
    outFields: ["*"],
    creator: async (event) => {
        const parcel_key = event.graphic.attributes.parcel_key;
        if (!addressWidgetCache[parcel_key]) {
            addressWidgetCache[parcel_key] = new Promise(async (resolve) => {
                const mapPoint = centroidOperator.execute(event.graphic.geometry);
                const lat = Number(mapPoint.latitude).toFixed(6);
                const lon = Number(mapPoint.longitude).toFixed(6);
        
                const locatorResp = await locator.locationToAddress(locatorUrl, { location: mapPoint })
                    .catch((err) => {
                        console.error(err);
                        return { address: 'Address not found' }
                    });

                return resolve(`<div style="width: 100%; font-size: 12px;">
                    <h3 style="font-size: 20px; color: #4A4A4A; font-weight: 400; margin-bottom: .25rem;">
                        Location
                    </h3>

                    <p>Parcel located in <strong>${event.graphic.attributes.county} County</strong> and part of <strong>${event.graphic.attributes.basin} Basin</strong></p>
                    <p>Approximate coordinates: <strong>${lon}, ${lat}</strong></p>
                    <p>Approximate address: <strong>${locatorResp.address}</strong></p>
                `);
            });
        }
        return await addressWidgetCache[parcel_key];
    }
});

const tableLayer = new FeatureLayer({
    portalItem: { id: serviceId },
    layerId: 1
});

const featureLayer = new FeatureLayer({ 
    portalItem: { id: serviceId },
    outFields: ["*"],
    minScale: 500000,
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
            addressWidget,
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
            historyDataWidget,
            soilDataWidget
        ],
    }
});

onMounted(async () => {
    const viewElement = document.querySelector("arcgis-map");
    const popupComponent = document.querySelector("arcgis-popup");
    popupComponent.dockEnabled = true;
    popupComponent.dockOptions = {
        buttonEnabled: false,
        breakpoint: false,
        position: 'bottom-left'
    }

    viewElement.addEventListener("arcgisViewMouseWheel", (event) => {
        // Only allow zooming if the Ctrl key is held down
        if (!event.detail.native.ctrlKey) {
            event.detail.stopPropagation();
        }
    });

    viewElement.addEventListener("arcgisViewClick", async (event) => {
        console.log(event);
        const hitTestResult = await viewElement.hitTest(event.detail.screenPoint, {
            include: [featureLayer]
        });
        if (hitTestResult.results.length > 0) {
            props.onParcelSelected(hitTestResult.results[0].graphic.attributes);
            await popupComponent.fetchFeatures(event.detail);
            popupComponent.open = true;
        }

    });

    await viewElement.viewOnReady(); // Wait for the properties to be ready.

    viewElement.map.add(featureLayer); // Use the map property to add the layer.
    await viewElement.whenLayerView(featureLayer); // Wait for the layer to be usable.

    // Zoom to the layer's full extent and customize the animation.
    // await viewElement.goTo(featureLayer.fullExtent, { animate: false, duration: 0 });
    await viewElement.goTo([-111.857701, 41.734548]); viewElement.zoom = 14;

    // Constrain navigation to the layer's full extent.
    viewElement.constraints = { geometry: featureLayer.fullExtent };

    popupComponent.addEventListener('arcgisClose', () => {
        props.onParcelSelected(null);
    });
});
</script>
