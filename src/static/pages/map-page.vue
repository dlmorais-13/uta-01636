<template>
    <div class="d-flex flex-grow-1 position-relative">
        <ParcelsMap :on-parcel-selected="onParcelSelected"></ParcelsMap>
        <Offcanvas :open="selectedParcel" title="Parcel Level Simulation">
            <div>
                <p>This simulation will ... {{ _textSimExplain }}</p>

                <button class="btn btn-block btn-bright-light">Execute</button>

                <h4 class="mt-3">Parameters</h4>
                
                <div class="form-group">
                    <label for="input-crop">Crop</label>
                    <select class="custom-select">
                        <option value=""></option>
                        <option value="corn">Corn</option>
                        <option value="soybean">Soybean</option>
                        <option value="wheat">Wheat</option>
                        <option value="barley">Barley</option>
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

const _textSimExplain = LoremIpsum.loremIpsum({ count: 1, units: 'paragraphs' });

const selectedParcel = ref(null);

function onParcelSelected(parcel) {
    selectedParcel.value = parcel;
}
</script>
