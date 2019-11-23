"""
Imports the best XML libraries as etree.
Modified from: https://lxml.de/tutorial.html
"""
try:
    from lxml import etree
    # print("running with lxml.etree")
except ImportError:  # pragma: no cover
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        # print("running with cElementTree on Python 2.5+")
    except ImportError:  # pragma: no cover
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            # print("running with ElementTree on Python 2.5+")
        except ImportError:  # pragma: no cover
            try:
                # normal cElementTree install
                import cElementTree as etree
                # print("running with cElementTree")
            except ImportError:  # pragma: no cover
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    # print("running with ElementTree")
                except ImportError:  # pragma: no cover
                    print("Failed to import ElementTree from any known place")
                    raise
