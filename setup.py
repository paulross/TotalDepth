#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script.
copyright 2010-2020, Paul Ross
"""
import os
import sysconfig

from setuptools import Extension, setup, find_packages

COPYRIGHT = '2010-2020, Paul Ross'

# from Cython.Build import cythonize

# Mac OS:
# MACOSX_DEPLOYMENT_TARGET=10.9 CC=clang CXX=clang++ python setup.py develop

# Obtain TotalDepth.ENTRY_POINTS_CONSOLE_SCRIPTS as we can't import TotalDepth
with open(os.path.join('src', 'TotalDepth', '__init__.py')) as init_file:
    code = compile(init_file.read(), __file__, 'exec')
    exec(code)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

install_requirements = [
    'Cython',
    'numpy',
    'lxml',
    'colorama',
    'psutil',
]

setup_requirements = [
    'setuptools>=18.0',
    'Cython',
    'wheel',
    'pytest-runner',
]

test_requirements = [
    'pytest',
    'asv',
]

XML_FORMAT_FILES = [
    'src/TotalDepth/util/plot/formats/Azimuthal_Density_3Track.xml',
    'src/TotalDepth/util/plot/formats/Azimuthal_Density_Image.xml',
    'src/TotalDepth/util/plot/formats/Azimuthal_Resistivity_3Track.xml',
    'src/TotalDepth/util/plot/formats/Blank_3Track_Depth.xml',
    'src/TotalDepth/util/plot/formats/Blank_3Track_Time.xml',
    'src/TotalDepth/util/plot/formats/Formation_Micro_Image_Aligned.xml',
    'src/TotalDepth/util/plot/formats/Formation_Micro_Image_Processed.xml',
    'src/TotalDepth/util/plot/formats/Formation_Test_Time.xml',
    'src/TotalDepth/util/plot/formats/HDT.xml',
    'src/TotalDepth/util/plot/formats/Micro_Resistivity_3Track.xml',
    'src/TotalDepth/util/plot/formats/Natural_GR_Spectrometry_3Track.xml',
    'src/TotalDepth/util/plot/formats/OilBaseMicroImager_Equalized.xml',
    'src/TotalDepth/util/plot/formats/Porosity_GR_3Track.xml',
    'src/TotalDepth/util/plot/formats/Pulsed_Neutron_3Track.xml',
    'src/TotalDepth/util/plot/formats/Pulsed_Neutron_Time.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_3Track_Correlation.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_3Track_Logrithmic.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_Porosity_GR_3Track.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_Radial_Investigation_Image.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_at_the_Bit.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_at_the_bit_deep_image.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_at_the_bit_medium_image.xml',
    'src/TotalDepth/util/plot/formats/Resistivity_at_the_bit_shallow_image.xml',
    'src/TotalDepth/util/plot/formats/Sonic_3Track.xml',
    'src/TotalDepth/util/plot/formats/Sonic_LowerDipole_VDL.xml',
    'src/TotalDepth/util/plot/formats/Sonic_P_S_VDL.xml',
    'src/TotalDepth/util/plot/formats/Sonic_Stonely_VDL.xml',
    'src/TotalDepth/util/plot/formats/Sonic_UpperDipole_VDL.xml',
    'src/TotalDepth/util/plot/formats/Sonic_Waveform4_Depth.xml',
]

XML_FORMAT_FILES = [os.path.join(*p.split('/')) for p in XML_FORMAT_FILES]

# ext_modules = cythonize(
#     module_list="src/TotalDepth/LIS/core/*.pyx",
# )

extra_compile_args = []
cflags = sysconfig.get_config_var('CFLAGS')
if cflags != None:
    extra_compile_args = sysconfig.get_config_var('CFLAGS').split()

ext_modules = [
    Extension(
        "TotalDepth.LIS.core.cRepCode",
        sources=[
            "src/TotalDepth/LIS/core/src/cython/cRepCode.pyx",
        ]
    ),
    Extension(
        "TotalDepth.LIS.core.cFrameSet",
        sources=[
            "src/TotalDepth/LIS/core/src/cython/cFrameSet.pyx",
        ]
    ),
    Extension(
        "TotalDepth.LIS.core.cpRepCode",
        sources=[
            "src/TotalDepth/LIS/core/src/cp/cpLISRepCode.cpp",
            "src/TotalDepth/LIS/core/src/cpp/LISRepCode.cpp",
        ],
        extra_compile_args=extra_compile_args + [
            "-Isrc/TotalDepth/LIS/core/src/cp/",
            "-Isrc/TotalDepth/LIS/core/src/cpp/",
            '-std=c++14',
        ],
    ),
]


setup(
    name='TotalDepth',
    version='0.3.2',
    description="TotalDepth is a software collection that can process petrophysical data such as wireline logs and seismic data.",
    long_description=readme + '\n\n' + history,
    author="Paul Ross",
    author_email='apaulross@gmail.com',
    url='https://github.com/paulross/TotalDepth',
    packages=find_packages('src'),
    package_dir={'' : 'src'},
    # package_data={'' : ['TotalDepth/util/plot/formats/*.xml']},
    data_files= [
        (os.path.join('TotalDepth', 'util', 'plot', 'formats'), XML_FORMAT_FILES),
    ],
    entry_points={
        'console_scripts': ENTRY_POINTS_CONSOLE_SCRIPTS,
    },
    include_package_data=True,
    license="GPLv2",
    zip_safe=False,
    keywords='TotalDepth',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    setup_requires=setup_requirements,
    install_requires=install_requirements,
    tests_require=test_requirements,
    # cmdclass = {'build_ext': build_ext},
    ext_modules=ext_modules
)
