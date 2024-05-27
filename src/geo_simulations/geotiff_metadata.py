import glob
import json
import os
from typing import Any

import rasterio
from rasterio.errors import RasterioIOError

from geo_simulations.geotiff_base import GeoTiffBase
from geo_simulations.logger import log


class GeoTiffMetadata(GeoTiffBase):
    """
    Class for managing GeoTIFF metadata.

    Inherits from GeoTiffBase and provides methods to create, load, and extract
    metadata for GeoTIFF files. Metadata is stored in-memory and can be matched
    based on geographical coordinates.

    Attributes:
        None
    """

    def __init__(self) -> None:
        """Initialize the GeoTiffMetadata class and set the metadata."""
        super().__init__()
        self.metadata_set()

    def metadata_get(self) -> dict[str, dict[str, Any]]:
        """
        Get the in-memory metadata.

        Returns:
            dict[str, dict[str, Any]]: The current metadata loaded in-memory.
        """
        return self.metadata

    def metadata_set(self) -> None:
        """
        Set the in-memory metadata.

        This method loads metadata from the storage and sets it in-memory.
        """
        self.metadata: dict[str, dict[str, Any]] = self.metadata_load()

    def metadata_match(self, lat: float, lon: float) -> dict[str, Any] | None:
        """
        Find metadata that matches the given latitude and longitude.

        Args:
            lat (float): Latitude to match.
            lon (float): Longitude to match.

        Returns:
            dict[str, Any] | None: The matched metadata or None if no match is found.
        """
        metadata: dict[str, dict[str, Any]] = self.metadata

        for key, info in metadata.items():
            bbox = info.get("bbox", {})
            if all(k in bbox for k in ["lat_min", "lat_max", "lon_min", "lon_max"]):
                if (
                    bbox["lat_min"] <= lat <= bbox["lat_max"]
                    and bbox["lon_min"] <= lon <= bbox["lon_max"]
                ):
                    return metadata[key]
        return None

    def metadata_create(self) -> None:
        """
        Create metadata for all GeoTIFF files in the directory and save it.

        This method scans the directory for GeoTIFF files, extracts their metadata,
        and saves it to the metadata file. It updates the in-memory metadata afterwards.
        """
        geotiff_filepaths = glob.glob(os.path.join(self.geotiff_dirpath, "*.tif"))
        log.info(f"Extracting metadata from {len(geotiff_filepaths)} GeoTIFF files.")

        # Load current metadata once
        current_metadata = self.metadata_load()

        for geotiff_filepath in geotiff_filepaths:
            key = os.path.splitext(os.path.basename(geotiff_filepath))[0]
            metadata = self.metadata_extract(geotiff_filepath)
            if metadata.get("error"):
                log.error(
                    f"Error extracting metadata for {geotiff_filepath}: {metadata['error']}"
                )
                continue
            current_metadata[key] = metadata
            log.info(f"Extracted metadata from {geotiff_filepath}")

        # Write updated metadata back to file once
        with open(self.geotiff_metadata_filepath, "w", encoding="utf-8") as file:
            json.dump(
                current_metadata, file, ensure_ascii=False, indent=4, sort_keys=True
            )
            log.info(f"Metadata written to {self.geotiff_metadata_filepath}")

        # Update the in-memory metadata
        self.metadata_set()

    def metadata_extract(self, geotiff_filepath: str) -> dict[str, Any]:
        """
        Extract metadata from a GeoTIFF file.

        Args:
            geotiff_filepath (str): The path to the GeoTIFF file.

        Returns:
            dict[str, Any]: Extracted metadata or an error message.
        """
        try:
            with rasterio.open(geotiff_filepath) as dataset:
                metadata = {
                    "file": geotiff_filepath,
                    "dtype": str(dataset.dtypes[0]),
                    "nodata": dataset.nodata,
                    "width": dataset.width,
                    "height": dataset.height,
                    "bands": dataset.count,
                    "crs": str(dataset.crs),
                    "bbox": {
                        "lat_min": dataset.bounds.bottom,
                        "lat_max": dataset.bounds.top,
                        "lon_min": dataset.bounds.left,
                        "lon_max": dataset.bounds.right,
                    },
                    "transform": {
                        "scale-factor-x": dataset.transform[0],
                        "shear-y-component-x": dataset.transform[1],
                        "x-translation-term": dataset.transform[2],
                        "shear-x-component-y": dataset.transform[3],
                        "scale-factor-y": dataset.transform[4],
                        "y-translation-term": dataset.transform[5],
                    },
                }
        except RasterioIOError as e:
            log.error(str(e))

        return metadata

    def metadata_load(self) -> dict[str, dict[str, Any]]:
        """
        Load metadata from the metadata file.

        This method reads the metadata from the file specified in
        `self.geotiff_metadata_filepath`.
        If the file does not exist or contains invalid data, it returns an
        empty dictionary.

        Returns:
            dict[str, dict[str, Any]]: The loaded metadata.
        """
        metadata_filepath = self.geotiff_metadata_filepath
        os.makedirs(os.path.dirname(metadata_filepath), exist_ok=True)

        if os.path.exists(metadata_filepath):
            try:
                with open(metadata_filepath, encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                log.error(f"Error loading metadata from {metadata_filepath}: {e}")
                return {}
        else:
            return {}


if __name__ == "__main__":
    gtm = GeoTiffMetadata()

    try:
        gtm.metadata_create()
    except Exception as e:
        log.error(f"Error occurred while creating metadata: {e}")

    try:
        lat = 53.558117
        lon = 9.5975027
        matched_metadata = gtm.metadata_match(lat, lon)
        print(json.dumps(matched_metadata, indent=4))
    except Exception as e:
        log.error(f"Error occurred while matching ({lat}, {lon}) with metadata: {e}")
