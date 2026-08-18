from arcgis.features import Feature
from arcgis.geometry import Polygon
from geopandas import GeoDataFrame
from shapely.ops import orient


class AgolGeopandasConverter:
    """
    Class to convert data from AGOL format to GeoPandas and vice-versa.
    """

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
