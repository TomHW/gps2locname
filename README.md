# gps2locname

Find nearest known location (GeoName) from gps position and add it to Iptc and Xmp image data.

I just wanted to populate my smartphone pictures with speaking names from the locations
were the pictures were taken. Then after import into a photo manager the pictures are already
tagged with location names. I know, there exist web services for GeoNames but I wanted to
perform geo naming offline.

## Installation

You need a python3 interpreter and some libs (sqlite3, pyexiv2, [mod_spatialite](http://www.gaia-gis.it/gaia-sins/)).
Download a country file from [GeoNames](http://download.geonames.org/export/dump/) that covers the region of your
pictures.

## Usage:

> `gps2name <location.csv> <image_path>`

- *location.csv* is a country file containing locations and gps postions in csv format.
Download your csv file from [GeoNames](http://download.geonames.org/export/dump/) and unzip it.

- *image_path* is the directory with your image files (*.jpg). Please note that image file's
metadata is changed inplace. Before starting the script make a backup of your images!

If the image file contains a gps position and a nearest location is found, the following
tags will be created in the image's metadata:
- Iptc.Application2.Keywords
- Xmp.dc.subject 
- Xmp.digiKam.TagsList
