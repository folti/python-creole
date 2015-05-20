#!/usr/bin/env python
# coding: utf-8

"""
    html -> Jira Wiki Emitter
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Links about Jira Wiki markup:

    https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all

    :copyleft: 2011-2012 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import division, absolute_import, print_function, unicode_literals
import posixpath

from creole.html_parser.config import BLOCK_TAGS
from creole.shared.base_emitter import BaseEmitter
from creole.shared.markup_table import MarkupTable


class JiraMarkupTable(MarkupTable):

    def get_rest_table(self):
        """ return the table data in ReSt markup. """
        # preformat every table cell
        cells, widths = self._get_preformat_info()

        lines = []
        first = True
        for no, row in enumerate(cells):
            # Join every line with ljust
            cells = [cell.ljust(width) for cell, width in zip(row, widths)]
            line = "|" + "|".join(cells) + "|"
            if first and self.has_header:
                line += self.head_prefix
                first = False
            lines.append(line)

        return "\n".join(lines)


class JiraTextEmitter(BaseEmitter):
    """
    Build from a document_tree (html2creole.parser.HtmlParser instance) a
    creole markup text.
    """
    def __init__(self, *args, **kwargs):
        super(JiraTextEmitter, self).__init__(*args, **kwargs)

        self.table_head_prefix = "|"
        self.table_auto_width = False

        self._substitution_data = []
        self._used_substitution_links = {}
        self._used_substitution_images = {}
        self._list_markup = ""

    def _get_block_data(self):
        """
        return substitution bock data
        e.g.:
        .. _link text: /link/url/
        .. |substitution| image:: /image.png
        """
        content = "\n".join(self._substitution_data)
        self._substitution_data = []
        return content

    #--------------------------------------------------------------------------

    def blockdata_pre_emit(self, node):
        """ pre block -> with newline at the end """
        pre_block = self.deentity.replace_all(node.content).strip()
        print(pre_block)
        pre_block = "\n".join(["%s" % line for line in pre_block.splitlines()])
        return "{quote}\n%s\n{quote}\n\n" % pre_block

    def inlinedata_pre_emit(self, node):
        """ a pre inline block -> no newline at the end """
        return "{{%s}}" % self.deentity.replace_all(node.content)

    def blockdata_pass_emit(self, node):
        return "%s\n\n" % node.content
        return node.content

    #--------------------------------------------------------------------------

    def emit_children(self, node):
        """Emit all the children of a node."""
        return "".join(self.emit_children_list(node))

    def emit(self):
        """Emit the document represented by self.root DOM tree."""
        return self.emit_node(self.root).rstrip()

    def document_emit(self, node):
        self.last = node
        result = self.emit_children(node)
        if self._substitution_data:
            # add rest at the end
            result += "%s\n\n" % self._get_block_data()
        return result

    def emit_node(self, node):
        result = ""
        if self._substitution_data and node.parent == self.root:
            result += "%s\n\n" % self._get_block_data()

        result += super(JiraTextEmitter, self).emit_node(node)
        return result

    def p_emit(self, node):
        return "%s\n\n" % self.emit_children(node)

    HEADLINE_DATA = {
        1: "h1",
        2: "h2",
        3: "h3",
        4: "h4",
        5: "h5",
        6: "h6",
    }
    def headline_emit(self, node):
        text = self.emit_children(node)

        level = node.level
        if level > 6:
            level = 6

        return "%s. %s\n\n" % (self.HEADLINE_DATA[level], text)


    #--------------------------------------------------------------------------

    def _typeface(self, node, key):
        return key + self.emit_children(node) + key

    def strong_emit(self, node):
        return self._typeface(node, key="*")
    def b_emit(self, node):
        return self._typeface(node, key="*")
    big_emit = strong_emit

    def i_emit(self, node):
        return self._typeface(node, key="_")
    def em_emit(self, node):
        return self._typeface(node, key="_")

    def tt_emit(self, node):
        return "{{" + self.emit_children(node) + "}}"

    def small_emit(self, node):
        # FIXME: Is there no small in ReSt???
        return self.emit_children(node)

    def sup_emit(self, node):
        return self._typeface(node, key="^")
    def sub_emit(self, node):
        return self._typeface(node, key="~")
    def del_emit(self, node):
        return self._typeface(node, key="-")
#
    def cite_emit(self, node):
        return self._typeface(node, key="??")
    def ins_emit(self, node):
        return self._typeface(node, key="+")

    #--------------------------------------------------------------------------

    def hr_emit(self, node):
        return "----\n\n"

    def _get_anchor(self, node):
        try:
            return node.attrs['name']
        except KeyError:
            # HTML 5
            return node.attrs['id']

    def a_emit(self, node):
        link_text = self.emit_children(node)
        url = None
        anchor = None

        if 'class' in node.attrs:
          if node.attrs['class'] in ('moz-txt-link-rfc2396e', 'moz-txt-link-rfc2396E'):
            return '[mailto:%s]' % link_text
          if node.attrs['class'] == 'moz-txt-link-freetext':
            return '[%s]' % link_text
          if node.attrs['class'] == 'moz-txt-link-abbreviated':
            return link_text

        try:
          url = node.attrs["href"]
        except KeyError:
          anchor = self._get_anchor(node)

        if url:
            link = "[%s]" % url
            if link_text != "":
                link = "[%s|%s]" % (link_text, url)
        if anchor:
            link = "{%s}" % anchor
            if link_text != "":
                link = "{%s:%s}" % (link_text, anchor)

        return link

    def img_emit(self, node):
        src = node.attrs["src"]

        if src.split(':')[0] == 'data':
            return ""

        ret = "!%s!" % src

        return ret

    #--------------------------------------------------------------------------

    def code_emit(self, node):
        return "{code}\n%s\n{code}\n\n" % self._emit_content(node)

    #--------------------------------------------------------------------------

    def li_emit(self, node):
        content = self.emit_children(node).strip("\n")
        result = "\n%s %s\n" % (self._list_markup, content)
        return result

    def _list_emit(self, node, list_type):
        if node.level > 1:
            self._list_markup += list_type
        else:
            self._list_markup = list_type
        content = self.emit_children(node)

        if node.level == 1:
            # FIXME: This should be made ​​easier and better
            complete_list = "\n".join([i.strip("\n") for i in content.split("\n") if i])
            content = "%s\n\n" % complete_list

        if node.level >= 1:
            self._list_markup = self._list_markup[:(node.level-1)]

        return content

    def ul_emit(self, node):
        return self._list_emit(node, "*")

    def ol_emit(self, node):
        return self._list_emit(node, "#")

    def table_emit(self, node):
        self._table = JiraMarkupTable(
            head_prefix="|",
            auto_width=True,
            debug_msg=self.debug_msg
        )
        self.emit_children(node)
        content = self._table.get_rest_table()
        return "%s\n\n" % content


if __name__ == '__main__':
    import doctest
    print(doctest.testmod())

#    import sys;sys.exit()
    from creole.html_parser.parser import HtmlParser

    data = """
<a href="#bottom">jump to bottom</a>
<p>A nested bullet lists:</p>
<ul>
<li><p>item 1</p>
<ul>
<li><p>A <strong>bold subitem 1.1</strong> here.</p>
<ul>
<li>subsubitem 1.1.1</li>
<li>subsubitem 1.1.2 with inline <img alt="substitution text" src="/url/to/image.png" /> image.</li>
</ul>
</li>
<li><p>subitem 1.2</p>
</li>
</ul>
</li>
<li><p>item 2</p>
<ol>
<li>subitem 2.1</li>
</ol>
</li>
</ul>
<p>Text under list.</p>
<p>4 <img alt="PNG pictures" src="/image.png" /> four</p>
<p>5 <img alt="Image without files ext?" src="/path1/path2/image" /> five</p>
<a id="_bottom">bottom</a>
"""

    print(data)
    h2c = HtmlParser(
#        debug=True
    )
    document_tree = h2c.feed(data)
    h2c.debug()

    e = JiraTextEmitter(document_tree,
        debug=True
    )
    content = e.emit()
    print("*" * 79)
    print(content)
    print("*" * 79)
    print(content.replace(" ", ".").replace("\n", "\\n\n"))

