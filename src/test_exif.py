'''
Created on 13.11.2021

@author: sesth
'''
import sys
import PIL.Image
import PIL.IptcImagePlugin
import PIL.ExifTags
import pyexiv2

def convposition(ref, pos):
    res = 0
    print(pos)
    res = pos.value[0] + pos.value[1] / 60.0 + pos.value[2] / 3600.
    if(ref == 'S' or ref == 'W'):
        res *= -1
    return res

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
        sys.exit("Bitte Bildatei als Parameter Übergeben!")
    
    print(argv[0])
    metadata = pyexiv2.ImageMetadata(argv[0])
    metadata.read()
    lat = convposition(metadata['Exif.GPSInfo.GPSLatitudeRef'], metadata['Exif.GPSInfo.GPSLatitude'])
    long = convposition(metadata['Exif.GPSInfo.GPSLongitudeRef'], metadata['Exif.GPSInfo.GPSLongitude'])
    print(lat, long)

    for k in metadata.iptc_keys:
        print(k, metadata[k] )
    
    for k in metadata.xmp_keys:
        print(k, metadata[k] )
    
    write_meta(metadata, 'Iptc.Application2.Keywords', ['Orte', 'mein Testort'])
    write_meta(metadata, 'Xmp.dc.subject', ['Orte', 'mein Testort'])
    write_meta(metadata, 'Xmp.digiKam.TagsList', ['Orte', 'Orte/mein Testort'])
    metadata.write()

if __name__ == '__main__':
    main(sys.argv[1:])