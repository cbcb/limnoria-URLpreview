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

import regex as re

from .generic import handle

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('URLpreview')
except ImportError:
    def _(x):
        return x

from URLpreview.previewer import Previewer


class NprPreviewer(Previewer):
    def can_handle(self, domain):
        '''Returns True iff this Previewer can handle the domain.'''
        return domain.endswith('npr.org')

    def get_preview(self, plugin, url):
        '''Rewrites URL to point to text.npr.org if necessary
           Then calls the generic previewer'''
        if re.search(r'text.npr.org', url) is None:
            story_id = re.match(r'.*npr\.org.*/\d\d\d\d/\d\d/\d\d/(\d+)', url)
            url = 'https://text.npr.org/%s' % story_id.group(1)
        return handle(url)

    def configure(self, plugin, advanced):
        '''Called by config.py during the initial configure step'''
        pass

    def register_vars(self, plugin):
        '''Called by config.py when the plugin is loaded.
            Register your variables here.'''
        pass
