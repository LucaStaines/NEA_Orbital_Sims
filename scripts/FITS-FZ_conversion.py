from astropy.io import fits

input_file = r'downloaded lco data pathway'
output_file = r'output data pathway'

#Open the compressed MEF file#
hdul = fits.open(input_file)

data = hdul[1].data
header = hdul[1].header

#Check the shape#
print(f"Original data shape: {data.shape}")

#If 3D extract first layer#
if data.ndim == 3:
    data = data[0]
    print(f"Extracted 2D layer, new shape: {data.shape}")

#Save as 2D FITS#
fits.writeto(output_file, data, header, overwrite=True)
print(f"\nDone Saved to: {output_file}")

