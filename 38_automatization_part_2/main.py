from choose_parameters import getGribFileNames
from download_grib_files import download_gribs

filenames = getGribFileNames()

for filename in filenames:
    download_gribs(filename)

