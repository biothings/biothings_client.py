import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="biothings_client",
    version="0.2.3",
    author="Cyrus Afrasiabi, Xinghua Zhou, Chunlei Wu",
    author_email="cwu@scripps.edu",
    description="Python Client for BioThings API services.",
    license="BSD",
    keywords="biology variant gene taxon species drug annotation web service client api myvariant mygene",
    url="https://github.com/biothings/biothings_client.py",
    packages=find_packages(),
    long_description=read('README.rst'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=[
        'requests>=2.3.0',
        'nose',
    ],
    extras_require={
        'dataframe': ["pandas>=0.18.0"],
        'caching': ["requests_cache>=0.4.13"],
        'jsonld': ["PyLD>=0.7.2"],
    }
)
