import os
from contextlib import ExitStack
from unittest.mock import patch

import numpy
import pytest

from geo_simulations.geotiff_convert import GeoTiffConvert


@pytest.fixture
def geotiff_convert():
    return GeoTiffConvert()


def test_convert_all(geotiff_convert):
    with ExitStack() as stack:
        mock_glob = stack.enter_context(patch("geo_simulations.geotiff_convert.glob.glob"))
        mock_convert = stack.enter_context(patch("geo_simulations.geotiff_convert.GeoTiffConvert.convert"))

        mock_glob.return_value = ["test1.tif", "test2.tif"]

        geotiff_convert.convert_all()

        mock_glob.assert_called_once_with(os.path.join(geotiff_convert.geotiff_dirpath, "*.tif"))
        mock_convert.assert_called_once_with("test1.tif", mock_convert.return_value, 1, 255, 1.0, False)
        assert mock_convert.call_count == 2


def test_convert(geotiff_convert):
    with ExitStack() as stack:
        mock_makedirs = stack.enter_context(patch("geo_simulations.geotiff_convert.os.makedirs"))
        mock_rasterio = stack.enter_context(patch("geo_simulations.geotiff_convert.rasterio.open"))
        mock_image = stack.enter_context(patch("geo_simulations.geotiff_convert.Image.fromarray"))
        mock_save = stack.enter_context(patch("geo_simulations.geotiff_convert.Image.save"))

        mock_rasterio.return_value.__enter__.return_value.read.return_value = [
            [1, 2],
            [3, 4],
        ]

        geotiff_convert.convert("test.tif", "test.png", 0, 255, 1.0, False)

        mock_makedirs.assert_called_once()
        mock_image.assert_called_once_with([[255, 255], [255, 255]], mode="L")
        mock_save.assert_called_once_with("test.png")


def test_convert_with_nodata(geotiff_convert):
    with ExitStack() as stack:
        mock_open = stack.enter_context(patch("geo_simulations.geotiff_convert.rasterio.open"))
        mock_pil_image = stack.enter_context(patch("geo_simulations.geotiff_convert.Image"))
        mock_np_clip = stack.enter_context(patch("geo_simulations.geotiff_convert.numpy.clip"))
        mock_np_where = stack.enter_context(patch("geo_simulations.geotiff_convert.numpy.where"))

        mock_dataset = mock_open().__enter__.return_value
        mock_dataset.read.return_value = numpy.array([[1, 2], [3, 4]])
        mock_dataset.nodata = 0

        mock_np_clip.return_value = numpy.array([[1, 2], [3, 4]])
        mock_np_where.return_value = numpy.array([[1, 2], [3, 4]])

        geotiff_convert.convert_with_nodata("test.tif", "test.png", 0, 255, 1.0)

        mock_open.assert_called_once_with("test.tif")
        mock_np_where.assert_called_once_with(
            numpy.array([[1, 2], [3, 4]]) == 0, numpy.nan, numpy.array([[1, 2], [3, 4]])
        )
        mock_np_clip.assert_called_once_with(numpy.array([[1, 2], [3, 4]]), 0, 255)
        mock_pil_image.fromarray.assert_called_once_with(numpy.array([[1, 2], [3, 4]], dtype=numpy.uint8))
        mock_pil_image.fromarray.return_value.save.assert_called_once_with("test.png")


def test_convert_with_force(geotiff_convert):
    with ExitStack() as stack:
        mock_convert = stack.enter_context(patch("geo_simulations.geotiff_convert.GeoTiffConvert.convert"))

        geotiff_convert.convert("test.tif", "test.png", 0, 255, 1.0, True)

        mock_convert.assert_called_once_with("test.tif", "test.png", 0, 255, 1.0, True)
