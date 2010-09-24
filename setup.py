#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import cmsplugin_photologue
media_files = []

for dirpath, dirnames, filenames in os.walk('cmsplugin_photologue'):
    media_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    author="adamcupial",
    name='cmsplugin-photologue',
    version=cmsplugin_photologue.__version__,
    description='plugin bridge between django-cms & django-photologue',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.txt')).read(),
    url='http://github.com/adamcupial/cmsplugin-photologue',
    license='BSD License',
    platforms=['OS Independent'],
    requires=[
        'django (>=2.1.0)',
        'cms (>=1.2)',
    ],
    
    packages=find_packages(),
    package_dir={
        'cmsplugin_photologue': 'cmsplugin_photologue',
    },
    data_files = media_files,
    package_data = {
        'cmsplugin_photologue': [
            'templates/*.html',
            'locale/*.mo',
            'locale/*.po',
            'templates/plugins/cmsplugin_photologue/*.html',
        ],
    },
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],

)
