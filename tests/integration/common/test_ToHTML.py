import os

import pytest

from TotalDepth.common import ToHTML


def test_to_html_index_html_single_file(tmpdir):
    idx = ToHTML.IndexHTML(['A', 'B'])
    root = tmpdir.strpath
    idx.add(os.path.join(root, 'spam.html'), 'a', 'b')
    # print(idx)
    index_paths = idx.write_indexes(create_intermediate=True, class_style='CLASS', css='CSS')
    # print(index_paths)
    index_contents = []
    for index_path in index_paths:
        with open(index_path) as index_file:
            index_content = index_file.read()
            index_contents.append(index_content)
        # print(index_path)
        # print(index_content)
    assert len(index_contents) == 1
    assert index_contents[0] == """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="UTF-8"/>
    <title>IndexHTML of: &quot;index.html&quot;</title>
    <style>CSS</style>
  </head>
  <body>
    <table class="CLASS">
      <tr>
        <th class="CLASS" colspan="1">Path</th>
        <th class="CLASS">A</th>
        <th class="CLASS">B</th>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="spam.html">spam.html</a>
        </td>
        <td class="CLASS">a</td>
        <td class="CLASS">b</td>
      </tr>
    </table>
  </body>
</html>
"""


def test_to_html_index_html_two_file(tmpdir):
    idx = ToHTML.IndexHTML(['A', 'B'])
    root = tmpdir.strpath
    idx.add(os.path.join(root, 'spam/spam.html'), 'a', 'b')
    idx.add(os.path.join(root, 'eggs/eggs.html'), 'c', 'd')
    # print(idx)
    index_paths = idx.write_indexes(create_intermediate=True, class_style='CLASS', css='CSS')
    assert len(index_paths) == 3
    # for index_path in index_paths:
    #     print(index_path)
    index_contents = []
    # print()
    for index_path in index_paths:
        with open(index_path) as index_file:
            index_content = index_file.read()
            index_contents.append(index_content)
            # print(index_path)
            # print(index_content)
    assert len(index_contents) == 3
    expected = """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="UTF-8"/>
    <title>IndexHTML of: &quot;eggs/index.html&quot;</title>
    <style>CSS</style>
  </head>
  <body>
    <table class="CLASS">
      <tr>
        <th class="CLASS" colspan="2">Path</th>
        <th class="CLASS">A</th>
        <th class="CLASS">B</th>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="eggs.html">eggs.html</a>
        </td>
        <td class="CLASS">c</td>
        <td class="CLASS">d</td>
      </tr>
    </table>
  </body>
</html>
"""
    assert index_contents[0] == expected
    assert index_contents[1] == """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="UTF-8"/>
    <title>IndexHTML of: &quot;spam/index.html&quot;</title>
    <style>CSS</style>
  </head>
  <body>
    <table class="CLASS">
      <tr>
        <th class="CLASS" colspan="2">Path</th>
        <th class="CLASS">A</th>
        <th class="CLASS">B</th>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="spam.html">spam.html</a>
        </td>
        <td class="CLASS">a</td>
        <td class="CLASS">b</td>
      </tr>
    </table>
  </body>
</html>
"""
    assert index_contents[2] == """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="UTF-8"/>
    <title>IndexHTML of: &quot;index.html&quot;</title>
    <style>CSS</style>
  </head>
  <body>
    <table class="CLASS">
      <tr>
        <th class="CLASS" colspan="2">Path</th>
        <th class="CLASS">A</th>
        <th class="CLASS">B</th>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="eggs/index.html">eggs</a>
        </td>
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="eggs/eggs.html">eggs.html</a>
        </td>
        <td class="CLASS">c</td>
        <td class="CLASS">d</td>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="spam/index.html">spam</a>
        </td>
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="spam/spam.html">spam.html</a>
        </td>
        <td class="CLASS">a</td>
        <td class="CLASS">b</td>
      </tr>
    </table>
  </body>
</html>
"""


@pytest.mark.xfail(reason='To be investigated.')
def test_to_html_index_html_multiple_file_with_intermediate(tmpdir):
    idx = ToHTML.IndexHTML(['A', 'B'])
    root = tmpdir.strpath
    # W001557/Barrow_G68M_Transcribed_Log_Data/183318/Imported/Barrow-G68M_FILE_002.las.html
    idx.add(os.path.join(root, 'W001553/SALADIN_6ST1_MWD_1430_1700.LAS.html'), 'a', 'b')
    idx.add(os.path.join(root, 'W001557/Barrow_G68M_Transcribed_Log_Data/183318/Imported/Barrow-G68M_FILE_002.las.html'), 'c', 'd')
    idx.add(os.path.join(root, 'W001557/Barrow_G68M_Transcribed_Log_Data/183318/Imported/Barrow-G68M_FILE_003.las.html'), 'e', 'f')
    idx.add(os.path.join(root, 'W001557/Barrow_G68M_Transcribed_Log_Data/183318/Imported/Barrow-G68M_FILE_004.las.html'), 'g', 'h')
    # print(idx)
    index_paths = idx.write_indexes(create_intermediate=True, class_style='CLASS', css='CSS')
    for index_path in index_paths:
        print(index_path)
    assert len(index_paths) == 17
    index_contents = []
    # print()
    for index_path in index_paths:
        with open(index_path) as index_file:
            index_content = index_file.read()
            index_contents.append(index_content)
            # print(index_path)
            # print(index_content)
    assert len(index_contents) == 17
    assert index_contents[0] == """<?xml version='1.0' encoding="utf-8"?>"""


def test_to_html_index_html_two_file_no_intermediate(tmpdir):
    idx = ToHTML.IndexHTML(['A', 'B'])
    root = tmpdir.strpath
    idx.add(os.path.join(root, 'spam/spam.html'), 'a', 'b')
    idx.add(os.path.join(root, 'eggs/eggs.html'), 'c', 'd')
    # print(idx)
    index_paths = idx.write_indexes(create_intermediate=False, class_style='CLASS', css='CSS')
    assert len(index_paths) == 1
    # for index_path in index_paths:
    #     print(index_path)
    index_contents = []
    # print()
    for index_path in index_paths:
        with open(index_path) as index_file:
            index_content = index_file.read()
            index_contents.append(index_content)
            # print(index_path)
            # print(index_content)
    assert len(index_contents) == 1
    assert index_contents[0] == """<?xml version='1.0' encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="UTF-8"/>
    <title>IndexHTML of: &quot;index.html&quot;</title>
    <style>CSS</style>
  </head>
  <body>
    <table class="CLASS">
      <tr>
        <th class="CLASS" colspan="2">Path</th>
        <th class="CLASS">A</th>
        <th class="CLASS">B</th>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">eggs</td>
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="eggs/eggs.html">eggs.html</a>
        </td>
        <td class="CLASS">c</td>
        <td class="CLASS">d</td>
      </tr>
      <tr class="CLASS">
        <td class="CLASS" colspan="1" rowspan="1">spam</td>
        <td class="CLASS" colspan="1" rowspan="1">
          <a class="CLASS" href="spam/spam.html">spam.html</a>
        </td>
        <td class="CLASS">a</td>
        <td class="CLASS">b</td>
      </tr>
    </table>
  </body>
</html>
"""
