#!/usr/bin/env python
# coding: utf-8

"""
    html2jira unittest
    ~~~~~~~~~~~~~~~~~~~~~
    
    Unittests for special cases which only works in the html2jira way.

    Note: This only works fine if there is no problematic whitespace handling.

    :copyleft: 2011-2012 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import division, absolute_import, print_function, unicode_literals

import unittest

from creole.shared.unknown_tags import preformat_unknown_nodes
from creole.tests.utils.base_unittest import BaseCreoleTest


class JiraTests(BaseCreoleTest):
    def test_line_breaks(self):
        """
        Line breaks in HTML are lost.
        """
        self.assert_html2jira(
            rest_string="""
                first block, line 1 and line 2
                
                second block, line 1 and line 2
            """,
            html_string="""
                <p>first block, line 1
                and line 2</p>
                <p>second block, line 1
                and line 2</p>
            """,
#            debug=True
        )

#    def test_substitution_image_without_alt_or_title(self):
#        self.assert_html2jira(
#            rest_string="""
#                A inline |image.png| image.
#
#                .. |image.png| image:: /url/to/image.png
#
#                ...and some text below.
#            """,
#            html_string="""
#                <p>A inline <img src="/url/to/image.png" /> image.</p>
#                <p>...and some text below.</p>
#            """
#        )

#    def test_substitution_image_with_title(self):
#        self.assert_html2jira(
#            rest_string="""
#                A inline |foo bar| image.
#
#                .. |foo bar| image:: /url/to/image.png
#
#                ...and some text below.
#            """,
#            html_string="""
#                <p>A inline <img title="foo bar" src="/url/to/image.png" /> image.</p>
#                <p>...and some text below.</p>
#            """
#        )

    def test_pre_code1(self):
        import pudb
        pudb.set_trace()
        self.assert_html2jira(
            rest_string="""\n {quote}>>> from creole import creole2html
>>> creole2html("This is **creole //markup//**")
'<p>This is <strong>creole <i>markup</i></strong></p>{quote}
            """,
            html_string="""
                <pre>
                &gt;&gt;&gt; from creole import creole2html
                &gt;&gt;&gt; creole2html(&quot;This is **creole //markup//**&quot;)
                '&lt;p&gt;This is &lt;strong&gt;creole &lt;i&gt;markup&lt;/i&gt;&lt;/strong&gt;&lt;/p&gt;\n'
                </pre>
            """
        )

#    def test_block(self):
#        self.assert_html2jira(
#            rest_string="""
#                    >>> from creole import creole2html
#                    >>> creole2html("This is **creole //markup//**")
#                    '<p>This is <strong>creole <i>markup</i></strong></p>
#            """,
#            html_string="""
#                <pre>
#                &gt;&gt;&gt; from creole import creole2html
#                &gt;&gt;&gt; creole2html(&quot;This is **creole //markup//**&quot;)
#                '&lt;p&gt;This is &lt;strong&gt;creole &lt;i&gt;markup&lt;/i&gt;&lt;/strong&gt;&lt;/p&gt;\n'
#                </pre>
#            """
#        )
#
    def test_escape(self):
        self.assert_html2jira(
            rest_string="""
                * Use <tt> when {{{ ... }}} is inline and not <pre>, or not?
            """,
            html_string="""
                <ul>
                <li>Use &lt;tt&gt; when {{{ ... }}} is inline and not &lt;pre&gt;, or not?</li>
                </ul>
            """
        )

    def test_inline_literals(self):
        self.assert_html2jira(
            rest_string="""
                This text is an example of {{inline literals}}.
            """,
            html_string="""
                <ul>
                <p>This text is an example of <tt>inline literals</tt>.</p>
                </ul>
            """
        )

    def test_list_without_p(self):
        self.assert_html2jira(
            rest_string="""
                A nested bullet lists:
                
                * item 1 without p-tag
                ** A *[subitem 1.1|/1.1/url/] link* here.
                *** subsubitem 1.1.1
                *** subsubitem 1.1.2
                ** subitem 1.2
                * item 2 without p-tag
                ** subitem 2.1
                    
                Text under list.
            """,
            html_string="""
                <p>A nested bullet lists:</p>
                <ul>
                    <li>item 1 without p-tag
                        <ul>
                            <li>A <strong><a href="/1.1/url/">subitem 1.1</a> link</strong> here.
                                <ul>
                                    <li>subsubitem 1.1.1</li>
                                    <li>subsubitem 1.1.2</li>
                                </ul>
                            </li>
                            <li>subitem 1.2</li>
                        </ul>
                    </li>
                    <li>item 2 without p-tag
                        <ul>
                            <li>subitem 2.1</li>
                        </ul>
                    </li>
                </ul>
                <p>Text under list.</p>
            """
        )

    def test_table_with_headings(self):
        self.assert_html2jira(
            rest_string="""
                ||head 1 ||head 2 ||
                | item 1 | item 2 |
            """,
            html_string="""
                <table>
                <tr><th>head 1</th><th>head 2</th>
                </tr>
                <tr><td>item 1</td><td>item 2</td>
                </tr>
                </table>
            """
        )

    def test_table_without_headings(self):
        self.assert_html2jira(
            rest_string="""
                | item 1 | item 2 |
                | item 3 | item 4 |
            """,
            html_string="""
                <table>
                <tr><td>item 1</td><td>item 2</td>
                </tr>
                <tr><td>item 3</td><td>item 4</td>
                </tr>
                </table>
            """
        )
        

#    def test_preformat_unknown_nodes(self):
#        """
#        Put unknown tags in a <pre> area.
#        """
#        self.assert_html2jira(
#            rest_string="""
#                111 <<pre>><x><</pre>>foo<<pre>></x><</pre>> 222
#                333<<pre>><x foo1="bar1"><</pre>>foobar<<pre>></x><</pre>>444
#                
#                555<<pre>><x /><</pre>>666
#            """,
#            html_string="""
#                <p>111 <x>foo</x> 222<br />
#                333<x foo1="bar1">foobar</x>444</p>
#    
#                <p>555<x />666</p>
#            """,
#            emitter_kwargs={"unknown_emit":preformat_unknown_nodes}
#        )
#
#    def test_transparent_unknown_nodes(self):
#        """
#        transparent_unknown_nodes is the default unknown_emit:
#        
#        Remove all unknown html tags and show only
#        their child nodes' content.
#        """
#        self.assert_html2jira(
#            rest_string="""
#                111 <<pre>><x><</pre>>foo<<pre>></x><</pre>> 222
#                333<<pre>><x foo1="bar1"><</pre>>foobar<<pre>></x><</pre>>444
#                
#                555<<pre>><x /><</pre>>666
#            """,
#            html_string="""
#                <p>111 <x>foo</x> 222<br />
#                333<x foo1="bar1">foobar</x>444</p>
#    
#                <p>555<x />666</p>
#            """,
#        )


if __name__ == '__main__':
    unittest.main()
