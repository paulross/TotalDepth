==========
TotalDepth
==========

.. image:: https://img.shields.io/pypi/v/TotalDepth.svg
        :target: https://pypi.python.org/pypi/TotalDepth

.. image:: https://img.shields.io/travis/paulross/TotalDepth.svg
        :target: https://travis-ci.org/paulross/TotalDepth

.. image:: https://readthedocs.org/projects/TotalDepth/badge/?version=latest
        :target: https://TotalDepth.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/paulross/TotalDepth/shield.svg
     :target: https://pyup.io/repos/github/paulross/TotalDepth/
     :alt: Updates

Petrophysical software capable of processing wireline logs.

* Free software: GPL 2.0
* Documentation: https://TotalDepth.readthedocs.io

Features
--------

* Reads LIS, LAS (1.2, 2.0) file formats for analysis or conversion to other formats.
* Plots log data as SVG viewable in any modern browser.
* Plots can be made with a wide variety of plot formats.
* TotalDepth can generate HTML summaries of log data.
* TotalDepth is written in Python so it is fast to develop with.
* Special indexing techniques are used to be able to randomly access sequential files.

Here is an example of a LAS file plotted with the Tripple Combo plot format as seen in a browser, this includes the API header:

.. image:: images/TrippleCombo.png
        :alt: Tripple Combo

An example of a High Resolution Dipmeter plotted at 1:25 scale:

.. image:: images/HDT_25_no_hdr.png
        :alt: High Resolution Dipmeter

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

