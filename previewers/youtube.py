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

from dateutil.parser import parse, ParserError
import random
import regex as re
import requests

# Optional support for humanize
try:
    from humanize import intcomma, naturaltime
except ImportError:
    def nop(x):
        return x
    naturaltime = intcomma = nop

from supybot import conf, log, registry
from supybot.questions import something, yn

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('URLpreview')
except ImportError:
    def _(x):
        return x

from URLpreview.previewer import Previewer

API_URL = 'https://www.googleapis.com/youtube/v3/videos'
# https://developers.google.com/youtube/v3/docs/videos/list
TIMEOUT = 10


class YoutubePreviewer(Previewer):
    def can_handle(self, domain):
        '''Returns True iff this Previewer can handle the domain.'''
        return domain.endswith('youtube.com') or domain.endswith('youtu.be')

    def get_preview(self, plugin, url):
        '''Returns a preview message for the url,
           or None if the preview fails'''
        if plugin.registryValue('youtube_enabled'):
            token = plugin.registryValue('youtube_api_token')
        else:
            return
        # Individual video?
        video_id = find_video_id(url)
        if video_id is not None:
            return preview_video(token, video_id)

        # We couldn't handle the url after all... :(
        return None

    def configure(self, plugin, advanced):
        '''Called by config.py during the initial configure step'''
        if yn(_('Enable for YouTube links? (needs API key)')):
            plugin.youtube_enabled.setValue(True)
            token = something(_('Enter Google Simple API key'))
            plugin.youtube_api_token.setValue(token)

    def register_vars(self, plugin):
        '''Called by config.py when the plugin is loaded.
            Register your variables here.'''
        conf.registerGlobalValue(
            plugin, 'youtube_enabled',
            registry.Boolean(False,
                             _('Enable for YouTube links? (needs API key)')))
        conf.registerGlobalValue(
            plugin, 'youtube_api_token',
            registry.String('',
                            _('Google Simple API key'),
                            private=True,))


def find_video_id(url):
    """Returns the video id in url or None if none has been found"""
    for pattern in [r'\.be/([\w_-]+)', r'v=([\w_-]+)']:
        result = re.search(pattern, url)
        if result is not None:
            return munge(result.group(1))
    return None


def preview_video(token, video_id):
    url = '%s?key=%s&id=%s&part=id,snippet,statistics' % \
        (API_URL, token, video_id)
    r = requests.get(url, timeout=TIMEOUT)
    if r.status_code != 200:
        log.error('youtube.preview_video: call to API ' +
                  'unsuccesful, HTTP status code ' + str(r.status_code))
        return None
    json = r.json()
    # See if we got something intelligible with 1 result
    try:
        if json['pageInfo']['totalResults'] != 1:
            log.error('youtube.preview_video: Got != 1 result for id %s' %
                      video_id)
            return None
    except KeyError as e:
        log.error('youtube.preview_video: %s' % repr(e))
        return None
    # Get our metadata
    meta = get_video_metadata(json)
    if meta is None:
        return None
    return format_video(meta)


def get_video_metadata(json):
    """Returns the metadata we're interested in
    or None if <json> can't be parsed"""
    meta = {}
    stats = json['items'][0]['statistics']
    snippet = json['items'][0]['snippet']
    try:
        meta['title'] = snippet['title']
        meta['channel'] = snippet['channelTitle']
        meta['views'] = stats['viewCount']
        # Likes and dislikes can be hidden so might not be present
        if 'likeCount' in stats and 'dislikeCount' in stats:
            likes = stats['likeCount']
            dislikes = stats['dislikeCount']
            meta['rating'] = (int(likes), int(dislikes))
        if 'liveBroadcastContent' in snippet and \
                snippet['liveBroadcastContent'] == 'live':
            meta['live'] = True
        else:
            meta['live'] = False
        meta['published'] = snippet['publishedAt']
    except KeyError as e:
        log.error('youtube.get_video_metadata:  %s' % repr(e))
    # Convert published timestamp to datetime object
    try:
        meta['published'] = parse(meta['published'])
    except ParserError as e:
        log.error('youtube.get_video_metadata:  %s' % repr(e))
    return meta


def format_video(meta):
    def bold(s):
        return '\x02%s\x02' % s

    title = meta['title']
    channel = meta['channel']
    views = intcomma(meta['views'])
    if 'rating' in meta:
        rating = 'Rating: %s ' % bold(format_rating(meta['rating']))
    else:
        rating = ''
    when = '🔴 LIVE' if meta['live'] else humanize_time(meta['published'])
    return '%s: %s Views: %s %s(%s)' % \
        (channel, bold(title), bold(views), rating, when)


def format_rating(rating):
    likes, dislikes = rating
    if likes + dislikes == 0:
        return 'n/a'
    if dislikes == 0:
        return '100%'
    if likes == 0:
        return '0%'
    ratio = (likes / (dislikes + likes)) * 100
    if ratio < 1:
        return '%.2f%%' % ratio
    if ratio > 99 or ratio < 10:
        return '%.1f%%' % ratio
    return '%.0f%%' % ratio


def munge(video_id):
    if video_id not in ['dQw4w9WgXcQ', 'YbaTur4A1OU', 'ZZ5LpwO-An4',
                        'cvh0nX08nRw', 'kfVsfOSbJY0', 'Tt7bzxurJ1I',
                        'W5BxWMD8f_w', 'doEqUhFiQS4', 'ub82Xb1C8os',
                        ]:
        return video_id
    return random.choice([
        'oBHTqoR0-8M', 'TZLWjERAtio', 'i-m7B1p2-Lg', 'qOz9vHDV-C0',
        'orESpBo_nPc', '-6Zc8Co2H3w', 'U9DyHthJ6LA', 'wgUczLEUWkA',
        '5iPH-br_eJQ', 'EYkBctqyKic', 'BKorP55Aqvg', 't_KdbASIkB8',
        'ZMByI4s-D-Y', 'f6wlrYwwjWQ', 'xoxhDk-hwuo', 'Rl_Rt0PNxn4', ])


def humanize_time(date):
    if date.utcoffset() is not None:
        date = date + date.utcoffset()
        date = date.replace(tzinfo=None)
    return naturaltime(date)
