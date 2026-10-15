from arcgis.features import Feature, FeatureSet
from arcgis.geometry import Polygon
from geopandas import GeoDataFrame
from shapely.ops import orient
import json


class AgolGeopandasConverter:
    """
    Class to convert data from AGOL format to GeoPandas and vice-versa.
    """

    @staticmethod
    def featuresToDataframe(feature_set: FeatureSet) -> GeoDataFrame:
        """
        Convert a FeatureSet into a GeoDataFrame.

        Args:
            feature_set: The feature set to convert.

        Returns:
            The newly build GeoDataFrame.
        """

        return GeoDataFrame.from_features(json.loads(feature_set.to_geojson)).set_crs(
            3857
        )

    @staticmethod
    def dataframeToFeatures(df: GeoDataFrame, wkid: int = 4326) -> list[Feature]:
        """
        Convert a GeoDataFrame to a list of Features.

        Args:
            df: The GeoDataFrame to convert.
            wkid: The coordinate system to be used. Defaults to 4326.

        Returns:
            The list of Features.
        """

        features: list[Feature] = []
        for _, row in df.iterrows():
            feature_attrs = row.drop("geometry").to_dict()

            geom = Polygon(
                {
                    "hasZ": False,
                    "hasM": False,
                    "rings": AgolGeopandasConverter.geodataframeGeometryToArcgisRings(
                        row["geometry"]
                    ),
                    "spatialReference": {"wkid": wkid},
                }
            )

            features.append(Feature(attributes=feature_attrs, geometry=geom))

        return features

    @staticmethod
    def geodataframeGeometryToArcgisRings(geom) -> list:
        """
        Converts a GeoDataFrame geometry into ArcGIS Online list
        representation of rings.

        Args:
            geom: The geometry to be converted.

        Returns:
            The list representation in ArcGIS Online format.
        """

        arcgis_rings = []
        polygons = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
        for poly in polygons:
            oriented_poly = orient(poly, sign=-1)
            arcgis_rings.append(list(oriented_poly.exterior.coords))
            for interior in oriented_poly.interiors:
                arcgis_rings.append(list(interior.coords))

        return arcgis_rings

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
