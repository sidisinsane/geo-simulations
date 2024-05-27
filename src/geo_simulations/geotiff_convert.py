import glob
import os
import pathlib

import numpy
import rasterio
from PIL import Image

from geo_simulations.geotiff_base import GeoTiffBase
from geo_simulations.logger import log

DEFAULT_MIN_THRESHOLD: int = 0
DEFAULT_MAX_THRESHOLD: int = 255
DEFAULT_GAMMA: float = 0.6


class GeoTiffConvert(GeoTiffBase):
    """
    Class for converting GeoTIFF files to PNG format.

    This class provides methods for converting individual GeoTIFF files to PNG
    format and converting all GeoTIFF files in a directory. It inherits from
    GeoTiffBase to utilize common functionalities.

    Attributes:
        None
    """

    def __init__(self) -> None:
        """
        Initialize the GeoTiffConvert class.

        This method initializes the GeoTiffConvert class.
        """
        super().__init__()

    def convert_all(
        self,
        min_threshold: int = DEFAULT_MIN_THRESHOLD,
        max_threshold: int = DEFAULT_MAX_THRESHOLD,
        gamma: float = DEFAULT_GAMMA,
        force: bool = False,
    ) -> None:
        """
        Convert all GeoTIFF files in the directory to PNG format.

        This method converts all GeoTIFF files in the specified directory to PNG format
        using the provided thresholds and gamma correction. Optionally, it can force
        conversion even if the PNG file already exists.

        Args:
            min_threshold (int): Minimum threshold for pixel values (default 1).
            max_threshold (int): Maximum threshold for pixel values (default 255).
            gamma (float): Gamma correction value (default 1.0).
            force (bool): Force conversion even if PNG already exists (default False).
        """
        geotiff_filepaths = glob.glob(os.path.join(self.geotiff_dirpath, "*.tif"))
        log.info(f"Converting {len(geotiff_filepaths)} GeoTIFF files.")

        for geotiff_filepath in geotiff_filepaths:
            png_filepath = os.path.join(self.pdm_dirpath, f"{pathlib.Path(geotiff_filepath).stem}.png")
            self.convert(
                geotiff_filepath,
                png_filepath,
                min_threshold,
                max_threshold,
                gamma,
                force,
            )
            log.info(f"Created {png_filepath}")

    def convert(
        self,
        geotiff_filepath: str,
        png_filepath: str,
        min_threshold: int = 1,
        max_threshold: int = 255,
        gamma: float = 1.0,
        force: bool = False,
    ) -> None:
        """
        Convert a single GeoTIFF file to PNG format.

        This method converts a single GeoTIFF file to PNG format using the provided
        thresholds and gamma correction. Optionally, it can force conversion even if
        the PNG file already exists.

        Args:
            geotiff_filepath (str): Path to the input GeoTIFF file.
            png_filepath (str): Path to save the output PNG file.
            min_threshold (int): Minimum threshold for pixel values (default 1).
            max_threshold (int): Maximum threshold for pixel values (default 255).
            gamma (float): Gamma correction value (default 1.0).
            force (bool): Force conversion even if PNG already exists (default False).
        """
        if os.path.exists(png_filepath) and not force:
            log.info(f"File {png_filepath} already exists. Skipping conversion.")
            return

        os.makedirs(os.path.dirname(png_filepath), exist_ok=True)

        try:
            with rasterio.open(geotiff_filepath) as dataset:
                data = dataset.read(1)

                nodata_value = dataset.nodata
                if nodata_value is not None:
                    data = numpy.where(data == nodata_value, numpy.nan, data)

                data = numpy.clip(data, min_threshold, max_threshold)

                data_min = numpy.nanmin(data)
                data_max = numpy.nanmax(data)

                if data_max != data_min:
                    data_normalized = ((data - data_min) / (data_max - data_min) * 255).astype(numpy.uint8)
                else:
                    data_normalized = numpy.zeros_like(data, dtype=numpy.uint8)

                data_normalized = 255 * (data_normalized / 255) ** (1 / gamma)
                data_normalized = data_normalized.astype(numpy.uint8)

                image = Image.fromarray(data_normalized)
                image.save(png_filepath)

            log.info(f"GeoTIFF {geotiff_filepath} converted to PNG at {png_filepath}")

        except Exception as e:
            log.error(f"Error converting {geotiff_filepath}: {e}")


if __name__ == "__main__":
    gtc = GeoTiffConvert()

    try:
        gtc.convert_all()
    except Exception as e:
        log.error(f"Error occurred during conversion: {e}")
