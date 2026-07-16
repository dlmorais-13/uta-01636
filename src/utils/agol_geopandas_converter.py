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
            df (GeoDataFrame): The GeoDataFrame to convert.
            wkid (int): The coordinate system to be used. Defaults to 4326.

        Returns:
            list[Feature]: A list of Features.
        """

        features: list[Feature] = []
        for _, row in df.iterrows():
            feature_attrs = row.drop("geometry").to_dict()

            arcgis_rings = []
            polygons = (
                row["geometry"].geoms
                if row["geometry"].geom_type == "MultiPolygon"
                else [row["geometry"]]
            )
            for poly in polygons:
                oriented_poly = orient(poly, sign=-1)
                arcgis_rings.append(list(oriented_poly.exterior.coords))
                for interior in oriented_poly.interiors:
                    arcgis_rings.append(list(interior.coords))

            geom = Polygon(
                {
                    "hasZ": False,
                    "hasM": False,
                    "rings": arcgis_rings,
                    "spatialReference": {"wkid": wkid},
                }
            )

            features.append(Feature(attributes=feature_attrs, geometry=geom))

        return features
