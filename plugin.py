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


from supybot import callbacks, ircmsgs  # utils, plugins, ircutils,

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('URLpreview')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x):
        return x

from .previewers import generic
from .previewer import PreviewerCollection


class URLpreview(callbacks.Plugin):  # pylint: disable=too-many-ancestors
    """This plugin looks for URLs posted to channels and responds with
    a preview of the content"""
    threaded = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previewers = PreviewerCollection()

    def doPrivmsg(self, irc, msg):
        channel = msg.args[0]
        text = msg.args[1]
        if not self.registryValue('enabled', channel):
            return  # Disabled in this channel
        url = find_url(text)
        if url is None:
            return  # No URL found
        domain = get_domain(url)

        preview = None
        # Find previewer
        previewer = self.previewers.get_previewer(domain)
        if previewer is not None:
            preview = previewer.get_preview(self, url)

        elif generic.can_handle(domain):
            if self.registryValue('generic_enabled'):
                preview = generic.handle(url)

        # Handle the result
        if preview is None:
            return
        irc.queueMsg(ircmsgs.privmsg(channel, preview))


def find_url(text):
    # First, find something that looks vaguely like a URL
    url_pattern = re.compile(
        r'http[s]?://(?:\p{Letter}|\p{Number}|[$-_@.&+]|[!*\(\),]'
        + r'|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    match = url_pattern.search(text)
    if match is None:
        return None
    return match.group(0)


def get_domain(url):
    domain = re.sub(r'https?://', '', url)  # remove scheme part
    domain = re.sub(r'/.*', '', domain)  # remove everything after first slash
    domain = re.sub(r':.*', '', domain)  # remove everything after first colon
    return domain


Class = URLpreview
