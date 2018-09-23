from setuptools import setup, find_packages
from os import path
from io import open

setup(
    name='conixsubscriber',  # Required
    version='0.0.1',  # Required
    description='Interface to a conix administrative domain on the subscriber side',  # Optional
    url='https://github.com/conix-center/smart-cities-demo/tree/master/client-library/subscriber/python/',  # Optional
    author='Joshua Adkins',  # Optional
    author_email='adkins@berkeley.edu',  # Optional
    keywords='sample setuptools development access control post sensor data',  # Optional
    packages=find_packages(exclude=['examples', 'docs', 'tests']),  # Required
    install_requires=['pint',
                      'aenum',
                      'wavemqtt'],  # Optional
    
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    #entry_points={  # Optional
    #    'console_scripts': [
    #        'conixpost=conixposter::main',
    #    ],
    #},
)
