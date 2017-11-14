from __future__ import unicode_literals

import json, os

from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import os_path


class FragmentsBuilder(StandaloneHTMLBuilder):
    name = 'fragments'

    def __init__(self, app):
        super(FragmentsBuilder, self).__init__(app)
        self.config.html_theme = 'bootstrap'
        self.config.html_theme_path.append(os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, 'theme')))
        self.docsmap_file = os.path.join(self.outdir, 'docsmap.json')
        if os.path.exists(self.docsmap_file):
            with open(self.docsmap_file, 'r') as fh:
                self.docs_map = json.load(fh, encoding='utf-8')
        else:
            self.docs_map = {}

    def prepare_writing(self, docnames):
        super(FragmentsBuilder, self).prepare_writing(docnames)
        for docname in docnames:
            doctree = self.env.get_doctree(docname)
            idx = doctree.first_child_matching_class(nodes.section)
            if idx is None or idx == -1:
                continue

            first_section = doctree[idx]
            idx = first_section.first_child_matching_class(nodes.title)
            if idx is None or idx == -1:
                continue

            doctitle = first_section[idx].astext()
            if doctitle:
                docurl = os_path(docname) + self.out_suffix
                self.docs_map[docname] = docurl, doctitle
                print(doctitle + ': ' + docurl)

    def Xget_relative_uri(self, from_, to, typ=None):
        relative_uri = super(FragmentsBuilder, self).get_relative_uri(from_, to, typ)
        return relative_uri

    def finish(self):
        super(FragmentsBuilder, self).finish()
        with open(self.docsmap_file, 'w') as fh:
            json.dump(self.docs_map, fh)


def setup(app):
    app.require_sphinx('1.0')
    app.add_builder(FragmentsBuilder)
