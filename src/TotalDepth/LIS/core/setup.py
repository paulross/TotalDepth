#!/usr/bin/env python
# Part of TotalDepth: Petrophysical data processing and presentation
# Copyright (C) 1999-2011 Paul Ross
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
# Paul Ross: apaulross@gmail.com
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# Usage: python3 setup.py build_ext --inplace
setup(
	cmdclass = {'build_ext': build_ext},
	ext_modules = [
			Extension("cRepCode", ["cRepCode.pyx"]),
			Extension("cFrameSet", ["cFrameSet.pyx"]),
			#Extension("StringIntConvert", ["StringIntConvert.pyx"]),
		]
)

#Output:
#W:\openLIS\src\TotalDepth.LIS\core>python setup.py build_ext --inplace
#running build_ext
#cythoning cRepCode.pyx to cRepCode.c
#building 'cRepCode' extension
#creating build
#creating build\temp.win32-3.1
#creating build\temp.win32-3.1\Release
#C:\Program Files\Microsoft Visual Studio 9.0\VC\BIN\cl.exe /c /nologo /Ox /MD /W3 /GS- /DNDEBUG -IC:\Python31\include -IC:\Python31\PC /TccRepCode.c /Fobuild\temp.win32-3.1\Release\cRepCode.obj cRepCode.c
#C:\Program Files\Microsoft Visual Studio 9.0\VC\BIN\link.exe /DLL /nologo /INCREMENTAL:NO /LIBPATH:C:\Python31\libs /LIBPATH:C:\Python31\PCbuild /EXPORT:PyInit_cRepCode build\temp.win32-3.1\Release\cRepCode.obj /OUT:W:\openLIS\src\TotalDepth.LIS\core\cRepCode.pyd /IMPLIB:build\temp.win32-3.1\Release\cRepCode.lib /MANIFESTFILE:build\temp.win32-3.1\Release\cRepCode.pyd.manifest
#   Creating library build\temp.win32-3.1\Release\cRepCode.lib and object build\temp.win32-3.1\Release\cRepCode.exp
#C:\Program Files\Microsoft SDKs\Windows\v6.0A\bin\mt.exe -nologo -manifest build\temp.win32-3.1\Release\cRepCode.pyd.manifest -outputresource:W:\openLIS\src\TotalDepth.LIS\core\cRepCode.pyd;2
#
#Paul-Rosss-MacBook-Pro:core paulross$ python3 setup.py build_ext --inplace
#running build_ext
#cythoning cRepCode.pyx to cRepCode.c
#building 'cRepCode' extension
#gcc-4.2 -fno-strict-aliasing -fno-common -dynamic -DNDEBUG -g -O3 -isysroot /Developer/SDKs/MacOSX10.6.sdk -arch i386 -arch x86_64 -isysroot /Developer/SDKs/MacOSX10.6.sdk -I/Library/Frameworks/Python.framework/Versions/3.2/include/python3.2m -c cRepCode.c -o build/temp.macosx-10.6-intel-3.2/cRepCode.o
#gcc-4.2 -bundle -undefined dynamic_lookup -arch i386 -arch x86_64 -isysroot /Developer/SDKs/MacOSX10.6.sdk -isysroot /Developer/SDKs/MacOSX10.6.sdk -g build/temp.macosx-10.6-intel-3.2/cRepCode.o -o /Users/paulross/Documents/workspace/TotalDepth.LIS/src/TotalDepth.LIS/core/cRepCode.so

