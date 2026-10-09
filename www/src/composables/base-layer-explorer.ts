import type { SimulationFilters, ValueCount } from "@/types";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer";

/**
 * Class to explore the data present in the public base layer view in ArcGIS Online.
 */
export function useBaseLayerExplorer() {

  // Reference to the base layer.
  const _baseLayer: FeatureLayer = new FeatureLayer({ portalItem: { id: import.meta.env.VITE_AGOL_BASE_LAYER_VIEW_ID } });

  // Caches
  let _lastSurveyYear: number | null = null;
  let _allCountiesCache: string[] | null = null;
  let _allBasinsCache: string[] | null = null;
  let _allCropsCache: ValueCount[] | null = null;
  let _allIrrigationTypesCache: ValueCount[] | null = null;

  /**
   * Gets the year of the last survey.
   */
  async function getLastSurveyYear() {
    if (_lastSurveyYear === null) {
      _lastSurveyYear = (await _baseLayer.queryFeatures({
        where: '1=1',
        outStatistics: [
          {
            "statisticType": "max",
            "onStatisticField": "survey_year",
            "outStatisticFieldName": "max_val",
          }
        ]
      })).features[0]!.attributes['max_val'];
    }
    return _lastSurveyYear;
  }

  /**
   * Returns each distinct value for a column and counts the number of parcels
   * with each of the values.
   * 
   * @param {string} column Column to be fetched.
   * @param {string} where Filters to be applied.
   * @returns List of objects with keys "value" and "count".
   */
  async function _getAllColumn(column: string, where = '1=1') {
    const queryRes = await _baseLayer.queryFeatures({
      where,
      groupByFieldsForStatistics: [column],
      outStatistics: [{
        onStatisticField: column,
        outStatisticFieldName: 'count',
        statisticType: 'count'
      }]
    });

    console.log(`Found ${queryRes.features.length} features for filter (${where}) to query column ${column}.`, queryRes);
    return queryRes.features
      .map(f => ({ value: f.attributes[column], count: f.attributes.count }))
      .sort((a, b) => a.value.localeCompare(b.value));
  }

  /**
   * List the counties in the base layer.
   * 
   * @returns List of the counties in the base layer.
   */
  async function getAllCounties() {
    if (_allCountiesCache === null) {
      _allCountiesCache = (await _getAllColumn('county')).map(i => i.value);
    }
    return _allCountiesCache;
  }

  /**
   * List the basins in the base layer.
   * 
   * @returns List of the basins in the base layer.
   */
  async function getAllBasins() {
    if (_allBasinsCache === null) {
      _allBasinsCache = (await _getAllColumn('basin')).map(i => i.value);
    }
    return _allBasinsCache;
  }

  /**
   * Lists all irrigation types matching the filters along with their count.
   * For each type not present, it is added with the count 0.
   * 
   * @param {array} filters Filters to be applied in the search.
   * @returns The list of irrigation types and their count.
   */
  async function getAllIrrigationTypes(filters: Array<SimulationFilters> = []) {
    if (_allIrrigationTypesCache === null) {
      _allIrrigationTypesCache = await _getAllColumn('irr_type');
    }

    const filteredValues = await _getAllColumn('irr_type', await buildWhereClauseFromFilters(filters, true));
    const filteredValuesNames = new Set(filteredValues.map(v => v.value));

    for (const irrType of _allIrrigationTypesCache) {
      if (!filteredValuesNames.has(irrType.value))
        filteredValues.push({ value: irrType.value, count: 0 });
    }

    return filteredValues.sort((a, b) => a.value.localeCompare(b.value));
  }

  /**
   * Lists all crops types matching the filters along with their count.
   * For each type not present, it is added with the count 0.
   * 
   * @param {array} filters Filters to be applied in the search.
   * @returns The list of crops and their count.
   */
  async function getAllCrops(filters: Array<SimulationFilters> = []) {
    if (_allCropsCache === null) {
      _allCropsCache = await _getAllColumn('crop');
    }

    const filteredValues = await _getAllColumn('crop', await buildWhereClauseFromFilters(filters, true));
    const filteredValuesNames = new Set(filteredValues.map(v => v.value));

    for (const crop of _allCropsCache) {
      if (!filteredValuesNames.has(crop.value))
        filteredValues.push({ value: crop.value, count: 0 });
    }

    return filteredValues.sort((a, b) => a.value.localeCompare(b.value));
  }

  /**
   * Calculates the parcel statistics for a given filter.
   * 
   * @param {array} filters Filters to be applied in the calculation.
   * @returns Object with the parcel count (parcel_count) and total area in m² (total_area).
   */
  async function getParcelStatistics(filters: Array<SimulationFilters>) {
    console.log(filters);
    const where = await buildWhereClauseFromFilters(filters, true);
    const queryRes = await _baseLayer.queryFeatures({
      where,
      returnDistinctValues: true,
      outStatistics: [{
        onStatisticField: 'parcel_key',
        outStatisticFieldName: 'parcel_count',
        statisticType: 'count'
      }, {
        onStatisticField: 'area',
        outStatisticFieldName: 'total_area',
        statisticType: 'sum'
      }]
    });

    if (queryRes.features[0]) {
      const count = queryRes.features[0].attributes['parcel_count'];
      console.log(`Found ${count} parcels using filter (${where}).`);
      return queryRes.features[0].attributes;
    }
  }

  /**
   * Builds a where clause to be used when searching the base layer, according to the
   * provided filters.
   * 
   * @param {array} filters Filters to build the where clause.
   * @param {boolean} only_last_year If should add the last survey year to the clause.
   * @returns {string} String with the built where clause.
   */
  async function buildWhereClauseFromFilters(filters: Array<SimulationFilters>, only_last_year = false) {
    const clausesPerFilter: Record<string, Array<string>> = {};
    for (const f of filters) {
      clausesPerFilter[f.name] = clausesPerFilter[f.name] ?? [];
      clausesPerFilter[f.name]!.push(`${f.column || f.name} = '${f.value}'`);
    }

    let where = !only_last_year ? "1=1" : `survey_year = '${await getLastSurveyYear()}'`;
    for (const fName in clausesPerFilter) {
      const clause = clausesPerFilter[fName]!.join(' OR ');
      where += ` AND (${clause}) `;
    }
    return where;
  }

  return {
    buildWhereClauseFromFilters,
    getAllBasins,
    getAllCounties,
    getAllCrops,
    getAllIrrigationTypes,
    getParcelStatistics
  }
}
