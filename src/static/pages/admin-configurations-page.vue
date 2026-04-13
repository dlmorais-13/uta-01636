<template>
    <h1>Configurations</h1>

    <h2 class="mt-5">General Configuration</h2>
    <AdminConfigurationInput label="Study Area Counties" help-text="Utah counties to be used as study area. Changing this configuration will
                require re-calculation of all layers.">
        <div class="form-check form-check-inline" v-for="c in allCountiesForCheckbox">
            <input class="form-check-input" type="checkbox" :id="`input-study-area-counties-${c.id}`" :value="c.id">
            <label class="form-check-label" :for="`input-study-area-counties-${c.id}`">{{ c.name }}</label>
        </div>
    </AdminConfigurationInput>

    <h2 class="mt-5">ArcGIS Online</h2>
    <AdminConfigurationInput label="ArcGIS Online URL">
        <input type="text" class="form-control" id="agol-url" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="ArcGIS Online Client ID">
        <input type="text" class="form-control" id="agol-client-id" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="ArcGIS Online Client Secret">
        <input type="text" class="form-control" id="agol-client-secret" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="ArcGIS Online Project Name">
        <input type="text" class="form-control" id="agol-project-name" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="ArcGIS Online Project Folder">
        <input type="text" class="form-control" id="agol-project-folder" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="ArcGIS Online Group ID">
        <input type="text" class="form-control" id="agol-group-id" />
    </AdminConfigurationInput>

    <h2 class="mt-5">External Layer References</h2>
    <AdminConfigurationInput label="USA Census Counties">
        <input type="text" class="form-control" id="layer-usa-census-counties" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="SSURGO Map Units">
        <input type="text" class="form-control" id="layer-ssurgo-mapunits" />
    </AdminConfigurationInput>

    <h2 class="mt-5">PRISM</h2>
    <AdminConfigurationInput label="PRISM Base URL">
        <input type="text" class="form-control" id="prism-base-url" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="PRISM Mesh Base URL">
        <input type="text" class="form-control" id="prism-base-url" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="PRISM Default Resolution">
        <div class="form-check form-check-inline" v-for="res in ['800m', '4km']">
            <input class="form-check-input" type="radio" :id="`input-prism-default-resolution-${res}`" :value="res">
            <label class="form-check-label" :for="`input-prism-default-resolution-${res}`">{{ res }}</label>
        </div>
    </AdminConfigurationInput>
    <AdminConfigurationInput label="PRISM Default Periodicity">
        <div class="form-check form-check-inline" v-for="p in periodicities">
            <input class="form-check-input" type="radio" :id="`input-prism-default-resolution-${p.id}`" :value="p.id">
            <label class="form-check-label" :for="`input-prism-default-resolution-${p.id}`">{{ p.name }}</label>
        </div>
    </AdminConfigurationInput>

    <h2 class="mt-5">Water-related Land Use</h2>
    <AdminConfigurationInput label="WebService Base URL">
        <input type="text" class="form-control" id="wrlu-webservice-base-url" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="County Columns">
        <input type="text" class="form-control" id="wrlu-county-columns" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="Land Use Columns">
        <input type="text" class="form-control" id="wrlu-landuse-columns" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="Land Use Values">
        <input type="text" class="form-control" id="wrlu-landuse-values" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="Specifications">
        <input type="text" class="form-control" id="wrlu-landuse-spec" />
    </AdminConfigurationInput>

    <button class="btn btn-bright-light btn-lg"
        style="position: fixed; right: 4em; bottom: 0.8em; z-index: 6;">Save</button>
</template>

<script setup>
import { computed } from 'vue';
import AdminConfigurationInput from '../components/admin-configuration-input.vue';

const allCounties = [
    'Beaver', 'Box Elder', 'Cache', 'Carbon', 'Daggett', 'Davis', 'Duchesne',
    'Emery', 'Garfield', 'Grand', 'Iron', 'Juab', 'Kane', 'Millard', 'Morgan',
    'Piute', 'Rich', 'Salt Lake', 'San Juan', 'Sanpete', 'Sevier', 'Summit',
    'Tooele', 'Uintah', 'Utah', 'Wasatch', 'Washington', 'Wayne', 'Weber'];

const allCountiesForCheckbox = computed(() => allCounties.map(c => ({ id: c.toLowerCase().replaceAll(' ', '-'), name: c })));

const periodicities = [
    { id: 'daily', name: 'Daily' },
    { id: 'daily-normals', name: 'Daily Normals' },
    { id: 'monthly', name: 'Monthly' },
    { id: 'monthly-normals', name: 'Monthly Normals' },
]

</script>