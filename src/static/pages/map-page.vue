<template>
    <div class="d-flex flex-grow-1 position-relative">
        <ParcelsMap :on-parcel-selected="onParcelSelected"></ParcelsMap>

        <Offcanvas :open="true" title="Simulation">
            <div>
                <p>This simulation will ... {{ _textSimExplain }}</p>

                <button class="btn btn-block btn-bright-light">Execute</button>

                <h4 class="mt-3">Parameters</h4>
                
                <div class="form-group">
                    <label for="input-crop">County</label>
                    <select class="custom-select">
                        <option value="">Select county...</option>
                        <option v-for="c in counties" :key="c" :value="c">
                            {{ c }}
                        </option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="input-crop">Crop</label>
                    <select class="custom-select">
                        <option value="">Select crop...</option>
                        <option v-for="c in distinctCrops" :key="c" :value="c">
                            {{ c }}
                        </option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="input-crop">Irrigation Type</label>
                    <select class="custom-select">
                        <option value="">Select irrigation type...</option>
                        <option v-for="it in distinctIrrTypes" :key="it" :value="it">
                            {{ it }}
                        </option>
                    </select>
                </div>
            </div>
        </Offcanvas>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import ParcelsMap from '../components/parcels-map.vue';
import Offcanvas from '../components/offcanvas.vue';

const [ FeatureLayer ] = await $arcgis.import([ "@arcgis/core/layers/FeatureLayer.js" ]);

const _textSimExplain = LoremIpsum.loremIpsum({ count: 1, units: 'paragraphs' });

const selectedParcel = ref(null);

function onParcelSelected(parcel) {
    selectedParcel.value = parcel;
}

const serviceIdResp = await fetch('/api/parcels/config/view_service_id');
const serviceId = await serviceIdResp.json();

const countiesResp = await fetch('/api/parcels/config/study_area_counties');
const counties = await countiesResp.json();

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

const distinctCrops = await queryDistinctValues('crop');
const distinctIrrTypes = await queryDistinctValues('irr_type');

// const result = await tableLayer.queryFeatures({
//     where: '1=1',
//     outFields: ['land_use_code', 'crop'],
//     groupByFieldsForStatistics: ['land_use_code', 'crop'],
//     outStatistics: [{
//         onStatisticField: 'crop',
//         outStatisticFieldName: "value_count",
//         statisticType: "count"   
//     }],
//     returnGeometry: false
// });

// console.log(result.features.reduce((acc, v) => {
//     if (!acc[v.attributes.land_use_code]) {
//         acc[v.attributes.land_use_code] = [];
//     }
//     acc[v.attributes.land_use_code].push(v.attributes.crop);
//     return acc;
// }, {}));
</script>
