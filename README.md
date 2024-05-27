# Geo Simulations

Modelling scenarios with geographic data.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Generate](#generate)
- [License](#license)

## Prerequisites

You will need [`hatch`](https://hatch.pypa.io/latest/) as Python project manager.

### Population Density Map GeoTiffs

- [Germany](https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/DEU/deu_pd_2020_1km.tif)
- [Spain](https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/ESP/esp_pd_2020_1km.tif)
- [France](https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/FRA/fra_pd_2020_1km.tif)
- [Italy](https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/ITA/ita_pd_2020_1km.tif)

You can search for more on the Humanitarian Data Exchange website under [WorldPop - Population Density](https://data.humdata.org/m/dataset/?dataseries_name=WorldPop+-+Population+Density&res_format=GeoTIFF&q=&sort=last_modified+desc). Their GeoTiffs are generally licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode) license. [More about licenses](https://data.humdata.org/faqs/licenses).

## Installation

1. Clone the repository.

```shell
git clone https://github.com/sidisinsane/geo-simulations.git
```

2. Create the virtual environment.

```shell
hatch env create
```

## Setup

1. Copy `.env.template` to `.env` and modify the values for your environment.
2. Copy `localities.json.template` to `localities.json` and modify if you like.
3. Run setup.

```shell
hatch run setup
```

Running setup will convert all your GeoTiffs into PNGs, create the metadata file
and generate an examle MP4 from random data in `localities.json`.

## Generate

```shell
hatch run generate
```

Running generate will create “Zombie Outbreak“ MP4s for all localities set in `localities.json`.

## License

This project is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
