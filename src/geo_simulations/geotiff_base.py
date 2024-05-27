import os

from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv(override=True)


# Fetch environment variables.
GEOTIFF_DIRPATH: str = os.environ.get("GEOTIFF_DIRPATH")
if not GEOTIFF_DIRPATH:
    raise OSError("GEOTIFF_DIRPATH environment variable not set.")
PDM_DIRPATH: str = os.environ.get("PDM_DIRPATH")
if not PDM_DIRPATH:
    raise OSError("PDM_DIRPATH environment variable not set.")
GEOTIFF_METADATA_FILEPATH: str = os.environ.get("GEOTIFF_METADATA_FILEPATH")
if not GEOTIFF_METADATA_FILEPATH:
    raise OSError("GEOTIFF_METADATA_FILEPATH environment variable not set.")
MP4_DIRPATH: str = os.environ.get("MP4_DIRPATH")
if not MP4_DIRPATH:
    raise OSError("MP4_DIRPATH environment variable not set.")
GIF_DIRPATH: str = os.environ.get("GIF_DIRPATH")
if not GIF_DIRPATH:
    raise OSError("GIF_DIRPATH environment variable not set.")


class GeoTiffBase:
    """
    Base class for GeoTIFF handling.

    This class provides the shared configuration for other GeoTiff related classes.

    Attributes:
        None
    """

    def __init__(
        self,
        geotiff_dirpath: str = GEOTIFF_DIRPATH,
        pdm_dirpath: str = PDM_DIRPATH,
        mp4_dirpath: str = MP4_DIRPATH,
        gif_dirpath: str = GIF_DIRPATH,
        geotiff_metadata_filepath: str = GEOTIFF_METADATA_FILEPATH,
    ) -> None:
        self.geotiff_dirpath = geotiff_dirpath
        self.pdm_dirpath = pdm_dirpath
        self.mp4_dirpath = mp4_dirpath
        self.gif_dirpath = gif_dirpath
        self.geotiff_metadata_filepath = geotiff_metadata_filepath
