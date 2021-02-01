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
                      'openpyxl'],
    package_data={
        "": ["*.csv", "*.xlsx"]}
)
