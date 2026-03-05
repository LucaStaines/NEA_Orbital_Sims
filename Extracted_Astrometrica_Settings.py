from astropy.io import fits
import numpy as np

#Maps LCO filter codes to Astrometrica filters#
LCO_FILTER_MAP = {
    'gp':  'g (Sloan)',
    'rp':  'r (Sloan)',
    'ip':  'i (Sloan)',
    'zs':  'z (Sloan)',
    'w':   'Clear/None',
    'V':   'V (Johnson)',
    'B':   'B (Johnson)',
    'R':   'R (Cousins)',
    'I':   'I (Cousins)',
    'up':  'u (Sloan)',
    'Y':   'Y',
}

#Maps LCO instrument to pixel sizes#
LCO_INSTRUMENTS = {
    'fa':   {'pixel_um': 15.0, 'name': 'Sinistro (1m)'},
    'fs':   {'pixel_um': 15.0, 'name': 'Spectral (2m)'},
    'kb':   {'pixel_um': 6.8,  'name': 'SBIG (0.4m)'},
    'ef':   {'pixel_um': 9.0,  'name': 'MuSCAT3 (2m)'},
    'sq':   {'pixel_um': 9.0,  'name': 'QHY600 (0.4m)'},
}

#Maps LCO site to MPC codes#
#Up to date as of /03/2026#
#Codes can be changed or new codes added so check against: https://www.minorplanetcenter.net/iau/lists/ObsCodesF.html#
LCO_MPC_CODES = {
    ('coj', '2m0'): 'Q63',   #Siding Spring, Australia#
    ('coj', '1m0'): 'Q64',
    ('coj', '0m4'): 'Q58',
    ('cpt', '1m0'): 'L09',   #Sutherland, South Africa#
    ('cpt', '0m4'): 'L06',
    ('tfn', '2m0'): 'Z17',   #Tenerife, Spain#
    ('tfn', '1m0'): 'Z31',
    ('tfn', '0m4'): 'Z21',
    ('lsc', '1m0'): 'W86',   #Cerro Tololo, Chile#
    ('lsc', '0m4'): 'W85',
    ('elp', '1m0'): 'V37',   #McDonald, Texas#
    ('elp', '0m4'): 'V39',
    ('ogg', '2m0'): 'T04',   #Haleakala, Maui#
    ('ogg', '0m4'): 'T03',
}


def extract_astrometrica_settings(fits_file):
    with fits.open(fits_file) as hdul:
        header = hdul[0].header if hdul[0].data is not None else hdul[1].header

        settings = {}

        #OBSERVATION TIME#
        
        settings['date_obs'] = header.get('DATE-OBS', None)
        settings['exptime'] = header.get('EXPTIME', None)

        #FILTER#
       
        raw_filter = header.get('FILTER', None)
        settings['raw_filter'] = raw_filter
        settings['filter'] = LCO_FILTER_MAP.get(raw_filter, f'UNKNOWN ({raw_filter})')

        #TELESCOPE ID#
        
        settings['telescope'] = header.get('TELESCOP', None)
        settings['instrument'] = header.get('INSTRUME', None)
        settings['site'] = header.get('SITEID', None) or header.get('SITE', None)

        #MPC CODE#
        
        if settings['site'] and settings['telescope']:
            site = settings['site'].lower()
            tel_class = settings['telescope'].split('-')[0]
            settings['mpc_code'] = LCO_MPC_CODES.get(
                (site, tel_class), f"UNKNOWN ({site}, {tel_class})"
            )
        else:
            settings['mpc_code'] = 'UNKNOWN'

        #FOCAL LENGTH#
        
        settings['focal_length'] = header.get('FOCALLEN', None)

        #PIXEL SIZE#
    
        settings['pixscale'] = header.get('PIXSCALE', None)
        
        if settings['instrument']:
            inst_id = settings['instrument'][:2].lower()
            if inst_id in LCO_INSTRUMENTS:
                settings['pixel_size_um'] = LCO_INSTRUMENTS[inst_id]['pixel_um']
                settings['instrument_name'] = LCO_INSTRUMENTS[inst_id]['name']

        #If the pixle size can't be found it will be calculated#
        if 'pixel_size_um' not in settings and settings['focal_length'] and settings['pixscale']:
            pixscale_rad = settings['pixscale'] / 206265.0
            pixel_size_mm = settings['focal_length'] * np.tan(pixscale_rad)
            settings['pixel_size_um'] = round(pixel_size_mm * 1000, 2)

        #SATURATION#
        
        settings['saturation'] = header.get('SATURATE', None) or header.get('MAXLIN', None)

        #POSITION ANGLE & FLIPS#
        #This will change slightly if u are using this code on multiple images from the same group and telescope but Astrometrica handles the small variations#
        if 'CROTA2' in header:
            settings['position_angle'] = round(header['CROTA2'], 2)
        elif 'CD1_1' in header:
            cd1_1 = header['CD1_1']
            cd1_2 = header['CD1_2']
            cd2_1 = header['CD2_1']
            cd2_2 = header['CD2_2']

            settings['position_angle'] = round(
                np.degrees(np.arctan2(cd1_2, cd2_2)), 2
            )
            
            det = cd1_1 * cd2_2 - cd1_2 * cd2_1
            settings['flip_horizontal'] = det > 0

        #OBSERVATORY LOCATION#
        
        settings['longitude'] = header.get('LONGITUD', None)
        settings['latitude'] = header.get('LATITUDE', None)
        settings['height'] = header.get('HEIGHT', None) or header.get('ALTITUDE', None)

        #APERTURE#
        settings['aperture'] = header.get('APTDIA', None) or header.get('APERTURE', None)

        #IMAGE DIMENSIONS#
        settings['naxis1'] = header.get('NAXIS1', None)
        settings['naxis2'] = header.get('NAXIS2', None)

        return settings


def print_astrometrica_settings(s):

    print("=" * 60)
    print("COPY THESE VALUES INTO ASTROMETRICA")
    print("=" * 60)

    print("\n LOCATION")
    print(f"  MPC Code:        {s.get('mpc_code', '???')}")
    lon = s.get('longitude', None)
    if lon is not None:
        direction = 'West' if lon < 0 else 'East'
        print(f"  Longitude:       {abs(lon):.4f}  {direction}")
    lat = s.get('latitude', None)
    if lat is not None:
        direction = 'South' if lat < 0 else 'North'
        print(f"  Latitude:        {abs(lat):.4f}  {direction}")
    print(f"  Height:          {s.get('height', '???')} m")

    print("\n SCALE AND ORIENTATION")
    print(f"  Focal Length:    {s.get('focal_length', '???')} mm")
    print(f"  Position Angle:  {s.get('position_angle', '???')}°")
    flip_h = s.get('flip_horizontal', False)
    print(f"  Flip Horizontal: {'Yes' if flip_h else 'No'}")

    print("\n CCD CHIP")
    print(f"  Pixel Width:     {s.get('pixel_size_um', '???')} μm")
    print(f"  Pixel Height:    {s.get('pixel_size_um', '???')} μm")
    print(f"  Saturation:      {s.get('saturation', '???')}")

    print("\n FILTER")
    print(f"  Filter:          {s.get('filter', '???')}")

    if s.get('aperture'):
        print("\n TELESCOPE")
        print(f"  Aperture:        {s['aperture']} m")

    print("\n GENERAL INFO NOT SETTINGS")
    print(f"  Telescope:       {s.get('telescope', '???')}")
    print(f"  Instrument:      {s.get('instrument_name', s.get('instrument', '???'))}")
    print(f"  Site:            {s.get('site', '???')}")
    print(f"  DATE-OBS:        {s.get('date_obs', '???')}")
    print(f"  Exposure:        {s.get('exptime', '???')} seconds")
    print(f"  Pixel Scale:     {s.get('pixscale', '???')} arcsec/px")
    print(f"  Image Size:      {s.get('naxis1','?')} x {s.get('naxis2','?')}")
    print("=" * 60)

#Add your own path to as many images as needed#
if __name__ == '__main__':
    test_files = [
        r"C:\Users\lucas\Downloads\eros_60s-expos_converted_2d_image_1.fits",
       # r"\path\to\image2.fits",
       # r"\path\to\image3.fits",
    ]
    
    for f in test_files:
        print(f"\nFile: {f}")
        settings = extract_astrometrica_settings(f)
        print_astrometrica_settings(settings)
