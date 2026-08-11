<template>
    <div class="flex-grow-1">
        <HeroBanner text="Studies">
            <template v-slot:actions v-if="studies.length > 0">
                <router-link to="/studies/new">
                    <button class="btn btn-primary">Create New Study</button>
                </router-link>
            </template>
        </HeroBanner>

        <div class="container my-5">
            <table class="table table-striped" v-if="studies.length > 0">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Filters</th>
                        <th>Parameters</th>
                        <th>Dates</th>
                        <th>Status</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="study in studies">
                        <td>{{ study.OBJECTID }}</td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;" v-if="study.filters && study.filters.length">
                                <template v-for="(f, fIdx) in study.filters" :key="fIdx">
                                    <StudyParameter :parameter="f"></StudyParameter>
                                </template>
                            </div>
                            <div v-else class="text-muted font-italic">
                                No filters configured.
                            </div>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;" v-if="study.params && study.params.length">
                                <template v-for="(p, pIdx) in study.params" :key="pIdx">
                                    <StudyParameter :parameter="p"></StudyParameter>
                                </template>
                            </div>
                            <div v-else class="text-muted font-italic">
                                No parameters configured.
                            </div>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: .75em">
                                <div class="text-right">
                                    <div>Created:</div>
                                    <div>Completed:</div>
                                </div>
                                <div>
                                    <div>{{ new Date(study.created_date).toLocaleString() }}</div>
                                    <div>{{ study.completed_date ? new Date(study.completed_date).toLocaleString() : '-'
                                        }}
                                    </div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span :class="`text-capitalize badge badge-${getStatusClass(study.status)}`">{{
                                getStatusText(study.status) }}</span>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;">
                                <router-link class="btn btn-sm btn-primary" :disabled="study.status != 'completed'"
                                    :to="{ name: 'studies-view', params: { id1: study.OBJECTID } }">
                                    Open
                                </router-link>
                                <button class="btn btn-sm btn-secondary"
                                    :disabled="study.status != 'completed'">Compare</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div v-else class="text-center">
                <h5 class="text-muted font-italic mb-4">No studies found.</h5>
                <router-link to="/studies/new">
                    <button class="btn btn-lg btn-primary">Create New Study</button>
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import HeroBanner from '../components/hero-banner.vue';
import StudyParameter from '../components/study-parameter.vue';

const studiesResp = await fetch('/api/studies');
const studies = await studiesResp.json();

function getStatusText(status) {
    return status.replace('_', ' ');
}

function getStatusClass(status) {
    switch (status) {
        case 'in_progress':
            return 'primary';
        case 'completed':
            return 'success';
        case 'failed':
            return 'danger';
        case 'created':
        default:
            return 'secondary';
    }
}
</script>
