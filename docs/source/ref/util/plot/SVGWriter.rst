.. moduleauthor:: Paul Ross <apaulross@gmail.com>
.. sectionauthor:: Paul Ross <apaulross@gmail.com>

****************************
SVG Writer Module
****************************


.. automodule:: TotalDepth.util.plot.SVGWriter
	:members:
	:special-members:

Examples
===================

All these examples assume these imports::

    import io
    from TotalDepth.util import XmlWrite
    from TotalDepth.util.plot import SVGWriter
    from TotalDepth.util.plot import Coord

Construction
--------------------------------

Writing to an in-memory file::

    f = io.StringIO()
    vp = Coord.Box(
        Coord.Dim(100, 'mm'),
        Coord.Dim(20, 'mm'),
    )
    with SVGWriter.SVGWriter(myF, myViewPort):
        pass
    print(myF.getvalue())
    # Prints:
    <?xml version='1.0' encoding="utf-8"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg height="20.000mm" version="1.1" width="100.000mm" xmlns="http://www.w3.org/2000/svg"/>

Writing Objects to SVG
--------------------------

Writing a rectangles to a stream::

    myF = io.StringIO()
    vp = Coord.Box(Coord.Dim(5, 'cm'), Coord.Dim(4, 'cm'))
    with SVGWriter.SVGWriter(myF, vp) as xS:
        with XmlWrite.Element(xS, 'desc'):
            xS.characters('A couple of rectangles')
        myPt = Coord.Pt(Coord.Dim(0.5, 'cm'), Coord.Dim(0.5, 'cm'))
        myBx = Coord.Box(Coord.Dim(2.0, 'cm'), Coord.Dim(1.0, 'cm'))
        with SVGWriter.SVGRect(xS, myPt, myBx):
            pass
        myPt = Coord.Pt(Coord.Dim(0.01, 'cm'), Coord.Dim(0.01, 'cm'))
        myBx = Coord.Box(Coord.Dim(4.98, 'cm'), Coord.Dim(3.98, 'cm'))
        with SVGWriter.SVGRect(xS, myPt, myBx, attrs= {'fill' : "none", 'stroke' : "blue", 'stroke-width' : ".02cm"}):
            pass
    print(myF.getvalue())
    # Prints:
    <?xml version='1.0' encoding="utf-8"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg height="4.000cm" version="1.1" width="5.000cm" xmlns="http://www.w3.org/2000/svg">
        <desc>A couple of rectangles</desc>
        <rect height="1.000cm" width="2.000cm" x="0.500cm" y="0.500cm"/>
        <rect fill="none" height="3.980cm" stroke="blue" stroke-width=".02cm" width="4.980cm" x="0.010cm" y="0.010cm"/>
    </svg>
