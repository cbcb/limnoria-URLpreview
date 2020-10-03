###
# Copyright © Christian Baumhof 2020
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###

from inspect import getmembers, isclass
from importlib import import_module
from pkgutil import iter_modules


class Previewer:
    def can_handle(self, domain):
        '''Returns True iff this Previewer can handle the domain.'''
        raise NotImplementedError

    def get_preview(self, url):
        '''Returns a preview message for the url,
           or None if the preview fails'''
        raise NotImplementedError

    def configure(self, plugin, advanced):
        '''Called by config.py during the initial configure step'''
        return

    def register_vars(self, plugin):
        '''Called by config.py when the plugin is loaded.
            Register your variables here.'''
        raise NotImplementedError


class PreviewerCollection:
    """Collection object that looks for all previewers upon creation"""

    def __init__(self):
        self.previewers = []
        package = import_module('URLpreview.previewers')

        for _, name, ispkg in iter_modules(
                package.__path__, package.__name__ + '.'):
            if not ispkg:
                module = import_module(name)
                classes = getmembers(module, isclass)
                for (_, c) in classes:
                    if c is not Previewer and issubclass(c, Previewer):
                        self.previewers.append(c())

    def get_previewer(self, domain):
        """Returns a previewer that claims to be able to handle <domain>"""
        for previewer in self.previewers:
            if previewer.can_handle(domain):
                return previewer
        return None

    def configure(self, plugin, advanced):
        """Calls the configure() method of each previewer"""
        for previewer in self.previewers:
            previewer.configure(plugin, advanced)

    def register_vars(self, plugin):
        """Calls the register_vars() method of each previewer"""
        for previewer in self.previewers:
            previewer.register_vars(plugin)
