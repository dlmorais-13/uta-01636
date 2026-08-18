from arcgis.features import FeatureSet


class GeoPandasUtils:
    """
    Utility class for convertions from/to GeoPandas and ArcGIS Online formats.

    TODO The current name for this class is not good. It is not operating over
    any data in GeoPandas format.
    """

    @staticmethod
    def featureset_to_geojson(fs: FeatureSet) -> str:
        """
        Converts a feature set into GeoJson.

        Args:
            fs: FeatureSet to be converted.

        Returns:
            The GeoJson with all the features.
        """

        if type(fs) is FeatureSet:
            return FeatureSet(
                features=[f for f in fs.features if f.geometry is not None],
                geometry_type=fs.geometry_type,
                spatial_reference=fs.spatial_reference,
                fields=fs.fields,
            ).to_geojson
        elif type(fs) is dict:
            return FeatureSet(
                features=[f for f in fs["features"] if f["geometry"] is not None],
                geometry_type=fs["geometryType"],
                spatial_reference=fs["spatialReference"],
                fields=fs["fields"],
            ).to_geojson
        else:
            raise RuntimeError(f"Unknown type of FeatureSet: {type(fs)}")
