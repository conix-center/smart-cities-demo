from setuptools import setup, find_packages
from os import path
from io import open

setup(
    name='wavemqtt',  # Required
    version='0.0.3',  # Required
    description='A client for wave-mqtt integration',  # Optional
    url='https://github.com/conix-center/smart-cities-demo/tree/master/wave/mqtt-client/python/wavemqtt',  # Optional
    author='Gabe Fierro',  # Optional
    author_email='gtfierro@cs.berkeley.edu',  # Optional
    keywords='wave mqtt access control entity',  # Optional
    packages=find_packages(exclude=['examples', 'docs', 'tests']),  # Required
    install_requires = ['grpcio',
                            'paho-mqtt'],

    #dependency_links = ['git://github.com/immesys/pywave#egg=wave3'],
)
