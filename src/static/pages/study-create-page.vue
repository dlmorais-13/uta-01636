<template>
  <div class="flex-grow-1 pb-4">
    <HeroBanner text="Create New Study"></HeroBanner>

    <div class="container">
      <div class="row mt-5">
        <div class="col-lg-8">
          <div class="d-flex w-100 justify-content-between steps">
            <div :class="{ 'active': step === 1, 'clickable': step > 1 }" @click="setStep(1)">
              <div>Step 1</div>
              <div v-if="step === 1">{{ stepTitle() }}</div>
              <div v-else-if="step > 1" class="text-capitalize">{{ stepValue(1) }}</div>
            </div>
            <div :class="{ 'active': step === 2, 'clickable': step > 2 }" @click="setStep(2)">
              <div>Step 2</div>
              <div v-if="step === 2">{{ stepTitle() }}</div>
              <div v-else-if="step > 2">{{ stepValue(2) }}</div>
            </div>
            <div :class="{ 'active': step === 3 }">
              <div>Step 3</div>
              <div v-if="step === 3">{{ stepTitle() }}</div>
            </div>
          </div>

          <div class="mt-5">
            <div v-if="step === 1" class="d-flex flex-column align-items-stretch px-5 w-50 mx-auto">
              <button class="btn btn-secondary" @click="chooseType('filter')" :disabled="parameters.length">Add a
                filter</button>
              <div class="align-items-center d-flex my-3 separator">
                <div class="bg-blue-dark w-50 separator-div"></div>
                <span class="font-weight-bold text-blue-dark">OR</span>
                <div class="bg-blue-dark w-50 separator-div"></div>
              </div>
              <button class="btn btn-secondary" @click="chooseType('parameter')">Add a parameter</button>
            </div>

            <div v-if="step === 2" class="d-grid grid-2 px-5 w-75 mx-auto gap-1">
              <template v-if="dataToAdd.type === 'filter'">
                <div v-for="filter in filtersAvailable">
                  <UsuCard class="h-100">
                    <div class="gap-1 d-flex flex-column h-100">
                      <div>
                        <strong>{{ filter.name }}</strong>
                        <br />
                        <em class="text-capitalize">{{ filter.type }} filter</em>
                      </div>
                      <div>{{ filter.description }}</div>
                      <div class="d-flex flex-column flex-grow-1 justify-content-end">
                        <button class="btn btn-primary btn-block" @click="chooseFilter(filter)">
                          Use this filter
                        </button>
                      </div>
                    </div>
                  </UsuCard>
                </div>
              </template>

              <template v-else-if="dataToAdd.type === 'parameter'">
                <div v-for="param in parametersAvailable">
                  <UsuCard class="h-100">
                    <div class="gap-1 d-flex flex-column h-100">
                      <div>
                        <strong>{{ param.name }}</strong>
                        <br />
                        <em class="text-capitalize">{{ param.type }} parameter</em>
                      </div>
                      <div>{{ param.description }}</div>
                      <div class="d-flex flex-column flex-grow-1 justify-content-end">
                        <button class="btn btn-primary btn-block" @click="chooseParameter(param)">
                          Use this parameter
                        </button>
                      </div>
                    </div>
                  </UsuCard>
                </div>
              </template>
            </div>

            <div v-if="step === 3" class="align-items-stretch px-5 w-75 mx-auto gap-1">
              <div v-if="dataToAdd.filter?.type === 'location' || dataToAdd.filter?.type === 'management'"
                class="d-grid grid-min-100 gap-1" id="filter-config-type-location">
                <div class="form-check" v-for="opt in dataToAdd.filter.options">
                  <input class="form-check-input" type="checkbox" :id="`input-${dataToAdd.filter.name}-${opt}`"
                    :value="opt" v-model="dataToAdd.value">
                  <label class="form-check-label" :for="`input-${dataToAdd.filter.name}-${opt}`">{{ opt }}</label>
                </div>
              </div>

              <div v-else-if="dataToAdd.parameter?.type === 'target'" id="param-config-type-target">
                <div class="form-group">
                  <label for="param-config-type-target-select">
                    Choose a <span class="text-lowercase">{{ dataToAdd.parameter.name }}</span>
                  </label>
                  <select class="form-control" v-model="dataToAdd.value.option" id="param-config-type-target-select"
                    @change="onSelectTargetItem()">
                    <option>Select a {{ dataToAdd.parameter.name }}</option>
                    <option v-for="opt in dataToAdd.parameter.options" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="param-config-type-target-input">
                    Define a target for <span class="text-lowercase">{{ dataToAdd.parameter.name }}</span>
                  </label>
                  <div class="input-group">
                    <input type="range" class="form-control custom-range" v-model="dataToAdd.value.target"
                      id="param-config-type-target-input" min="0" max="100" step="0.001" />
                    <input type="number" class="form-control" v-model="dataToAdd.value.target" min="0" max="100"
                      step="0.001" style="flex: 0 1 auto; min-width: 6em;" />
                    <div class="input-group-append">
                      <span class="input-group-text">%</span>
                    </div>
                  </div>
                </div>
              </div>

              <button class="btn btn-block btn-primary btn-lg mt-5" @click="useFilterOrParameter()"
                :disabled="!dataToAddValid()">
                Use this {{ dataToAdd.type }}
              </button>
            </div>
          </div>
        </div>

        <div class="col-lg-4 current-filters-params-div">
          <UsuCard>
            <p class="text-muted fst-italic small">Click on a filter or parameter to remove it from the study
              configuration.</p>

            <div>
              <h4>Filters</h4>
              <span v-if="!filters.length" class="text-muted font-italic">No filters applied.</span>
              <div v-else class="d-flex gap-half flex-wrap">
                <StudyParameter v-for="(f, idx) of filters" :key="idx" :parameter="f" @click="removeFilter(idx)"
                  class="clickable" />
              </div>
            </div>

            <div class="my-3">
              <h4>Parameters</h4>
              <span v-if="!parameters.length" class="text-muted font-italic">No parameters applied.</span>
              <div v-else class="d-flex gap-half flex-wrap">
                <StudyParameter v-for="(p, idx) of parameters" :key="idx" :parameter="p" @click="removeParamter(idx)"
                  class="clickable" />
              </div>
            </div>

            <div class="my-3">
              <h4>Study numbers</h4>

              <div>
                <template v-if="!loadingParcelStats">
                  <div>{{ usFormatter.format(parcelCount) }} parcels</div>
                  <div>{{ usFormatter.format(parcelTotalArea.toFixed(3)) }} km²</div>
                </template>
                <span v-else class="pt-2 d-block">
                  <UsuSpinner></UsuSpinner>
                </span>
              </div>
            </div>

            <div class="mt-5">
              <ButtonSpinner class="btn btn-block btn-lg btn-primary" @click="createStudy()" :loading="savingStudy">
                Create Study
              </ButtonSpinner>
            </div>
          </UsuCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import HeroBanner from '../components/hero-banner.vue';
import UsuCard from '../components/usu-card.vue';
import StudyParameter from '../components/study-parameter.vue';
import { ref, onMounted } from 'vue';
import UsuSpinner from '../components/usu-spinner.vue';
import ButtonSpinner from '../components/button-spinner.vue';
import BaseLayerExplorer from '../utils/base-layer-explorer.mjs';
import { useRouter } from 'vue-router';

// Filters configured in the page.
const filters = ref([]);
// Parameters configured in the page.
const parameters = ref([]);
// Current step in the configuration wizard.
const step = ref(1);
// Number of parcels in current filter.
const parcelCount = ref(0);
// Total area (km²) of the parcels in the current filter.
const parcelTotalArea = ref(0);
// Indicates if the parcel statistics are being loaded.
const loadingParcelStats = ref(false);
// Indicates if the system is saving the study.
const savingStudy = ref(false);
// Stores the current configuration in the wizard.
const dataToAdd = ref({});
// List of the filters available. They are loaded only once.
const filtersAvailable = ref([]);
// List of the parameters available. They are loaded every time the filters change.
const parametersAvailable = ref([]);
// Formatter for numbers.
const usFormatter = new Intl.NumberFormat('en-US');
// Creates an instance of the base layer explorer class.
const layerExplorer = new BaseLayerExplorer();

const router = useRouter();

await layerExplorer.loadBaseLayer();

// Lists all data required for the filters.
const [countyList, basinList, cropList, irrTypeList] = await Promise.all([
  layerExplorer.getAllCounties(),
  layerExplorer.getAllBasins(),
  layerExplorer.getAllCrops(),
  layerExplorer.getAllIrrigationTypes()
]);

// Build the county filter.
filtersAvailable.value.push({
  type: 'location',
  name: 'County',
  description: 'Filters the study to consider only the parcels located in specific counties.',
  options: countyList
});

// Build the basin filter.
filtersAvailable.value.push({
  type: 'location',
  name: 'Basin',
  description: 'Filters the study to consider only the parcels located in specific basins.',
  options: basinList
});

// Build the crop filter.
filtersAvailable.value.push({
  type: 'management',
  name: 'Crop',
  description: 'Filters the study to consider only the parcels currently cultivating specific crops.',
  options: cropList.map(i => i.value)
});

// Build the irrigation type filter.
filtersAvailable.value.push({
  type: 'management',
  name: 'Irrigation Type',
  column: 'irr_type',
  description: 'Filters the study to consider only the parcels currently using specific irrigation types.',
  options: irrTypeList.map(i => i.value)
});

/**
 * Load the parameters available to be configured.
 * 
 * @param filters Filters current applied in the page.
 */
async function loadParameters(filters) {
  parametersAvailable.value = [];

  // Load all necessary data at the same time.
  const [crops, irrTypes] = await Promise.all([
    layerExplorer.getAllCrops(filters),
    layerExplorer.getAllIrrigationTypes(filters)
  ]);

  const parametersToConfig = [{
    type: 'target',
    name: 'Crop',
    source: crops,
    description: 'Defines the number of parcels cultivating a specific type of crop.',
  }, {
    type: 'target',
    name: 'Irrigation Types',
    source: irrTypes,
    description: 'Defines the number of parcels using a specific irrigation type.',
  }];

  parametersToConfig.forEach(p => {
    const totalCount = p.source.reduce((acc, i) => acc + i.count, 0);
    parametersAvailable.value.push({
      type: p.type,
      name: p.name,
      description: p.description,
      options: p.source.map(i => ({
        label: `${i.value} (${i.count})`,
        value: i.value
      })),
      optionPercentage: p.source.reduce((acc, i) => {
        acc[i.value] = i.count / totalCount;
        return acc;
      }, {})
    });
  });
}

/**
 * Loads the parcel statistics for current filters.
 * 
 * @param filters Filters current applied in the page.
 */
async function loadParcelStats(filters) {
  const parcelStats = await layerExplorer.getParcelStatistics(filters);
  parcelCount.value = parcelStats.parcel_count;
  parcelTotalArea.value = parcelStats.total_area / 10 ** 6;
}

/**
 * Resets the wizard to the initial state.
 */
function resetForm() {
  step.value = 1;
  dataToAdd.value = {
    type: null,
    filter: null,
    parameter: null,
    value: null
  };
}

// Call once when loading the page.
resetForm();

/**
 * Loads the data that may change depending on the selected filters.
 */
async function loadFilterRelatedData() {
  try {
    loadingParcelStats.value = true;

    const results = await Promise.allSettled([
      loadParameters(filters.value),
      loadParcelStats(filters.value)
    ]);

    results.forEach(r => {
      if (r.status === 'rejected') throw (r.reason);
    });
  } catch (e) {
    console.error(e);
  } finally {
    loadingParcelStats.value = false;
  }
}

// Load the filter related data when the page is loaded.
await loadFilterRelatedData();

/**
 * Returns the title for each of the steps.
 * 
 * Only operate over the current enabled step, since the name is only shown for
 * this step.
 */
function stepTitle() {
  switch (step.value) {
    case 1:
      return 'Choose filter or parameter';
    case 2:
      return `Choose the type of ${dataToAdd.value.type}`;
    case 3:
      return `Choose the value for the ${dataToAdd.value.type}`;
  }
}

/**
 * Returns the value defined for a given step.
 * 
 * @param stepNumber Number of the step.
 */
function stepValue(stepNumber) {
  switch (stepNumber) {
    case 1:
      return dataToAdd.value.type;
    case 2:
      return dataToAdd.value.filter?.name || dataToAdd.value.parameter?.name;
    case 3:
      return dataToAdd.value.value;
  }
}

/**
 * Sets the step number in the wizard, resetting the form if necessary.
 * Only used to go back in the wizard.
 * 
 * @param stepNumber Step number to the defined.
 */
function setStep(stepNumber) {
  if (step.value > stepNumber) {
    if (stepNumber === 1) resetForm();
    step.value = stepNumber
  };
}

/**
 * Selects a type of configuration being added in the wizard.
 * 
 * @param type Type chosen: filter or parameter.
 */
function chooseType(type) {
  dataToAdd.value.type = type;
  if (type === 'filter') delete dataToAdd.value.parameter;
  if (type === 'parameter') delete dataToAdd.value.filter;
  step.value = 2;
}

/**
 * Choose a filter.
 * 
 * @param filter Filter chosen.
 */
function chooseFilter(filter) {
  dataToAdd.value.filter = filter;
  if (filter.options) dataToAdd.value.value = [];
  step.value = 3;
}

/**
 * Choose a parameter.
 * 
 * @param parameter Parameter chosen.
 */
function chooseParameter(parameter) {
  dataToAdd.value.parameter = parameter;
  if (parameter.type === 'target') dataToAdd.value.value = { option: null, target: null };
  step.value = 3;
}

/**
 * Function called when the user finishes configuring a filter or parameter.
 * Will call the necessary method to add the configuration, then reset the form
 * and reload the filter related data, if necessary.
 */
async function useFilterOrParameter() {
  switch (dataToAdd.value.type) {
    case 'filter':
      useFilter();
      resetForm();
      await loadFilterRelatedData();
      break;
    case 'parameter':
      useParameter();
      resetForm();
      break;
  }

}

/**
 * Call the appropriate filter configuration function according
 * to the filter type.
 */
function useFilter() {
  switch (dataToAdd.value.filter.type) {
    case 'location':
    case 'management':
      useTextFilter();
      break;
  }
}

/**
 * Configures a filter as a text filter.
 */
function useTextFilter() {
  for (let value of dataToAdd.value.value) {
    // Only adds a text filter if it was not already added before.
    if (!filters.value.find(f => f.column === dataToAdd.value.filter.column && f.value === value)) {
      filters.value.push({
        type: 'text',
        name: dataToAdd.value.filter.name,
        column: dataToAdd.value.filter.column,
        value
      });
    }
  }
}

/**
 * Call the appropriate parameter configuration function according
 * to the filter type.
 */
function useParameter() {
  switch (dataToAdd.value.parameter.type) {
    case 'target':
      useTargetParameter();
      break;
  }
}

/**
 * Configures a parameter as a target value parameter.
 */
function useTargetParameter() {
  const targetName = dataToAdd.value.parameter.name;

  let parameter = parameters.value.find(p => {
    return p.value === dataToAdd.value.value.option
      && p.name === `${targetName.charAt(0).toUpperCase() + targetName.slice(1)} Target`
  });

  // If the same parameter was added before, change its target to the new value.
  if (parameter) {
    parameter.target = dataToAdd.value.value.target / 100;
  } else {
    parameters.value.push({
      type: 'target',
      name: `${targetName.charAt(0).toUpperCase() + targetName.slice(1)} Target`,
      value: dataToAdd.value.value.option,
      target: dataToAdd.value.value.target / 100
    });
  }
}

/**
 * Removes a filter from the list of applied filters.
 * 
 * @param idx Index of the removed filter.
 */
async function removeFilter(idx) {
  filters.value.splice(idx, 1);
  await loadFilterRelatedData();
}

/**
 * Removes a parameter from the list of applied parameters.
 * 
 * @param idx Index of the parameter.
 */
function removeParamter(idx) {
  parameters.value.splice(idx, 1);
}

/**
 * Called when user is configuring target type parameters, when the
 * user changes the target item, its current value is loaded into the target
 * slider.
 */
function onSelectTargetItem() {
  dataToAdd.value.value.target = Number(dataToAdd.value.parameter.optionPercentage[dataToAdd.value.value.option] * 100).toFixed(3);
}

/**
 * Checks if the object being manipulated by the wizard is valid.
 */
function dataToAddValid() {
  if (!dataToAdd.value.type) return false;
  if (dataToAdd.value.type === 'filter') {
    return dataToAdd.value.filter && dataToAdd.value.value;
  } else if (dataToAdd.value.type === 'parameter') {
    switch (dataToAdd.value.parameter.type) {
      case 'target':
        return dataToAdd.value.value.option && !isNaN(dataToAdd.value.value.target);
      default:
        return !!dataToAdd.value.value;
    }
  }
}

/**
 * Creates the new study.
 */
async function createStudy() {
  savingStudy.value = true;
  this.validateStudyConfiguration();
  const resp = await fetch('/api/studies/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      filters: filters.value,
      parameters: parameters.value
    })
  });

  if (resp.ok) {
    const content = await resp.json();
    if (content.OBJECTID) {
      router.push('/studies')
    } else {
      savingStudy.value = false;
    }
  } else {
    savingStudy.value = false;
  }
}

/**
 * Checks if the configured filters are valid.
 */
function validateFilters() {
  // TODO implement.
}

/**
 * Checks if the configured parameters are valid.
 */
function validateParameters() {
  // TODO implement.
}

/**
 * Checks if the study configuration is valid.
 */
function validateStudyConfiguration() {
  // TODO implement properly.
  this.validateFilters();
  this.validateParameters();
}
</script>

<style scoped>
.separator {
  gap: .5em;
}

.separator>div {
  height: .25em;
}

.steps>div {
  border-bottom: 3px solid var(--usu-gray);
  /* color: var(--usu-gray); */
  padding: 0 .5em .5em;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 15%;
}

.steps>div.active {
  flex-grow: 1;
  border-bottom: 3px solid var(--usu-aggie-blue);
  /* color: var(--usu-aggie-blue); */
}

.steps>div>*:first-child {
  font-weight: bold;
}
</style>
