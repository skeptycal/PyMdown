# -*- coding: utf-8 -*-
"""
PyMdown

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function
from markdown import Markdown
import codecs
import sys
import traceback
import re
from os.path import exists, isfile, dirname, abspath, join

PY3 = sys.version_info >= (3, 0)
RE_TAGS = re.compile(r'''</?[^>]*>''')
RE_WORD = re.compile(r'''[^\w\- ]''')

if PY3:
    from urllib.parse import quote
    string_type = str
else:
    from urllib import quote
    string_type = basestring  # flake8: noqa


def slugify(text, sep):
    if text is None:
        return ''
    # Strip html tags and lower
    id = RE_TAGS.sub('', text).lower()
    # Remove non word characters or non spaces and dashes
    # Then convert spaces to dashes
    id = RE_WORD.sub('', id).replace(' ', sep)
    # Encode anything that needs to be
    return quote(id)


class PyMdownException(Exception):
    pass


class MdWrapper(Markdown):
    Meta = {}

    def __init__(self, *args, **kwargs):
        super(MdWrapper, self).__init__(*args, **kwargs)

    def registerExtensions(self, extensions, configs):
        """
        Register extensions with this instance of Markdown.

        Keyword arguments:

        * extensions: A list of extensions, which can either
           be strings or objects.  See the docstring on Markdown.
        * configs: A dictionary mapping module names to config options.

        """
        from markdown import util
        from markdown.extensions import Extension
        import logging

        logger =  logging.getLogger('MARKDOWN')

        for ext in extensions:
            try:
                conf = configs.get(ext, {})
                if ext in ('markdown.extensions.headerid', 'markdown.extensions.toc', 'pymdown.headeranchor'):
                    conf['slugify'] = slugify
                if isinstance(ext, util.string_type):
                    ext = self.build_extension(ext, conf)
                if isinstance(ext, Extension):
                    ext.extendMarkdown(self, globals())
                    logger.info('Successfully loaded extension "%s.%s".'
                                % (ext.__class__.__module__, ext.__class__.__name__))
                elif ext is not None:
                    raise TypeError(
                        'Extension "%s.%s" must be of type: "markdown.Extension"'
                        % (ext.__class__.__module__, ext.__class__.__name__))
            except:
                # We want to gracefully continue even if an extension fails.
                # print(str(traceback.format_exc()))
                continue

        return self


class PyMdown(object):
    def __init__(
        self, file_name, encoding, base_path=None, extensions=[]
    ):
        """ Initialize """
        self.meta = {}
        self.file_name = abspath(file_name)
        self.base_path = base_path if base_path is not None else ''
        self.encoding = encoding
        self.check_extensions(extensions)
        self.convert()

    def check_extensions(self, extensions):
        """ Check the extensions and see if anything needs to be modified """
        if isinstance(extensions, string_type) and extensions == "default":
            extensions = [
                "markdown.extensions.extra",
                "markdown.extensions.toc",
                "markdown.extensions.codehilite(guess_lang=False,pygments_style=default)"
            ]
        self.extensions = []
        for e in extensions:
            self.extensions.append(e.replace("${BASE_PATH}", self.base_path))

    def convert(self):
        """ Convert the file to HTML """
        self.markdown = ""
        try:
            with codecs.open(self.file_name, "r", encoding=self.encoding) as f:
                md = MdWrapper(extensions=self.extensions)
                self.markdown = md.convert(f.read())
                try:
                    self.meta = md.Meta
                except:
                    pass
        except:
            raise PyMdownException(str(traceback.format_exc()))


class PyMdowns(PyMdown):
    def __init__(
        self, string,
        base_path=None, extensions=[]
    ):
        """ Initialize """
        self.meta = {}
        self.string = string
        self.base_path = base_path if base_path is not None else ''
        self.check_extensions(extensions)
        self.convert()

    def convert(self):
        """ Convert the given string to HTML """
        self.markdown = ""
        try:
            md = MdWrapper(extensions=self.extensions)
            self.markdown = md.convert(self.string)
            try:
                self.meta = md.Meta
            except:
                pass
        except:
            raise PyMdownException(str(traceback.format_exc()))
