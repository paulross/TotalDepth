.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>


****************************
XML Writer Module
****************************

Introduction
===============

The important classes here are:

* ``XmlWrite.XMLStream`` (and derived classes): these manage the low level stream output.
* ``XmlWrite.XMLElement``: these handles opening and closing elements via the Context Manager. They require an initialised XMLStream in their constructor.

Together, if used correctly, these make writing output to a stream fluent in the code. They also make strong guarantees about the encoding and well-formedness of the result.

Reference
===========

.. automodule:: TotalDepth.util.XmlWrite
    :member-order: bysource
    :members:
    :special-members:

Examples
==========

All these examples assume these imports::

    import io
    from TotalDepth.util import XmlWrite

Creating an XML Stream
--------------------------

Create a file-like object and write to it using an ``XmlWrite.XmlStream``::

    myF = io.StringIO()
    with XmlWrite.XmlStream(myF):
        pass
    print(myF.getvalue())
    # Results in:
    <?xml version='1.0' encoding="utf-8"?>\n

Simple Elements
--------------------------

Create a file-like object and write elements to it using an ``XmlWrite.XmlElement``::

    myF = io.StringIO()
    with XmlWrite.XmlStream(myF) as xS:
        with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
            with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                pass
    print(myF.getvalue())
    # Results in:
    <?xml version='1.0' encoding="utf-8"?>
    <Root version="12.0">
        <A attr_1="1"/>
    </Root>


Mixed Content
---------------------

As above but writing text as well::

    myF = io.StringIO()
    with XmlWrite.XmlStream(myF) as xS:
        with XmlWrite.Element(xS, 'Root', {'version' : '12.0'}):
            with XmlWrite.Element(xS, 'A', {'attr_1' : '1'}):
                xS.characters('<&>')
    print(myF.getvalue())
    # Results in:
    <?xml version='1.0' encoding="utf-8"?>
    <Root version="12.0">
        <A attr_1="1">&lt;&amp;&gt;</A>
    </Root>




Testing
============

The unit tests are in :file:`test/TestWMLWrite.py`.

