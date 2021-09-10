TotalDepth: Petrophysical data processing and presentation
Copyright (C) 1999-2021 Paul Ross

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Paul Ross: apaulross@gmail.com

TotalDepth: Petrophysical data processing and presentation

This is a pre-release of TotalDepth.

Requirements
------------
Python3, Cython, and numpy.

Installation
------------

From PyPi:

$ pip install TotalDepth

This is the preferred method to install TotalDepth, as it will always install the most recent stable release. 

From sources
------------

The sources for TotalDepth can be downloaded from the Github repo.

You can either clone the public repository:

(TotalDepth) $ git clone git://github.com/paulross/TotalDepth.git

Or download the tarball:

(TotalDepth) $ curl  -OL https://github.com/paulross/TotalDepth/tarball/master

Make a virtual environment in your <PYTHONVENVS, say ~/pyvenvs:

$ python3 -m venv <PYTHONVENVS>/TotalDepth
$ . <PYTHONVENVS>/TotalDepth/bin/activate
(TotalDepth) $

Install the dependencies, numpy and Cython:

(TotalDepth) $ pip install -r requirements.txt

Install TotalDepth with:

(TotalDepth) $ cd TotalDepth
(TotalDepth) $ python setup.py install

Install the test dependencies and run TotalDepth's tests:

(TotalDepth) $ pip install -r requirements-dev.txt
(TotalDepth) $ python setup.py test

See https://totaldepth.readthedocs.io/en/latest/index.html for the documentation.
