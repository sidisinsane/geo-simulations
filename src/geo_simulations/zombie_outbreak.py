import json
import os
import pathlib
from typing import Any

import numpy
from moviepy.editor import ImageClip, VideoClip
from PIL import Image
from scipy.ndimage import convolve

from geo_simulations.geotiff_metadata import GeoTiffMetadata
from geo_simulations.logger import log
from geo_simulations.utils import load_json

DEFAULT_DISPERSION_RATES: list[float] = [0, 0.07, 0.03]
DEFAULT_HOURS_PER_SECOND: int = 168
DEFAULT_INFECTION_RATE: float = 0.3
DEFAULT_INCUBATION_RATE: float = 0.1
DEFAULT_TIMESTEP: float = 1.0
DEFAULT_START_LEVEL: float = 0.8


class ZombieOutbreak(GeoTiffMetadata):
    """
    Model of a Zombie outbreak starting at given geo-coordinates.

    Scenario
    --------

    The population is divided into 3 groups (modified SIR model):

    S: Sane (S) individuals (blue)
    I: Infected (I) individuals (yellow)
    R: Rampaging (R) Zombies (red)

    The rules:

    - Sane individuals are immobile (they comply with the lockdown).
    - Infected individuals move rapidly (they are in panic).
    - Zombies move slowly and infect the sane.

    The consequences:

    Infected individuals tend to flee to larger settlements. As a consequence,
    those settlements will be contaminated ahead of the main Zombie wave.
    """

    def __init__(
        self, country_code: str, locality: str, lat: float, lon: float, width: int = 400
    ) -> None:
        """
        Initialize the ZombieOutbreak class with the given parameters.

        Args:
            country_code (str): The ISO 3166-1 alpha-2 country code.
            locality (str): The locality or city name.
            lat (float): Latitude of the starting point.
            lon (float): Longitude of the starting point.
            width (int): Width of the resulting media file in pixels (default 400).
        """
        super().__init__()

        self.set_locality(locality=locality)
        self.set_country_code(country_code=country_code)

        self.set_latitude(lat)
        self.set_longitude(lon)
        self.set_width(width)

        self.set_pdm_filepath()
        self.set_mp4_filepath()
        self.set_gif_filepath()

        self.set_dispersion_kernel()
        self.set_dispersion_rates()
        self.set_hours_per_second()
        self.set_infection_rate()
        self.set_incubation_rate()
        self.set_timestep()
        self.set_world()

    def generate_animation(
        self,
        duration: int = 25,
        fps: int = 15,
        is_gif: bool = False,
        force: bool = False,
    ) -> None:
        """
        Create MP4 or GIF animation of the zombie outbreak simulation.

        Args:
            duration (int): Duration of the video in seconds (default 25).
            fps (int): Frames per second for the video (default 15).
            is_gif (bool): Whether to save as a GIF file (default False).
            force (bool): Whether to force creation even if the file exists
                (default False).
        """
        clip = self.get_clip_from_frame(duration)
        filepath = self.gif_filepath if is_gif else self.mp4_filepath
        save_method = self.save_clip_as_gif if is_gif else self.save_clip_as_mp4

        if not os.path.exists(filepath) or force:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            save_method(clip, filepath, fps=fps)
            log.info(f"Generated animation at {filepath}")
        else:
            log.info(f"Animation already exists at {filepath}")

    def set_country_code(self, country_code: str) -> None:
        """
        Set the country code for the simulation.

        Args:
            country_code (str): The ISO 3166-1 alpha-2 country code.
        """
        self.country_code = country_code.lower()

    def set_locality(self, locality: str) -> None:
        """
        Set the locality for the simulation.

        Args:
            locality (str): The locality or city name.
        """
        self.locality = locality.lower()

    def set_latitude(self, lat: float) -> None:
        """
        Set the latitude for the simulation.

        Args:
            lat (float): Latitude in decimal degrees.
        """
        self.lat = lat

    def set_longitude(self, lon: float) -> None:
        """
        Set the longitude for the simulation.

        Args:
            lon (float): Longitude in decimal degrees.
        """
        self.lon = lon

    def set_width(self, width: int) -> None:
        """
        Set the width of the resulting media file.

        Args:
            width (int): Width in pixels.
        """
        self.width = width

    def set_pdm_filepath(self) -> None:
        """
        Set the file path for the population density map image.

        This method attempts to match the provided coordinates to a metadata entry
        and constructs the file path for the population density map (PDM) image.
        """
        try:
            metadata_match = self.metadata_match(self.lat, self.lon)
            # print(json.dumps(metadata_match, indent=4))
            geotiff_filepath = metadata_match["file"]
            self.pdm_filepath = os.path.join(
                self.pdm_dirpath, f"{pathlib.Path(geotiff_filepath).stem}.png"
            )
        except (FileNotFoundError, AttributeError) as e:
            log.error(f"File not found: {e}")

    def set_mp4_filepath(self) -> None:
        """Set the file path for the MP4 video output."""
        self.mp4_filepath = os.path.join(
            self.mp4_dirpath,
            f"zombie-outbreak-{self.country_code}-{self.locality}.mp4",
        )

    def set_gif_filepath(self) -> None:
        """Set the file path for the GIF output."""
        self.gif_filepath = os.path.join(
            self.gif_dirpath,
            f"zombie-outbreak-{self.country_code}-{self.locality}.gif",
        )

    def set_dispersion_rates(
        self, rates: list[float] = DEFAULT_DISPERSION_RATES
    ) -> None:
        """
        Set the dispersion rates for the SIR populations.

        Args:
            rates (list[float], optional): Dispersion rates
                (default DEFAULT_DISPERSION_RATES).
        """
        self.dispersion_rates = rates

    def set_dispersion_kernel(self) -> None:
        """
        Set the dispersion kernel for the simulation.

        The dispersion kernel models how individuals spread to neighboring positions.
        """
        self.dispersion_kernel: numpy.typing.NDArray[Any] = numpy.array(
            [[0.5, 1, 0.5], [1, -6, 1], [0.5, 1, 0.5]]
        )

    def set_hours_per_second(self, hours: int = DEFAULT_HOURS_PER_SECOND) -> None:
        """
        Set the number of hours in the model that equal one second in the video.

        Args:
            hours (int, optional): Hours per second (default DEFAULT_HOURS_PER_SECOND).
        """
        self.hours_per_second = hours

    def set_infection_rate(self, rate: float = DEFAULT_INFECTION_RATE) -> None:
        """
        Set the infection rate for the simulation.

        Args:
            rate (float, optional): Infection rate (default DEFAULT_INFECTION_RATE).
        """
        self.infection_rate = rate

    def set_incubation_rate(self, rate: float = DEFAULT_INFECTION_RATE) -> None:
        """
        Set the incubation rate for the simulation.

        Args:
            rate (float, optional): Incubation rate (default DEFAULT_INFECTION_RATE).
        """
        self.incubation_rate = rate

    def set_timestep(self, fraction: float = DEFAULT_TIMESTEP) -> None:
        """
        Set the time step for the simulation.

        Args:
            fraction (float, optional): Time step in hours (default DEFAULT_TIMESTEP).
        """
        self.timestep = fraction

    def set_world(self) -> None:
        """
        Build the initial world state for the zombie outbreak simulation.

        This method initializes the simulation world by:
        1. Loading and resizing a population density image.
        2. Setting up the modified SIR (Sane, Infected, Rampaging) array.
        3. Defining the initial evolution point.
        4. Returning the world dictionary containing the initial state.
        """
        # Load the image from the given file path and resize it to the specified width
        try:
            img = ImageClip(self.pdm_filepath).resize(width=self.width)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"PDM file not found: {self.pdm_filepath}") from e

        # Initialize a 3D NumPy array with zeros to hold the SIR model data
        # Dimensions: (3, height, width) corresponding to (S, I, R)
        sir: numpy.typing.NDArray[Any] = numpy.zeros((3, img.h, img.w), dtype=float)

        # Set the initial sane population based on the grayscale values of
        # the image. Normalize the grayscale values to be between 0 and 1.
        frame = img.get_frame(0)

        # Check the number of dimensions
        sir[0] = frame.mean(axis=2) / 255 if frame.ndim == 3 else frame / 255

        # Define the initial evolution starting point as specific coordinates in
        # the image.
        coord_x, coord_y = self.get_relative_px_coords()
        start = int(coord_y * img.h), int(coord_x * img.w)

        # Set the initial evolution level at the defined starting point
        # Here, DEFAULT_START_LEVEL (0.8) indicates a high level of evolution
        # at time t=0
        sir[1, start[0], start[1]] = DEFAULT_START_LEVEL

        # Create a dictionary to hold the world state, including the SIR array and
        # initial time.
        self.world = {"SIR": sir, "t": 0}

    def evolve(self) -> numpy.typing.NDArray[Any]:
        """
        Compute the evolution of the populations: (s)ane, (i)nfected, and (r)ampaging.

        This method calculates the changes in the sane (s), infected (i), and
        rampaging (r) populations based on the current state and the given infection
        and incubation rates.

        Args:
            sir (numpy.typing.NDArray[Any]): Current SIR populations.

        Returns:
            numpy.typing.NDArray[Any]: Updated SIR populations after evolution.
        """
        s, i, r = self.world["SIR"]

        # Calculate the number of newly infected.
        # i_new is the number of people moving from sane (s) to infected (i)
        # This is calculated as the product of the infection rate, the number of
        # rampaging (r) individuals, and the number of sane (s) individuals.
        i_new: float = self.infection_rate * r * s

        # Calculate the number of newly rampaging.
        # r_new is the number of people moving from infected (i) to rampaging (r)
        # This is calculated as the product of the incubation rate and the number of
        # infected (i) individuals.
        r_new: float = self.incubation_rate * i

        # Calculate the change in the sane population.
        # ds is the change in the sane (s) population, which decreases by the number of
        # newly infected.
        s_change = -i_new

        # Calculate the change in the infected population.
        # di is the change in the infected (i) population, which increases by the number
        # of newly infected and decreases by the number of newly rampaging individuals.
        i_change = i_new - r_new

        # Calculate the change in the rampaging population.
        # dr is the change in the rampaging (r) population, which increases by the
        # number of newly rampaging individuals.
        r_change = r_new

        # Return the changes in the populations as a numpy array.
        return numpy.array([s_change, i_change, r_change])

    def disperse(self) -> numpy.typing.NDArray[Any]:
        """
        Compute the dispersion (spread) of the s(ane), (i)nfected, and (r)ampaging.

        This method calculates the spread of the susceptible (s), infected (i), and
        rampaging (r) populations across neighboring positions based on the dispersion
        kernel and dispersion rates.

        Args:
            sir (numpy.typing.NDArray[Any]): Current SIR populations.

        Returns:
            numpy.typing.NDArray[Any]: Updated SIR populations after dispersion.
        """
        # Retrieve the current state of the populations from the world dictionary
        sir = self.world["SIR"]

        # Compute the dispersion for each population type (s, i, r).
        # The dispersion is calculated using convolution with the dispersion kernel.
        # Each population type has a different dispersion rate applied to the result of
        # the convolution.
        return numpy.array(
            [
                # Convolve the population array with the dispersion kernel and multiply
                # by the dispersion rate.
                # `strict=True` ensures equal length of sir and dispersion_rates.
                convolve(population, self.dispersion_kernel, cval=0) * dispersion_rate
                for (population, dispersion_rate) in zip(
                    sir, self.dispersion_rates, strict=True
                )
            ]
        )

    def update_world(self) -> None:
        """
        Update the world state by evolving and dispersing SIR populations.

        This method updates the state of the world by computing the evolution of the
        populations (sane, infected, rampaging) and their dispersion, then applying
        these changes over one time step.

        Returns:
            numpy.typing.NDArray[Any]: Updated SIR populations.
        """
        # Compute the evolution of the populations (sane, infected, rampaging).
        evolution = self.evolve()
        self.world["SIR"] += evolution * self.timestep

        # Compute the dispersion (spread) of the populations.
        dispersion = self.disperse()

        # Update the SIR populations by adding the changes due to evolution and
        # dispersion. The changes are scaled by the time step (self.timestep) to
        # simulate one time step.
        self.world["SIR"] += (evolution + dispersion) * self.timestep

        # Increment the simulation time by the time step.
        self.world["t"] += self.timestep

    def convert_map_to_rgb(self) -> numpy.typing.NDArray[Any]:
        """
        Convert SIR data to an RGB image for visualization.

        Returns:
            numpy.typing.NDArray[Any]: RGB image representation of SIR populations.
        """
        # Coefficients to accentuate the SIR populations for visualization.
        # These coefficients determine how strongly each population affects
        # the RGB channels.
        coefficients: numpy.ndarray[Any, numpy.dtype[Any]] = numpy.array(
            [2, 25, 25]
        ).reshape((3, 1, 1))

        # Accentuate the SIR populations for visualization by multiplying with the
        # coefficients and scaling by 255.
        accentuated_world = 255 * coefficients * self.world["SIR"]

        # Rearrange the axes to create an RGB image
        # - First reverse the order of the populations (so they map to RGB correctly)
        # - Then swap the axes to get the correct shape for the image
        #   (height, width, channels)
        image = accentuated_world[::-1].swapaxes(0, 2).swapaxes(0, 1)

        # Ensure the values are within the valid range for RGB images (0-255).
        return numpy.minimum(255, image)

    def get_frame_for_time(self, t: float) -> numpy.typing.NDArray[Any]:
        """
        Advance the simulation to a specified time and return the corresponding frame.

        Args:
            t (float): Time in seconds.

        Returns:
            numpy.typing.NDArray[Any]: RGB image representation of SIR populations
                at time t.
        """
        # Advance the simulation until world time reaches the specified video time t.
        while self.world["t"] < self.hours_per_second * t:
            self.update_world()

        # Convert the current state of the world to an RGB image.
        return self.convert_map_to_rgb()

    def get_clip_from_frame(self, duration: int = 25) -> VideoClip:
        """
        Generate a VideoClip object using frames produced by get_frame_for_time.

        Args:
            duration (int, optional): Duration of the clip in seconds (default 25).

        Returns:
            VideoClip: VideoClip object representing the outbreak animation.
        """
        return VideoClip(self.get_frame_for_time, duration=duration)

    def save_clip_as_gif(self, clip: VideoClip, filepath: str, fps: int = 15) -> None:
        """
        Save a VideoClip as a GIF file.

        Args:
            clip (VideoClip): The VideoClip object to be saved as a GIF.
            filepath (str): The filepath where the GIF will be saved.
            fps (int): Frames per second for the GIF (default 15).

        Returns:
            None
        """
        clip.write_gif(filepath, fps=fps)

    def save_clip_as_mp4(self, clip: VideoClip, filepath: str, fps: int = 15) -> None:
        """
        Save a VideoClip as an MP4 file.

        This method saves the given VideoClip as an MP4 file at the specified filepath.

        Args:
            clip (VideoClip): The VideoClip object to be saved as an MP4.
            filepath (str): The filepath where the MP4 will be saved.
            fps (int): Frames per second for the MP4 (default 15).

        Returns:
            None
        """
        clip.write_videofile(filepath, fps=fps)

    def get_img_size(self, filepath: str) -> tuple[int, int]:
        """
        Get the size of an image.

        Args:
            image_file_path (str): Path to the image file.

        Returns:
            tuple[int, int]: Width and height of the image.
        """
        img = Image.open(filepath)
        return img.size

    def convert_geo_to_px_coords(self) -> tuple[int, int]:
        """
        Convert geographical coordinates to pixel coordinates on the PDM.

        Args:
            geo_x (float): Geographical x-coordinate (latitude).
            geo_y (float): Geographical y-coordinate (longitude).
            img_x (float): Image width.
            img_y (float): Image height.

        Returns:
            tuple[float, float]: Pixel coordinates.
        """
        metadata = self.metadata_match(self.lat, self.lon)
        transform = metadata["transform"]

        # Extract the affine transformation parameters
        scale_factor_x = transform["scale-factor-x"]
        scale_factor_y = transform["scale-factor-y"]
        x_translation = transform["x-translation-term"]
        y_translation = transform["y-translation-term"]

        # Calculate the pixel coordinates
        px_coord_x = int((self.lon - x_translation) / scale_factor_x)
        px_coord_y = int((self.lat - y_translation) / scale_factor_y)

        return (px_coord_x, px_coord_y)

    def get_relative_px_coords(self) -> tuple[float, float]:
        """
        Convert geographical coordinates to relative pixel coordinates.

        This method is useful for setting the initial outbreak location on the map.

        Returns:
            tuple[float, float]: Relative pixel coordinates.
        """
        px_coord_x, px_coord_y = self.convert_geo_to_px_coords()
        img_w, img_h = self.get_img_size(self.pdm_filepath)

        return ((px_coord_x / img_w), (px_coord_y / img_h))


if __name__ == "__main__":
    data: list[dict[str, Any]] = load_json(
        os.path.join(os.getcwd(), "assets/data", "zombie-outbreak-localities.json")
    )
    example_data = {
        "locality": "canberra",
        "country_code": "au",
        "lat": -35.282,
        "lon": 149.128,
    }
    is_gif: bool = True
    force: bool = False
    try:
        zo = ZombieOutbreak(**example_data)
        zo.generate_animation(is_gif=is_gif, force=force)
    except Exception as e:
        log.error(f"Error occurred while generating animation: {e}")

    # i = 1
    # limit = 10
    # for d in data:
    #     item: dict[str, Any] = d
    #     if i <= limit:
    #         try:
    #             zo = ZombieOutbreak(**item)
    #             zo.generate_animation(is_gif=is_gif, force=force)
    #             i += 1
    #         except Exception as e:
    #             log.error(f"Error occurred while generating animation: {e}")
