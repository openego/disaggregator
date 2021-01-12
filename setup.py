import os
from setuptools import find_packages, setup

setup(
    name='disaggregator',
    packages=find_packages(),
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
                      'holidays']
)
