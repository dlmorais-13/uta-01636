/**
 * Class to explore the data present in the public base layer view in ArcGIS Online.
 */
export default class BaseLayerExplorer {

  // Reference to the base layer.
  _baseLayer = null;
  // Year of the last survey in the data.
  _lastSurveyYear = null;

  // Caches
  _allCountiesCache = null;
  _allBasinsCache = null;
  _allCropsCache = null;
  _allIrrigationTypesCache = null;

  /**
   * Initializes the class, loading the base layer and last survey year.
   */
  async loadBaseLayer() {
    const [FeatureLayer, PortalItem] = await $arcgis.import([
      "@arcgis/core/layers/FeatureLayer.js",
      "@arcgis/core/portal/PortalItem.js"]
    );

    const serviceIdResp = await fetch('/api/parcels/config/view_service_id');
    const serviceId = await serviceIdResp.json();

    this._baseLayer = new FeatureLayer({ portalItem: { id: serviceId } });

    this._lastSurveyYear = (await this._baseLayer.queryFeatures({
      where: '1=1',
      outStatistics: [
        {
          "statisticType": "max",
          "onStatisticField": "survey_year",
          "outStatisticFieldName": "max_val",
        }
      ]
    })).features[0].attributes['max_val'];
  }

  /**
   * Returns each distinct value for a column and counts the number of parcels
   * with each of the values.
   * 
   * @param {string} column Column to be fetched.
   * @param {string} where Filters to be applied.
   * @returns List of objects with keys "value" and "count".
   */
  async _getAllColumn(column, where = '1=1') {
    const queryRes = await this._baseLayer.queryFeatures({
      where, 
      groupByFieldsForStatistics: column,
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
  async getAllCounties() {
    if (this._allCountiesCache === null) {
      this._allCountiesCache = (await this._getAllColumn('county')).map(i => i.value);
    }
    return this._allCountiesCache;
  }

  /**
   * List the basins in the base layer.
   * 
   * @returns List of the basins in the base layer.
   */
  async getAllBasins() {
    if (this._allBasinsCache === null) {
      this._allBasinsCache = (await this._getAllColumn('basin')).map(i => i.value);
    }
    return this._allBasinsCache;
  }

  /**
   * Lists all irrigation types matching the filters along with their count.
   * For each type not present, it is added with the count 0.
   * 
   * @param {array} filters Filters to be applied in the search.
   * @returns The list of irrigation types and their count.
   */
  async getAllIrrigationTypes(filters = []) {
    if (this._allIrrigationTypesCache === null) {
      this._allIrrigationTypesCache = await this._getAllColumn('irr_type');
    }

    const filteredValues = await this._getAllColumn('irr_type', this.buildWhereClauseFromFilters(filters, true));
    const filteredValuesNames = new Set(filteredValues.map(v => v.value));

    for (let irrType of this._allIrrigationTypesCache) {
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
  async getAllCrops(filters = []) {
    if (this._allCropsCache === null) {
      this._allCropsCache = await this._getAllColumn('crop');
    }

    const filteredValues = await this._getAllColumn('crop', this.buildWhereClauseFromFilters(filters, true));
    const filteredValuesNames = new Set(filteredValues.map(v => v.value));

    for (let crop of this._allCropsCache) {
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
  async getParcelStatistics(filters) {
    console.log(filters);
    const where = this.buildWhereClauseFromFilters(filters, true);
    const queryRes = await this._baseLayer.queryFeatures({
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
    const count = queryRes.features[0].attributes['parcel_count'];
    console.log(`Found ${count} parcels using filter (${where}).`);
    return queryRes.features[0].attributes;
  }

  /**
   * Builds a where clause to be used when searching the base layer, according to the
   * provided filters.
   * 
   * @param {array} filters Filters to build the where clause.
   * @param {boolean} only_last_year If should add the last survey year to the clause.
   * @returns {string} String with the built where clause.
   */
  buildWhereClauseFromFilters(filters, only_last_year = false) {
    const clausesPerFilter = {};
    for (let f of filters) {
      clausesPerFilter[f.name] = clausesPerFilter[f.name] ?? [];
      clausesPerFilter[f.name].push(`${f.column || f.name} = '${f.value}'`);
    }

    let where = !only_last_year ? "1=1" : `survey_year = '${this._lastSurveyYear}'`;
    for (let fName in clausesPerFilter) {
      const clause = clausesPerFilter[fName].join(' OR ');
      where += ` AND (${clause}) `;
    }
    return where;
  }

}
