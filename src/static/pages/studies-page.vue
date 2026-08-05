<template>
    <div class="flex-grow-1">
        <HeroBanner text="Studies">
            <template v-slot:actions>
                <router-link to="/studies/new">
                    <button class="btn btn-primary">Create New Study</button>
                </router-link>
            </template>
        </HeroBanner>

        <div class="container my-5">
            <table class="table table-striped">
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
                        <td>{{ study.study_id }}</td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;">
                                <template v-for="(f, fIdx) in study.filters" :key="fIdx">
                                    <StudyParameter :parameter="f"></StudyParameter>
                                </template>
                            </div>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;">
                                <template v-for="(p, pIdx) in study.params" :key="pIdx">
                                    <StudyParameter :parameter="p"></StudyParameter>
                                </template>
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
                                    <div>{{ study.completed_date ? new Date(study.completed_date).toLocaleString() : '-' }}</div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span :class="`text-capitalize badge badge-${getStatusClass(study.status)}`">{{ getStatusText(study.status) }}</span>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;">
                                <router-link class="btn btn-sm btn-primary" :disabled="study.status != 'completed'"
                                    :to="{ name: 'studies-view', params: { id1: study.study_id } }">
                                    Open
                                </router-link>
                                <button class="btn btn-sm btn-secondary" :disabled="study.status != 'completed'">Compare</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
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
        default:
            return 'secondary';
    }
}
</script>
