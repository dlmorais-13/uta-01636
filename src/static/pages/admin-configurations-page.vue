<template>
    <h1>Configurations</h1>

    <h2 class="mt-5">General Configuration</h2>
    <AdminConfigurationInput label="Study Area Counties"
        help-text="Utah counties to be used as study area. Changing this configuration requires re-calculation of all layers.">
        <div class="form-check form-check-inline" v-for="c in allCountiesForCheckbox">
            <input class="form-check-input" type="checkbox" :id="`input-study-area-counties-${c.id}`" :value="c.name"
                v-model="editableConfigs.STUDY_AREA_COUNTIES.config">
            <label class="form-check-label" :for="`input-study-area-counties-${c.id}`">{{ c.name }}</label>
        </div>
    </AdminConfigurationInput>

    <h2 class="mt-5">PRISM</h2>
    <AdminConfigurationInput label="PRISM Default Resolution">
        <div class="form-check form-check-inline" v-for="res in ['800m', '4km']">
            <input class="form-check-input" type="radio" :id="`input-prism-default-resolution-${res}`" :value="res"
                v-model="editableConfigs.PRISM_DEFAULT_RESOLUTION.config">
            <label class="form-check-label" :for="`input-prism-default-resolution-${res}`">{{ res }}</label>
        </div>
    </AdminConfigurationInput>
    <AdminConfigurationInput label="PRISM Default Periodicity">
        <div class="form-check form-check-inline" v-for="p in periodicities">
            <input class="form-check-input" type="radio" :id="`input-prism-default-resolution-${p.id}`" :value="p.name"
                v-model="editableConfigs.PRISM_DEFAULT_PERIODICITY.config">
            <label class="form-check-label" :for="`input-prism-default-resolution-${p.id}`">{{ p.name }}</label>
        </div>
    </AdminConfigurationInput>

    <h2 class="mt-5">Water-related Land Use</h2>
    <AdminConfigurationInput label="WebService Base URL">
        <input type="text" class="form-control" id="wrlu-webservice-base-url"
            v-model="editableConfigs.WRLU_REST_BASE_URL.config" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="County Columns">
        <input type="text" class="form-control" id="wrlu-county-columns"
            v-model="editableConfigs.WRLU_COUNTY_COLUMNS.config" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="Land Use Columns">
        <input type="text" class="form-control" id="wrlu-landuse-columns"
            v-model="editableConfigs.WRLU_LAND_USE_COLUMNS.config" />
    </AdminConfigurationInput>
    <AdminConfigurationInput label="Land Use Values">
        <input type="text" class="form-control" id="wrlu-landuse-values"
            v-model="editableConfigs.WRLU_LAND_USE_VALUES.config" />
    </AdminConfigurationInput>

    <AdminConfigurationInput label="Specifications">
        <div class="input-group mt-1" v-for="spec in editableConfigs.WRLU_SPECS">
            <input type="text" class="form-control" :id="`wrlu_spec_{year}`" v-model="spec.year" />
            <input type="text" class="form-control" style="flex: 4 1 auto;" :id="`wrlu_spec_{year}_config`"
                v-model="spec.config" />
        </div>

        <button class="btn btn-secondary float-right mt-1"
            @click="editableConfigs.WRLU_SPECS.push({ year: '', config: '' })">Add specification</button>
    </AdminConfigurationInput>

    <button class="btn btn-bright-light btn-lg" @click="saveConfigurations()"
        style="position: fixed; right: 4em; bottom: 0.8em; z-index: 6;">Save</button>
</template>

<script setup>
import { computed, ref } from 'vue';
import AdminConfigurationInput from '../components/admin-configuration-input.vue';

const originalConfigs = ref({})
const editableConfigs = ref({})

const props = defineProps({
    credentials: {
        type: Object,
        default: null
    }
});

if (props.credentials) {
    const response = await fetch('/api/admin/configurations', {
        headers: {
            'Authorization': `bearer ${props.credentials.token}`
        }
    });

    if (response.ok) {
        let configs = await response.json();

        configs.reduce((acc, c) => {
            switch (c.name) {
                case 'STUDY_AREA_COUNTIES':
                    acc[c.name] = {
                        config: c.config.split(',').map(v => v.trim()),
                        ObjectId: c.ObjectId
                    };
                    break;
                case c.name.startsWith('WRLU_SPEC_') ? c.name : false:
                    acc['WRLU_SPECS'] = acc['WRLU_SPECS'] || [];
                    acc['WRLU_SPECS'].push({
                        year: c.name.split('_')[2],
                        config: c.config.split('|')
                    });
                    break;
                default:
                    acc[c.name] = { config: c.config, ObjectId: c.ObjectId };
                    break;
            }

            return acc;
        }, originalConfigs.value);

        editableConfigs.value = JSON.parse(JSON.stringify(originalConfigs.value));
    }
}

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

async function saveConfigurations() {
    await fetch('/api/admin/configurations', {
        method: 'PUT',
        headers: { 'Authorization': `bearer ${props.credentials.token}` }
    });
}
</script>