"""
 source: https://gist.github.com/1311010
 Get django-sekizai, django-compessor (and django-cms) playing nicely together
 re: https://github.com/ojii/django-sekizai/issues/4
 using: https://github.com/django-compressor/django-compressor.git
 and: https://github.com/ojii/django-sekizai.git@0.6 or later
"""
from compressor.templatetags.compress import CompressorNode
from compressor.exceptions import UncompressableFileError
from compressor.base import Compressor
from compressor.conf import settings
from compressor.utils import get_class

from django.template.base import TextNode


def compress(context, data, name):
    """
    Data is the string from the template (the list of js files in this case)
    Name is either 'js' or 'css' (the sekizai namespace)
    Basically passes the string through the {% compress 'js' %} template tag
    """
    # separate compressable from uncompressable files
    parser = get_class(settings.COMPRESS_PARSER)(data)
    compressor = Compressor()
    compressable_elements, expanded_elements, deferred_elements = [], [], []
    if name == 'js':
        for elem in parser.js_elems():
            attribs = parser.elem_attribs(elem)
            try:
                if 'src' in attribs:
                    compressor.get_basename(attribs['src'])
            except UncompressableFileError:
                if 'defer' in attribs:
                    deferred_elements.append(elem)
                else:
                    expanded_elements.append(elem)
            else:
                compressable_elements.append(elem)
    elif name == 'css':
        for elem in parser.css_elems():
            attribs = parser.elem_attribs(elem)
            try:
                if parser.elem_name(elem) == 'link' and attribs['rel'].lower() == 'stylesheet':
                    compressor.get_basename(attribs['href'])
            except UncompressableFileError:
                expanded_elements.append(elem)
            else:
                compressable_elements.append(elem)

    # reconcatenate them
    data = ''.join(parser.elem_str(e) for e in expanded_elements)
    expanded_node = CompressorNode(nodelist=TextNode(data), kind=name, mode='file')
    data = ''.join(parser.elem_str(e) for e in compressable_elements)
    compressable_node = CompressorNode(nodelist=TextNode(data), kind=name, mode='file')
    data = ''.join(parser.elem_str(e) for e in deferred_elements)
    deferred_node = CompressorNode(nodelist=TextNode(data), kind=name, mode='file')

    return '\n'.join([
        expanded_node.get_original_content(context=context),
        compressable_node.render(context=context),
        deferred_node.get_original_content(context=context),
    ])
