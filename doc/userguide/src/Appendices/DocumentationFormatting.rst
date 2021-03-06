.. _Documentation syntax:

Documentation formatting
------------------------

It is possible to use simple HTML formatting with `test suite`__,
`test case`__ and `user keyword`__ documentation and `free test suite
metadata`_ in the test data, as well as when `documenting test
libraries`__.  The formatting is similar to the style used in most
wikis, and it is designed to be understandable both as plain text and
after the HTML transformation.

__ `test suite documentation`_
__ `test case documentation`_
__ `user keyword documentation`_
__ `Documenting libraries`_

.. contents::
   :depth: 2
   :local:

Representing newlines
~~~~~~~~~~~~~~~~~~~~~

Adding newlines manually in test data
'''''''''''''''''''''''''''''''''''''

The documentation of test suites, test cases and keywords as well as
the test suite metadata are subject to `general parsing rules`__ of the
test data. This means that normal newlines are not preserved and
dividing documentation into lines and paragraphs generally requires
using a `literal newline character sequence`__ (:code:`\\n`). This is
shown in the example below.

__ `Test data syntax`_
__ `Handling whitespace`_

.. raw:: html

   <table class="example docutils">
     <caption>Adding newlines manually</caption>
     <tr>
       <th>Setting</th>
       <th>Value</th>
       <th>Value</th>
     </tr>
     <tr>
       <td>Documentation</td>
       <td>
         First line.\n<br>\n<br>
         Second paragraph, this time\n<br>with multiple lines.
       </td>
       <td>&nbsp;</td>
     </tr>
     <tr>
       <td>Metadata</td>
       <td>Example</td>
       <td>Value\n<br>in two lines</td>
     </tr>
   </table>

Automatic newlines in test data
'''''''''''''''''''''''''''''''

Adding newlines manually to a long documentation takes some effort and
extra characters also make the documentation in the test data slightly
harder to read. Starting from Robot Framework 2.7, this is not always
required as newlines are inserted automatically between `continued
documentation and metadata lines`__. In practice this means that the
above example could be written also as follows.

.. table:: Automatic newlines
   :class: example

   =============  ===========================
      Setting                Value
   =============  ===========================
   Documentation  First line.
   ...
   ...            Second paragraph, this time
   ...            with multiple lines.
   Metadata       Example
   ...            Value
   ...            in two lines
   =============  ===========================

This style works especially well in the `plain text format`_ where the
same example could be written like this::

  *** Settings ***
  Documentation
  ...    First line.
  ...
  ...    Second paragraph, this time
  ...    with multiple lines.
  Metadata
  ...    Example
  ...    Value
  ...    in two lines

No automatic newline is added if a line already ends with a newline or
if it ends with and an `escaping backslash`__. Notice also that if
documentation or metadata is defined in multiple cells in a same row,
these cells are catenated together with spaces. All these cases are
illustrated in the examples below where all test cases end up having
the same two line documentation.

__ `Dividing test data to several rows`_
__ Escaping_

.. table:: Multiline documentation examples
   :class: example

   =========  ===============  ================  ==============  ==============
   Test Case      Action           Argument         Argument       Argument
   =========  ===============  ================  ==============  ==============
   Example 1  [Documentation]  First line\\n     Second line in  multiple parts
   \          No Operation
   Example 2  [Documentation]  First line
   \          ...              Second line in    multiple parts
   \          No Operation
   Example 3  [Documentation]  First line\\n
   \          ...              Second line in\\
   \          ...              multiple parts
   \          No Operation
   =========  ===============  ================  ==============  ==============

Documentation in test libraries
'''''''''''''''''''''''''''''''

With library documentations normal newlines are enough, and for
example the following keyword documentation would create same end result
as the test suite documentation in the previous section.

.. sourcecode:: python

  def example_keyword():
      """First line.

      Second paragraph, this time
      with multiple lines.
      """
      pass


Paragraphs
~~~~~~~~~~

Starting from Robot Framework 2.7.2, all regular text in the formatted HTML
documentation is represented as paragraphs. In practice, lines separated
by a single newline will be combined in a paragraph regardless whether the
newline is added manually or automatically. Multiple paragraphs can be separated
with an empty line (i.e. two newlines) and also tables, lists, and other
specially formatted blocks discussed in subsequent sections end a paragraph.

For example, the following test suite or resource file documentation::

  *** Settings ***
  Documentation
  ...    First paragraph has only one line.
  ...
  ...    Second paragraph, this time created
  ...    with multiple lines.

will be formatted in HTML as:

.. raw:: html

  <div class="doc">
  <p>First paragraph has only one line.</p>
  <p>Second paragraph, this time created with multiple lines.</p>
  </div>

.. note:: Prior to 2.7.2 handling paragraphs was inconsistent. In documentation
          generated with libdoc_ lines were combined to paragraphs but in
          documentations shown in log and report they were not.

Bold and italic
~~~~~~~~~~~~~~~

Bold text can be created by having an asterisk before and after the
selected word or words, for example :code:`\*this is bold*`. Italic
style works similarly, but the special character to use is an
underscore, for example, :code:`\_italic_`. It is also possible to have
bold italic with the syntax :code:`\_*bold italic*_`.

An asterisk or an underscore alone, or in the middle of a word, does
not start formatting, but punctuation characters before or after them
are allowed. When multiple lines form a paragraph__, both bold and italic
can span over multiple lines.

__ paragraphs_

.. raw:: html

   <table class="tabular docutils">
     <caption>Bold and italic examples</caption>
     <tr>
       <th>Unformatted</th>
       <th>Formatted</th>
     </tr>
     <tr>
       <td>*bold*</td>
       <td><b>bold</b></td>
     </tr>
     <tr>
       <td>_italic_</td>
       <td><i>italic</i></td>
     </tr>
     <tr>
       <td>*bold* and then _italic_</td>
       <td><b>bold</b> and then <i>italic</i></td>
     </tr>
     <tr>
       <td>_*bold italic*_, _italic_, nothing</td>
       <td><i><b>bold italic</b></i>, <i>italic</i>, nothing</td>
     </tr>
     <tr>
       <td>This is *bold\n<br>on multiple\n<br>lines*.</td>
       <td>This is <b>bold</b><br><b>on multiple</b><br><b>lines</b>.</td>
     </tr>
   </table>

URLs
~~~~

All strings that look like URLs are automatically converted into
clickable links. Additionally, URLs that end with extension
:path:`.jpg`, :path:`.jpeg`, :path:`.png`, :path:`.gif` or
:path:`.bmp` (case-insensitive) will automatically create images. For
example, URLs like :code:`http://example.com` are turned into links, and
:code:`http:///host/image.jpg` and :code:`file:///path/chart.png`
into images.

The automatic conversion of URLs to links is applied to all the data
in logs and reports, but creating images is done only for test suite,
test case and keyword documentation, and for test suite metadata.

Custom links and images
~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.7, it is possible to create custom links
and embed images using special syntax :code:`[link|content]`. This creates
a link or image depending are :code:`link` and :code:`content` images.
They are considered images if they have the same image extensions that are
special with URLs_. The surrounding square brackets and the pipe character
between the parts are mandatory in all cases.

Link with text content
''''''''''''''''''''''

If neither :code:`link` nor :code:`content` is an image, the end result is
a normal link where :code:`link` is the link target and :code:`content`
the visible text::

    [file.html|this file] -> <a href="file.html">this file</a>
    [http://host|that host] -> <a href="http://host">that host</a>

Link with image content
'''''''''''''''''''''''

If :code:`content` is an image, you get a link where the link content is an
image. Link target is created by :code:`link` and it can be either text or image::

    [robot.html|robot.png] -> <a href="robot.html"><img src="robot.png"></a>
    [image.jpg|thumb.jpg] -> <a href="image.jpg"><img src="thumb.jpg"></a>

Image with title text
'''''''''''''''''''''

If :code:`link` is an image but :code:`content` is not, the syntax creates an
image where the :code:`content` is the title text shown when mouse is over
the image::

    [robot.jpeg|Robot rocks!] -> <img src="robot.jpeg" title="Robot rocks!">

Section titles
~~~~~~~~~~~~~~

If documentation gets longer, it is often a good idea to split it into
sections. Starting from Robot Framework 2.7.5, it is possible to separate
sections with titles using syntax :code:`= My Title =`, where the number of
equal signs denotes the level of the title::

    = First section =

    == Subsection ==

    Some text.

    == Second subsection ==

    More text.

    = Second section =

    You probably got the idea.

Notice that only three title levels are supported and that spaces between
equal signs and the title text are mandatory.

Tables
~~~~~~

Tables are created using the pipe character with whitespace around it
as a cell boundary and the possibly automatically added newline character
as a row separator::

   | *A* | *B*   | *C*   |
   | _1_ | Hello | world |
   | _2_ | Hi    |

The created table always has a thin border and the text is
left-aligned. Formatting using bold and italic works also in table
cells, so it is possible to create headers. Empty cells are automatically
added to make rows equally long. For example, the above
example would be formatted like this in HTML:

.. raw:: html

  <div class="doc">
  <table>
    <tr><td><b>A</b></td><td><b>B</b></td><td><b>C</b></td>
    <tr><td><i>1</i></td><td>Hello</td><td>world</td>
    <tr><td><i>2</i></td><td>Hi</td><td></td>
  </table>
  </div>

Lists
~~~~~

Lists are created by starting a line with a hyphen and space ('- '). List items
can be split into multiple lines by indenting continuing lines with one or more
spaces. A line that does not start with '- ' and is not indented ends the list::

  Example:
  - a list item
  - second list item
    is continued

  This is outside the list.

The above documentation is formatted like this in HTML:

.. raw:: html

  <div class="doc">
  <p>Example:</p>
  <ul>
    <li>a list item</li>
    <li>second list item is continued</li>
  </ul>
  <p>This is outside the list.</p>
  </div>

.. note:: Support for formatting lists was added in 2.7.2. Prior to that,
          the same syntax prevented :prog:`libdoc` from combining lines to
          paragraphs, so the end result was similar. Support for splitting
          list items into multiple lines was added in 2.7.4.

Preformatted text
~~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.7, it is possible to embed blocks of
preformatted text in the documentation. Preformatted block is created by
starting lines with '| ', one space being mandatory after the pipe character
except on otherwise empty lines. The starting '| ' sequence will be removed
from the resulting HTML, but all other whitespace is preserved.

In the following documentation, the two middle lines form a preformatted
block when converted to HTML::

  Doc before block:
  | inside block
  |    some   additional whitespace
  After block.

The above documentation is formatted like this:

.. raw:: html

  <div class="doc">
  <p>Doc before block:</p>
  <pre>inside block
    some   additional whitespace</pre>
  <p>After block.</p>
  </div>

Horizontal ruler
~~~~~~~~~~~~~~~~

Horizontal rulers (the <hr> tag) make it possible to separate larger
sections from each others, and they can be created by having three or more
hyphens alone on a line::

   Some text here.

   ---

   More text...

The above documentation is formatted like this:

.. raw:: html

  <div class="doc">
  <p>Some text here.</p>
  <hr>
  <p>More text...</p>
  </div>
