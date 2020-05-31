========
jxl2txt
========

jxl2txt is a Python script to convert Trimble JobXML files to various kinds of text using XSLT stylesheets.

.. image:: https://travis-ci.org/mrahnis/jxl2txt.svg?branch=master
    :target: https://travis-ci.org/mrahnis/jxl2txt

.. image:: https://ci.appveyor.com/api/projects/status/9st7tu5v9hhlg306?svg=true
	:target: https://ci.appveyor.com/project/mrahnis/jxl2txt

.. image:: https://github.com/mrahnis/jxl2txt/workflows/Python%20package/badge.svg
	:target: https://github.com/mrahnis/jxl2txt/actions?query=workflow%3A%22Python+package%22
	:alt: Python Package

.. image:: https://readthedocs.org/projects/jxl2txt/badge/?version=latest
	:target: http://jxl2txt.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

Installation
============

.. image:: https://img.shields.io/pypi/v/jxl2txt.svg
	:target: https://pypi.python.org/pypi/jxl2txt/

.. image:: https://anaconda.org/mrahnis/jxl2txt/badges/version.svg
	:target: https://anaconda.org/mrahnis/jxl2txt

To install from the Python Package Index:

	$pip install jxl2txt

To install from Anaconda Cloud:

If you are starting from scratch the first thing to do is install the Anaconda Python distribution, add the necessary channels to obtain the dependencies and install jxl2txt.

.. code-block:: console

	$conda config --append channels conda-forge
	$conda install jxl2txt -c mrahnis

To install from the source distribution execute the setup script in the jxl2txt directory:

	$python setup.py install

Examples
========

To do

License
=======

BSD

Documentation
=============

Latest `html`_

.. _`Python 2.7 or 3.x`: http://www.python.org
.. _lxml: http://lxml.de
.. _Click: http://click.pocoo.org

.. _html: http://jxl2xml.readthedocs.org/en/latest/