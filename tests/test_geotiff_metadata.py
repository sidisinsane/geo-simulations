import json
from unittest.mock import mock_open, patch

import pytest
import rasterio

from geo_simulations.geotiff_metadata import GeoTiffMetadata


@pytest.fixture
def geotiff_metadata():
    return GeoTiffMetadata()


def test_init(geotiff_metadata):
    assert isinstance(geotiff_metadata, GeoTiffMetadata)
    assert isinstance(geotiff_metadata.metadata, dict)


def test_metadata_get(geotiff_metadata):
    assert geotiff_metadata.metadata_get() == geotiff_metadata.metadata


def test_metadata_set(geotiff_metadata):
    mock_metadata = {"key1": {"dummy": "data"}}
    with patch.object(GeoTiffMetadata, "metadata_load", return_value=mock_metadata):
        geotiff_metadata.metadata_set()
        assert geotiff_metadata.metadata == mock_metadata


def test_metadata_match(geotiff_metadata):
    mock_metadata = {
        "key1": {"bbox": {"lat_min": 10, "lat_max": 20, "lon_min": 30, "lon_max": 40}},
        "key2": {"bbox": {"lat_min": -10, "lat_max": 0, "lon_min": -20, "lon_max": -10}},
    }
    geotiff_metadata.metadata = mock_metadata

    result = geotiff_metadata.metadata_match(15, 35)
    assert result == mock_metadata["key1"]

    result = geotiff_metadata.metadata_match(-5, -15)
    assert result == mock_metadata["key2"]

    result = geotiff_metadata.metadata_match(50, 50)
    assert result is None


@patch("geo_simulations.geotiff_metadata.glob.glob")
@patch("geo_simulations.geotiff_metadata.GeoTiffMetadata.metadata_load")
@patch("geo_simulations.geotiff_metadata.open", new_callable=mock_open)
def test_metadata_create(mock_open, mock_metadata_load, mock_glob, geotiff_metadata):
    mock_glob.return_value = ["test1.tif", "test2.tif"]
    mock_metadata_load.return_value = {}

    with patch.object(
        GeoTiffMetadata,
        "metadata_extract",
        side_effect=[
            {
                "file": "test1.tif",
                "bbox": {"lat_min": 0, "lat_max": 1, "lon_min": 0, "lon_max": 1},
            },
            {
                "file": "test2.tif",
                "bbox": {"lat_min": 1, "lat_max": 2, "lon_min": 1, "lon_max": 2},
            },
        ],
    ):
        geotiff_metadata.metadata_create()

        mock_open.assert_called_once_with(geotiff_metadata.geotiff_metadata_filepath, "w", encoding="utf-8")
        file_handle = mock_open()
        file_handle.write.assert_called_once()


def test_metadata_extract(geotiff_metadata):
    dummy_tif = "dummy.tif"

    with patch("rasterio.open") as mock_rasterio:
        mock_dataset = mock_rasterio.return_value.__enter__.return_value
        mock_dataset.dtypes = ["uint8"]
        mock_dataset.nodata = None
        mock_dataset.width = 100
        mock_dataset.height = 100
        mock_dataset.count = 1
        mock_dataset.crs = "EPSG:4326"
        mock_dataset.bounds = rasterio.coords.BoundingBox(0, 0, 100, 100)
        mock_dataset.transform = [1, 0, 0, 0, -1, 100]

        metadata = geotiff_metadata.metadata_extract(dummy_tif)

        assert metadata["file"] == dummy_tif
        assert metadata["dtype"] == "uint8"
        assert metadata["width"] == 100
        assert metadata["height"] == 100
        assert metadata["bands"] == 1
        assert metadata["crs"] == "EPSG:4326"
        assert metadata["bbox"] == {
            "lat_min": 0,
            "lat_max": 100,
            "lon_min": 0,
            "lon_max": 100,
        }
        assert metadata["transform"] == {
            "scale-factor-x": 1,
            "shear-y-component-x": 0,
            "x-translation-term": 0,
            "shear-x-component-y": 0,
            "scale-factor-y": -1,
            "y-translation-term": 100,
        }


@patch(
    "geo_simulations.geotiff_metadata.open",
    new_callable=mock_open,
    read_data='{"key1": {"dummy": "data"}}',
)
def test_metadata_load(mock_open, geotiff_metadata):
    metadata = geotiff_metadata.metadata_load()
    assert metadata == {"key1": {"dummy": "data"}}

    mock_open.side_effect = FileNotFoundError
    metadata = geotiff_metadata.metadata_load()
    assert metadata == {}

    mock_open.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    metadata = geotiff_metadata.metadata_load()
    assert metadata == {}
