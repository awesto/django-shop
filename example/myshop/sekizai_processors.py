"""
 source: https://gist.github.com/1311010
 Get django-sekizai, django-compessor (and django-cms) playing nicely together
 re: https://github.com/ojii/django-sekizai/issues/4
 using: https://github.com/django-compressor/django-compressor.git
 and: https://github.com/ojii/django-sekizai.git@0.6 or later
"""
from compressor.templatetags.compress import CompressorNode
from compressor.exceptions import UncompressableFileError
from django.template.base import TextNode


def compress(context, data, name):
    """
    Data is the string from the template (the list of js files in this case)
    Name is either 'js' or 'css' (the sekizai namespace)
    Basically passes the string through the {% compress 'js' %} template tag
    """
    try:
        return CompressorNode(nodelist=TextNode(data), kind=name, mode='file').render(context=context)
    except UncompressableFileError:
        return CompressorNode(nodelist=TextNode(data), kind=name, mode='file').get_original_content(context=context)
