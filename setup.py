#!/usr/bin/python

# Copyright (C) 2012 Israel Herraiz Tabernero

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Authors : Israel Herraiz <israel.herraiz@upm.es>

"""
Installer

@author:       Israel Herraiz
@organization: Universidad Politecnica de Madrid
@copyright:    Universidad Politecnica de Madrid
@license:      
@contact:      israel.herraiz@upm.es
"""

from distutils.core import setup
from pymeasurer.version import measurer_version

setup(name = "Debian Measurer",
      version = measurer_version,
      author =  "Israel Herraiz",
      author_email = "israel.herraiz@upm.es",
      description = "Debian Measurer",
      long_description = "Measures the size of the source code files included in a Debian source package",
      license = "MIT license",
      url = "http://mat.caminos.upm.es/~iht/",
      platforms = ["any"],
      packages = ['pymeasurer'],
      scripts = ['debian-measurer'],
      install_requires = ['lockfile']
      )
