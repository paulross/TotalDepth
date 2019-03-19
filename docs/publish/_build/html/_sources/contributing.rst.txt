.. include:: ../../CONTRIBUTING.rst

Release Checklist
------------------------

In the following example the version we are moving to, in  ``Major.Minor.Patch`` format, is ``0.2.1``.

Current version should be something like ``M.m.(p)rcX``, for example ``0.2.1rc0``.

Increment version
~~~~~~~~~~~~~~~~~~~

Change the version to ``M.m.p`` in these places:

    * *setup.cfg*
    * *setup.py*
    * *src/TotalDepth/__init__.py*
    * /docs/source/conf.py (two places).

In *src/TotalDepth/__init__.py* change ``VERSION = (0, 2, 1)``

Update the history:

    * *HISTORY.rst*
    * *src/TotalDepth/__init__.py*

Update any Trove classifiers in *setup.py*, https://pypi.python.org/pypi?%3Aaction=list_classifiers

Build and Test
~~~~~~~~~~~~~~~~~~~

Build and test for Python 3.6:

.. code-block:: console

    $ . ~/venvs/TotalDepth_00/bin/activate
    (TotalDepth_00) $ python setup.py install
    (TotalDepth_00) $ python setup.py test

Build the docs HTML to test them, from an environment that has Sphinx:

.. code-block:: console

    (Sphinx) $ cd docs
    (Sphinx) $ make clean
    (Sphinx) $ make html

Commit and Tag
~~~~~~~~~~~~~~~~~~~

Commit, tag and push:

.. code-block:: console

    $ git add .
    $ git commit -m 'Release version 0.2.1'
    $ git tag -a v0.2.1 -m 'Version 0.2.1'
    $ git push
    $ git push origin v0.2.1

PyPi
~~~~~~~~~~~~~~~~~~~

Prepare release to PyPi for Python 3.6:

Build the egg and the source distribution:

.. code-block:: console

    (TotalDepth_00) $ python setup.py install sdist

Check the contents of ``dist/*``, unpack into ``tmp/`` if you want:

.. code-block:: console

    $ cp dist/* tmp/
    $ cd tmp/
    $ unzip TotalDepth-0.2.1-py3.6-macosx-10.6-intel.egg -d py27egg
    $ tar -xzf TotalDepth-0.2.1.tar.gz

Release to PyPi, https://pypi.python.org/pypi/TotalDepth:

.. code-block:: console

    (TotalDepth_00) $ twine upload dist/*

ReadTheDocs
~~~~~~~~~~~~~~~~~~~

Build the documentation: https://readthedocs.org/projects/TotalDepth/builds/

Prepare Next Release Candidate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally change the version to ``M.m.(p+1)rc0``, in this example ``0.2.2rc0`` in these places:

    * *setup.cfg*
    * *setup.py*
    * *src/TotalDepth/__init__.py*
    * /docs/source/conf.py (two places).

In *src/TotalDepth/__init__.py* change ``VERSION = (0, 2, 2, 'rc0')``

Commit and push:

.. code-block:: console

    $ git add .
    $ git commit -m 'Release candidate v0.2.2rc0'
    $ git push
