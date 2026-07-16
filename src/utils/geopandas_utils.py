from arcgis.features import FeatureSet


class GeoPandasUtils:

    @staticmethod
    def featureset_to_geojson(fs: FeatureSet):
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
