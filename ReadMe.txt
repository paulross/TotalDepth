TotalDepth: Petrophysical data processing and presentation
Copyright (C) 1999-2012 Paul Ross

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

Alpha Release 2017-09-25
========================

This is a pre-release of TotalDepth.

Requirements
------------
Python 3, Cython, and numpy.

Installation
------------

$ pip install TotalDepth

This is the preferred method to install TotalDepth, as it will always install the most recent stable release. 

From sources
------------

First make a virtual environment in your <PYTHONVENVS, say ~/pyvenvs:

$ python3 -m venv <PYTHONVENVS>/TotalDepth
$ . <PYTHONVENVS>/TotalDepth/bin/activate
(TotalDepth) $

Install the dependencies, numpy and Cython:

(TotalDepth) $ pip install numpy
(TotalDepth) $ pip install Cython
    
The sources for TotalDepth can be downloaded from the Github repo.

You can either clone the public repository:

(TotalDepth) $ git clone git://github.com/paulross/TotalDepth.git

Or download the tarball:

(TotalDepth) $ curl  -OL https://github.com/paulross/TotalDepth/tarball/master

Once you have a copy of the source, you can install it with:

(TotalDepth) $ cd TotalDepth
(TotalDepth) $ python setup.py install

Install the test dependencies and run TotalDepth's tests:

(TotalDepth) $ pip install pytest
(TotalDepth) $ pip install pytest-runner
(TotalDepth) $ python setup.py test

See https://TotalDepth.readthedocs.io for the documentation.
