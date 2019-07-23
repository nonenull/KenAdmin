# coding=utf-8
from importlib import import_module

from django.conf import settings
from django.template.context import make_context
from django.template.backends.base import BaseEngine
from django.template.backends.django import get_installed_libraries, Template
import tenjin
from tenjin.helpers import *

import logging

logger = logging.getLogger("oms")


class TenJinTemplates(BaseEngine):
    app_dirname = 'templates'

    def __init__(self, params):
        params = params.copy()
        options = params.pop('OPTIONS').copy()
        super().__init__(params)
        self.debug = options.get('debug', settings.DEBUG)
        # self.autoescape = options.get('autoescape', True)
        self.file_charset = options.get('file_charset', settings.FILE_CHARSET)
        # self.libraries = self.get_templatetag_libraries(
        #     options.get('libraries', {})
        # )
        """
        
        tenjin.Template params
        
        (self, filename=None, encoding=None, input=None, escapefunc=None, tostrfunc=None,
         indent=None, preamble=None, postamble=None, smarttrim=None, trace=None)
         
        --------------------------
        tenjin.Engine params
         
        (self, prefix=None, postfix=None, layout=None, path=None,
         cache=True, preprocess=None, templateclass=None, preprocessorclass=None,
          lang=None, loader=None, pp=None, **kwargs)
        """

        antiDebug = (not self.debug)
        self.engine = tenjin.Engine(
            path=self.template_dirs, postfix=".html", encoding=self.file_charset,
            trace=self.debug, smarttrim=antiDebug, cache=antiDebug
        )

    def get_template(self, template_name):
        template = TenJinTemplate(self.engine.get_template(template_name), self)
        logger.debug("TenJinTemplate get_template===== %s" % template)
        return template

    def get_templatetag_libraries(self, custom_libraries):
        """
        Return a collation of template tag libraries from installed
        applications and the supplied custom_libraries argument.
        """
        librarieList = []
        libraries = get_installed_libraries()
        libraries.update(custom_libraries)
        for lib in libraries.values():
            pkg = import_module(lib)
            librarieList.append(pkg)
        return librarieList


class TenJinTemplate(Template):
    def __init__(self, template, backend):
        super(TenJinTemplate, self).__init__(template, backend)

    def render(self, context=None, request=None):
        return self.template.render(context)
