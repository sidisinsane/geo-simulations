import os

from dotenv import load_dotenv

from geo_simulations.logger import log
from geo_simulations.utils import load_json
from geo_simulations.zombie_outbreak import ZombieOutbreak

load_dotenv(override=True)

LOCALITIES_FILEPATH: str = os.environ.get("LOCALITIES_FILEPATH")
if not LOCALITIES_FILEPATH:
    raise OSError("LOCALITIES_FILEPATH environment variable not set.")

if __name__ == "__main__":
    # Create all mp4 animations from JSON file.
    localities = load_json(LOCALITIES_FILEPATH)

    for locality in localities:
        zo = ZombieOutbreak(**locality)

        try:
            zo.generate_animation()
        except Exception as e:
            log.error(f"Error occurred while generating animation: {e}")
