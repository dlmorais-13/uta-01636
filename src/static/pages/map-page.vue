<template>
    <div class="d-flex flex-grow-1 position-relative">
        <ParcelsMap :on-parcel-selected="onParcelSelected"></ParcelsMap>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import ParcelsMap from '../components/parcels-map.vue';
import Offcanvas from '../components/offcanvas.vue';

const [ FeatureLayer ] = await $arcgis.import([ "@arcgis/core/layers/FeatureLayer.js" ]);

const selectedParcel = ref(null);

function onParcelSelected(parcel) {
    selectedParcel.value = parcel;
}

const serviceIdResp = await fetch('/api/parcels/config/view_service_id');
const serviceId = await serviceIdResp.json();

const tableLayer = new FeatureLayer({
    portalItem: { id: serviceId },
    layerId: 1
});

const queryDistinctValues = async function (field) {
    const result = await tableLayer.queryFeatures({
        where: '1=1',
        outFields: [field],
        groupByFieldsForStatistics: [field],
        outStatistics: [{
            onStatisticField: field,
            outStatisticFieldName: "value_count",
            statisticType: "count"   
        }],
        returnGeometry: false
    });

    const total_value_count = result.features.reduce((acc, v) => acc + v.attributes.value_count, 0);

    return result.features.map(f => `${f.attributes[field]} (${f.attributes.value_count} - ${(f.attributes.value_count / total_value_count * 100).toFixed(2)}%)`);
}
</script>
