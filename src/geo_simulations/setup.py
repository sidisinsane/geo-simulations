import os
import random

from dotenv import load_dotenv

from geo_simulations.geotiff_convert import GeoTiffConvert
from geo_simulations.geotiff_metadata import GeoTiffMetadata
from geo_simulations.logger import log
from geo_simulations.utils import load_json
from geo_simulations.zombie_outbreak import ZombieOutbreak

load_dotenv(override=True)

LOCALITIES_FILEPATH: str = os.environ.get("LOCALITIES_FILEPATH")
if not LOCALITIES_FILEPATH:
    raise OSError("LOCALITIES_FILEPATH environment variable not set.")

if __name__ == "__main__":
    # 1. Convert all GeoTiffs to PNGs.
    gtc = GeoTiffConvert()

    try:
        gtc.convert_all()
    except Exception as e:
        log.error(f"Error occurred during conversion: {e}")

    # # 2. Create the metadata file.
    # gtm = GeoTiffMetadata()

    # try:
    #     gtm.metadata_create()
    # except Exception as e:
    #     log.error(f"Error occurred while creating metadata: {e}")

    # # 3. Create random example animation from JSON file.
    # localities = load_json(LOCALITIES_FILEPATH)
    # locality = random.choice(localities)

    # zo = ZombieOutbreak(**locality)

    # try:
    #     zo.generate_animation()
    # except Exception as e:
    #     log.error(f"Error occurred while generating animation: {e}")
