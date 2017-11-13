from __future__ import unicode_literals

import json, os

from docutils import nodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util import os_path


class DjangoCMSBuilder(StandaloneHTMLBuilder):
    name = 'djangocms'

    def __init__(self, app):
        super(DjangoCMSBuilder, self).__init__(app)
        self.docsmap_file = os.path.join(self.outdir, 'docsmap.json')
        if os.path.exists(self.docsmap_file):
            with open(self.docsmap_file, 'r') as fh:
                self.docs_map = json.load(fh, encoding='utf-8')
        else:
            self.docs_map = {}

    def prepare_writing(self, docnames):
        super(DjangoCMSBuilder, self).prepare_writing(docnames)
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

    def finish(self):
        super(DjangoCMSBuilder, self).finish()
        with open(self.docsmap_file, 'w') as fh:
            json.dump(self.docs_map, fh)


def setup(app):
    app.require_sphinx('1.0')
    app.add_builder(DjangoCMSBuilder)
