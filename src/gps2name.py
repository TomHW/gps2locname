'''
Created on 12.11.2021
@summary: Find nearest known location (GeoName) from gps position

usage: gps2name <location.csv> <image_path>

location.csv is a country file containing locations and gps postions in csv format.
Download your csv file from http://download.geonames.org/export/dump/ and unzip it.

image_path is the directory with your image files (*.jpg). Please note that image file's
metadata is changed inplace. Before starting the script make a backup of your images!

If the image file contains a gps position and a nearest location is found, the following
tags will be created in the image's metadata:
- Iptc.Application2.Keywords
- Xmp.dc.subject 
- Xmp.digiKam.TagsList

@author: TomHW
'''
import sys
import sqlite3
import csv
import pyexiv2
from pathlib import Path

'''
Converts a position from Cardinal direction, degree, minute, second into decimal value
@param ref: Cardinal direction (N, S, W or E)
@param pos: List with degree, minute and second
@return: Decimal position value 
'''
def convposition(ref, pos):
    res = pos.value[0] + pos.value[1] / 60.0 + pos.value[2] / 3600.
    if(ref == 'S' or ref == 'W'):
        res *= -1
    return res

'''
Creates or updates dictionary entry in metadata for Exif, Iptc and Xmp tags
@param meta: Dictionary object
@param key: Dictionary key
@param value: New value for key
'''
def write_meta(meta, key, value):
    if(key in meta):
        meta[key] = value
    else:
        keytype = key.split('.')[0]
        if(keytype == 'Exif'):
            meta[key] = pyexiv2.ExifTag(key, value)
        elif(keytype == 'Iptc'):
            meta[key] = pyexiv2.IptcTag(key, value)
        elif(keytype == 'Xmp'):
            meta[key] = pyexiv2.XmpTag(key, value)

def main(argv):
    if(len(argv) < 1):
        sys.exit("Please pass the location file as a parameter!")

    # build location database with spatial column
    with sqlite3.connect(":memory:") as conn:
        conn.enable_load_extension(True)
        conn.load_extension("mod_spatialite")
        
        curR = conn.cursor()
        curR.execute('SELECT InitSpatialMetaData(1);')
        curR.execute('''CREATE TABLE location(
            geonameid         INTEGER PRIMARY KEY,
            name              varchar(200),
            lat               decimal,
            long              decimal
            )''')
        
        curR.execute('SELECT AddGeometryColumn("location", "point_geom", 4326, "POINT", 2)')
        conn.commit()

        with open(argv[0],'r') as fin:
            for record in csv.reader(fin, delimiter = '\t'):
                ins = "INSERT INTO location VALUES ({0}, '{1}', {2}, {3}, GeomFromText('POINT({4} {5})', 4326))".format(record[0], record[1].replace("'", "\""), record[4], record[5], record[4], record[5])
                curR.execute(ins)
        
        conn.commit()
        conn.execute('select CreateSpatialIndex("location", "point_geom");')
        conn.commit()

        # query database with gps positions        
        if(len(argv) > 1):
            # iterate over image files
            pathlist = Path(argv[1]).rglob('*.jpg')
            for path in pathlist:
                # because path is object not string
                path_in_str = str(path)
                metadata = pyexiv2.ImageMetadata(path_in_str)
                metadata.read()
                if('Exif.GPSInfo.GPSLatitudeRef' in metadata):
                    lat = convposition(metadata['Exif.GPSInfo.GPSLatitudeRef'], metadata['Exif.GPSInfo.GPSLatitude'])
                    long = convposition(metadata['Exif.GPSInfo.GPSLongitudeRef'], metadata['Exif.GPSInfo.GPSLongitude'])
            
                    cursor = conn.execute('''
                        SELECT geonameid, name, lat, long, ST_Distance(point_geom,
                        MakePoint(?, ?)) AS Distance
                        FROM location
                        WHERE distance < 0.1
                        ORDER BY distance LIMIT 1        
                        ''', (lat, long))
                    
                    for item in cursor:
                        print(path_in_str, item)
                        write_meta(metadata, 'Iptc.Application2.Keywords', ['Orte', item[1]])
                        write_meta(metadata, 'Xmp.dc.subject', ['Orte', item[1]])
                        write_meta(metadata, 'Xmp.digiKam.TagsList', ['Orte', 'Orte/' + item[1]])
                        metadata.write()

if __name__ == '__main__':
    main(sys.argv[1:])