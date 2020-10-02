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

from supybot import conf, registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('URLpreview')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x): return x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import something, yn  # expect, anything,
    # General
    conf.registerPlugin('URLpreview', True)
    # Twitter
    if yn(_('Enable for Twitter links? (needs API key)')):
        URLpreview.twitter_enable.setValue(True)
        token = something(_('Enter Twitter OAuth Bearer token'))
        URLpreview.twitter_api_token.setValue(token)


URLpreview = conf.registerPlugin('URLpreview')
# General
conf.registerChannelValue(
    URLpreview, 'enabled',
    registry.Boolean(True, _('enable for this channel')))

# Twitter
conf.registerGlobalValue(
    URLpreview, 'twitter_enabled',
    registry.Boolean(False, _('Enable for Twitter links? (needs API key)')))
conf.registerGlobalValue(
    URLpreview, 'twitter_api_token',
    registry.String('', _('Twitter API OAuth 2.0 Bearer token'), private=True))

# Youtube
conf.registerGlobalValue(
    URLpreview, 'youtube_enabled',
    registry.Boolean(False, _('Enable for YouTube links? (needs API key)')))