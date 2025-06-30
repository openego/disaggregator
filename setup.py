# Manually added setup file not shipped in the original version

import os
from setuptools import find_packages, setup

setup(
    name='disaggregator',
    packages= ['disaggregator'],
    include_package_data=True,
    install_requires=['numpy',
                      'pandas',
                      'tables',
                      'pyyaml',
                      'requests',
                      'geopandas',
                      'descartes',
                      'xarray',
                      'xlrd',
                      'matplotlib',
                      'holidays',
                      'openpyxl==3.1.0',
                      'ruamel.yaml<0.18.0'],
    package_data={
        "": ["*.csv", "*.xlsx"]}
)
