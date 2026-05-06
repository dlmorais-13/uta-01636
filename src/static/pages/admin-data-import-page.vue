<template>
    <h1>Data Import</h1>

    <div class="row">
        <div class="col-lg-6 d-flex" v-for="dataPoint in dataPoints">
            <div class="card nav-card mb-3 w-100">
                <div class="card-body">
                    <h3 class="h4 mb-2">{{ dataPoint.name }}</h3>
                    <p>{{ dataPoint.description }}</p>

                    <ul class="list-group" v-if="dataPoint.imports[0].name != '<default>'">
                        <li v-for="i in dataPoint.imports" :key="`${i.id}:${i.status}`"
                            class="list-group-item justify-content-between align-items-center d-flex">
                            <div>
                                <div>{{ i.name }}</div>
                                <i class="badge" :class="statuses[i.status].badge">{{ statuses[i.status].text }}</i>
                            </div>
                            <button class="btn btn-sm btn-info" @click="process(dataPoint.id, i.id)">Import</button>
                        </li>
                    </ul>
                    <div v-else>
                        <button class="btn btn-info" @click="process(dataPoint.id)">Import</button>
                    </div>
                </div>
                <div class="card-footer p-2 bg-info"></div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    credentials: {
        type: Object,
        default: null
    }
});

const statuses = {
    'not-imported': { text: 'Not imported', badge: 'badge-secondary' },
    'partially-imported': { text: 'Partially imported', badge: 'badge-warning' },
    'fully-imported': { text: 'Fully imported', badge: 'badge-success' },
    'in-progress': { text: 'In progress', badge: 'badge-primary' },
    'scheduled': { text: 'Scheduled', badge: 'badge-secondary' },
    'unknown': { text: 'Unknown', badge: 'badge-secondary' },
}

const dataPoints = ref([
    {
        id: 'study-area',
        name: 'Study Area',
        description: 'Layer with the study area limits.',
        imports: [
            {
                name: 'Layer',
                status: 'fully-imported'
            }
        ]
    },
    {
        name: 'Base Layer',
        description: 'Layer with the parcels in the study area limits.',
        imports: [
            {
                name: 'WRLU Data',
                status: 'not-imported'
            }
        ]
    },
    {
        name: 'PRISM Mesh',
        description: 'PRISM Mesh within the study area limits. Used to associate parcels with PRISM data.',
        imports: [
            {
                name: '4km resolution',
                status: 'fully-imported'
            },
            {
                name: '800m resolution',
                status: 'fully-imported'
            }
        ]
    },
    {
        name: 'PRISM Daily Data',
        description: 'PRISM daily data for the cells within the study area limits.',
        imports: [
            {
                name: '4km resolution',
                status: 'not-imported'
            },
            {
                name: '800m resolution',
                status: 'not-imported'
            }
        ]
    },
    {
        name: 'PRISM Monthly Data',
        description: 'PRISM monthly data for the cells within the study area limits.',
        imports: [
            {
                name: '4km resolution',
                status: 'not-imported'
            },
            {
                name: '800m resolution',
                status: 'not-imported'
            }
        ]
    },
    {
        name: 'PRISM Daily Normals Data',
        description: 'PRISM daily normals data for the cells within the study area limits.',
        imports: [
            {
                name: '4km resolution',
                status: 'not-imported'
            },
            {
                name: '800m resolution',
                status: 'not-imported'
            }
        ]
    },
    {
        name: 'PRISM Monthly Normals Data',
        description: 'PRISM monthly normals data for the cells within the study area limits.',
        imports: [
            {
                name: '4km resolution',
                status: 'not-imported'
            },
            {
                name: '800m resolution',
                status: 'not-imported'
            }
        ]
    }
])

const dataPointsResp = await fetch("/api/admin/data", {
    headers: {
        'Authorization': `bearer ${props.credentials.token}`
    }
});

if (dataPointsResp.ok) {
    dataPoints.value = await dataPointsResp.json()
}

let runningProcesses = [];
async function checkForStatus() {
    const results = await Promise.allSettled(runningProcesses.map(p =>
        reloadImportData(p.dataPointId, p.importId)
    ));

    for (let rIdx in results) {
        if (!(['in-progress', 'scheduled'].includes(results[rIdx].value.status))) {
            runningProcesses = runningProcesses.filter(p => p.importId !== results[rIdx].value.id);
        }
    }

    if (runningProcesses.length) setTimeout(checkForStatus, 5000);
}

async function reloadImportData(dataPointId, importId) {
    const resp = await fetch(`/api/admin/data/${dataPointId}/import/${importId}`, {
        headers: {
            'Authorization': `bearer ${props.credentials.token}`
        }
    })

    const dp = dataPoints.value.find(dp => dp.id == dataPointId);
    const ipIdx = dp.imports.findIndex(ip => ip.id == importId);
    dp.imports[ipIdx] = await resp.json();
    return dp.imports[ipIdx];
}

async function process(dataPointId, importId) {
    await fetch(`/api/admin/data/${dataPointId}/import/${importId}/process`, {
        method: 'POST',
        headers: {
            'Authorization': `bearer ${props.credentials.token}`
        }
    })

    const dp = dataPoints.value.find(dp => dp.id == dataPointId);
    const ipIdx = dp.imports.findIndex(ip => ip.id == importId);
    dp.imports[ipIdx].status = 'scheduled';

    runningProcesses.push({ dataPointId, importId });
    checkForStatus();
}
</script>
