from astropy.io import fits

#LCO site to MPC code mapping#
lco_codes = {
    'cpt': {'1m0': 'K91', '2m0': 'K92', '0m4': 'L09'},  #South Africa
    'coj': {'1m0': 'Q63', '2m0': 'Q64', '0m4': 'Q58'},  #Australia
    'lsc': {'1m0': 'W85', '2m0': 'W86', '0m4': 'W89'},  #Chile
    'elp': {'1m0': 'V37', '0m4': 'V38'},                 #Texas
    'tfn': {'1m0': 'Z31', '2m0': 'Z24', '0m4': 'Z17'},  #Tenerife
    'ogg': {'2m0': 'F65', '0m4': 'T03'},                 #Hawaii
}

#Change to your file path#
input_file = r'same pathway as the output data in FITS-FZ_conversion.py'

hdul = fits.open(input_file)
header = hdul[0].header

#Get site and telescope info#
site = header.get('SITEID', header.get('SITE', 'unknown')).lower()
telescope = header.get('TELESCOP', 'unknown')

#Extract telescope class#
tel_class = telescope.split('-')[0] if '-' in telescope else telescope

print(f"Site: {site}")
print(f"Telescope: {telescope}")
print(f"Telescope class: {tel_class}")

#Look up MPC code#
if site in lco_codes and tel_class in lco_codes[site]:
    mpc_code = lco_codes[site][tel_class]
    print(f"\nMPC Code: {mpc_code}")
else:
    print(f"\nCouldn't find code for {site} / {tel_class}")
