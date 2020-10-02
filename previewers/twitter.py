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


from datetime import datetime
import regex as re
import requests

from supybot import log

# Optional support for humanize
try:
    from humanize import naturaltime
except ImportError:
    def naturaltime(x):
        return x


def can_handle(domain):
    return domain == 'twitter.com'


def handle(url, token):
    # Look for status (tweet) URL
    # negative lookbehind to exclude sub-pages like …status/123/likes
    status_pattern = re.compile(r'twitter.com/\w+/status/(\d+)(?!.*/\w+)')
    status_id = status_pattern.search(url)
    if status_id is not None:
        preview = get_status(status_id.group(1), token)
        if preview is None:
            return None
        return preview
    # We found no status/tweet URL, but maybe still a twitter profile?
    # Look for status (tweet) URL
    # negative lookbehind to exclude urls like twitter.com/foo/likes
    profile_pattern = re.compile(r'twitter.com/(\w+)(?!.*/\w+)')
    handle = profile_pattern.search(url)
    if handle is not None:
        profile_info = get_profile(handle.group(1), token)
        if profile_info is None:
            return None
        return profile_info
    return None


def format_author(name, username, verified):
    if verified:
        # Name in bold, checkmark in cyan (58 => #00ffff)
        return '\x02%s\x0358✔️\x03\x02(@%s)' % (name, username)
    else:
        # Name in bold
        return '\x02%s\x02 (@%s)' % (name, username)


def humanize_count(count):
    if count > 1e10:
        return '%.0fB' % (count / 1e9)
    if count > 1e9:
        return '%.1fB' % (count / 1e9)
    if count > 1e7:
        return '%.0fM' % (count / 1e6)
    if count > 1e6:
        return '%.1fM' % (count / 1e6)
    if count > 1e4:
        return '%.0fK' % (count / 1e3)
    if count > 1e3:
        return '%.1fK' % (count / 1e3)
    return count


def humanize_time(timestamp):
    '''Humanizes time. Doesn't do much if humanize couldn't be imported'''
    # Remove trailing Z that datetime doesn't like
    timestamp = timestamp.replace('Z', '')
    created_at = datetime.fromisoformat(timestamp)
    return naturaltime(created_at)


def get_profile(user, token):
    headers = {'Authorization': 'Bearer %s' % token}
    # Twitter API wants value lists to be comma separated , but requests lib
    # urlencodes commas – so we build the URL by hand
    url = 'https://api.twitter.com/2/users/by/username/' + user
    url += '?user.fields=description,public_metrics,verified'
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log.error('twitter.get_profile: call to API ' +
                  'unsuccesful, HTTP status code ' + str(r.status_code))
        return None
    json = r.json()
    if 'errors' in json:
        # Most likely there's no profile with that name, so abort
        return None
    try:
        description = json['data']['description']
        name = json['data']['name']
        username = json['data']['username']
        verified = json['data']['verified']
        tweet_count = json['data']['public_metrics']['tweet_count']
        followers_count = json['data']['public_metrics']['followers_count']
    except KeyError as e:
        log.error('twitter.get_status: %s' % repr(e))
        return None
    # replace linebreaks with Return symbol
    description = re.sub('\n+', ' ⏎ ', description)
    # Remove excess whitespace
    description = re.sub(' +', ' ', description)
    author = format_author(name, username, verified)
    followers_count = humanize_count(followers_count)
    tweet_count = humanize_count(tweet_count)
    return '%s: %s (%s tweets, %s followers)' \
           % (author, description, tweet_count, followers_count)


def get_status(tweet_id, token):
    headers = {'Authorization': 'Bearer %s' % token}
    # Twitter API wants value lists to be comma separated , but requests lib
    # urlencodes commas – so we build the URL by hand
    url = 'https://api.twitter.com/2/tweets/%s' % tweet_id
    url += '?tweet.fields=created_at'
    url += '&expansions=author_id&user.fields=username,verified'
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        log.error('twitter.get_status: call to API ' +
                  'unsuccesful, HTTP status code ' + str(r.status_code))
        return None
    json = r.json()
    if 'errors' in json:
        # Most likely there's no tweet with that id, so abort
        return None
    try:
        tweet = json['data']['text'].strip()
        timestamp = json['data']['created_at']
        username = json['includes']['users'][0]['username']
        name = json['includes']['users'][0]['name']
        verified = json['includes']['users'][0]['verified']
    except KeyError as e:
        log.error('twitter.get_status: %s' % repr(e))
        return None
    # replace linebreaks with Return symbol
    tweet = re.sub('\n+', ' ⏎ ', tweet)
    # Remove excess whitespace
    tweet = re.sub(' +', ' ', tweet)
    author = format_author(name, username, verified)
    time = humanize_time(timestamp)
    return '%s: %s (%s)' % (author, tweet, time)
