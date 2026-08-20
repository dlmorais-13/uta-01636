<template>
    <div class="flex-grow-1">
        <HeroBanner text="Simulations">
            <template v-slot:actions v-if="simulations.length > 0">
                <router-link to="/simulations/new">
                    <button class="btn btn-primary">Create New Simulation</button>
                </router-link>
            </template>
        </HeroBanner>

        <div class="container my-5">
            <table class="table table-striped" v-if="simulations.length > 0">
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
                    <tr v-for="simulation in simulations">
                        <td>{{ simulation.OBJECTID }}</td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;" v-if="simulation.filters && simulation.filters.length">
                                <template v-for="(f, fIdx) in simulation.filters" :key="fIdx">
                                    <SimulationParameter :parameter="f"></SimulationParameter>
                                </template>
                            </div>
                            <div v-else class="text-muted font-italic">
                                No filters configured.
                            </div>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;" v-if="simulation.params && simulation.params.length">
                                <template v-for="(p, pIdx) in simulation.params" :key="pIdx">
                                    <SimulationParameter :parameter="p"></SimulationParameter>
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
                                    <div>{{ new Date(simulation.created_date).toLocaleString() }}</div>
                                    <div>{{ simulation.completed_date ? new Date(simulation.completed_date).toLocaleString() : '-'
                                        }}
                                    </div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span :class="`text-capitalize badge badge-${getStatusClass(simulation.status)}`">{{
                                getStatusText(simulation.status) }}</span>
                        </td>
                        <td>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25em;">
                                <router-link class="btn btn-sm btn-primary" :disabled="simulation.status != 'completed'"
                                    :to="{ name: 'simulations-view', params: { id1: simulation.OBJECTID } }">
                                    Open
                                </router-link>
                                <button class="btn btn-sm btn-secondary"
                                    :disabled="simulation.status != 'completed'">Compare</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div v-else class="text-center">
                <h5 class="text-muted font-italic mb-4">No simulations found.</h5>
                <router-link to="/simulations/new">
                    <button class="btn btn-lg btn-primary">Create New Simulation</button>
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import HeroBanner from '../components/hero-banner.vue';
import SimulationParameter from '../components/simulation-parameter.vue';

const simulationsResp = await fetch('/api/simulations');
const simulations = await simulationsResp.json();

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
