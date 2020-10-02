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

from bs4 import BeautifulSoup
from datetime import datetime
import regex as re
import requests

# Optional support for humanize
try:
    from humanize import naturaltime
except ImportError:
    def naturaltime(x): return x

from supybot import log


MAX_SIZE = 5 * 1024 * 1024
TIMEOUT = 10
ATTEMPT_INSECURE = True
MAX_TITLE_LENGTH = 140
MAX_DESC_LENGTH = 280

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0)' +
           'Gecko/20100101 Firefox/81.0'}

DOMAIN_BLACKLIST = [
    # Blacklist domains that shouldn't be accessed or don't work
    'localhost',
    'local',
    # RFC 2606
    'invalid',
    'example',
    'test',
    # Previewers are available for these:
    'twitter.com',
    't.co',
    'youtube.com',
    'youtu.be',
    # Add other non-working domains below:
    'blog.fefe.de',
    'outline.com',
]


def can_handle(domain):
    return not is_domain_blacklisted(domain)


def handle(url):
    secure = True
    try:
        r = download(url)
    except requests.exceptions.SSLError:
        secure = False
    except Exception as e:
        log.info('URLpreview.generic.handle: trying "%s", exception %s' %
                 (url, repr(e)))
        return
    # Retry without verification?
    if ATTEMPT_INSECURE and not secure:
        try:
            r = download(url, False)
        except Exception as e:
            log.info('URLpreview.generic.handle: trying "%s", exception %s' %
                     (url, repr(e)))
            return

    if not r.headers['content-type'].startswith('text/html'):
        return

    if not r.ok:
        return format_msg(secure, {
            'title': 'Error %d' % r.status_code,
            'desc': r.reason,
            'date': None,
        })

    meta = get_meta(r.content)

    return format_msg(secure, meta)


def download(url, verify=True):
    r = requests.get(
        url, headers=HEADERS, timeout=TIMEOUT, stream=True, verify=verify)

    data = []
    length = 0

    for chunk in r.iter_content(1024):
        data.append(chunk)
        length += len(chunk)
        if length > MAX_SIZE:
            break

    r._content = b''.join(data)
    return r


def get_meta(content):
    soup = BeautifulSoup(content, 'html.parser')
    title = None
    desc = None
    date = None
    # Get title from meta tags
    for place in [
        soup.find('meta', {'name': 'title'}),
        soup.find('meta', {'property': 'og:title'}),
        soup.find('meta', {'property': 'twitter:title'}),
    ]:
        if place is not None:
            title = place['content']
            break
    # Last chance: title tag
    if title is None and soup.title is not None:
        title = soup.title.string

    # Get desc from meta tags
    for place in [
        soup.find('meta', {'name': 'description'}),
        soup.find('meta', {'property': 'og:description'}),
        soup.find('meta', {'property': 'twitter:description'}),
    ]:
        if place is not None:
            desc = place['content']
            break

    # Date handling from meta tag
    if soup.find('meta', {'name': 'date'}) is not None:
        date = soup.find('meta', {'name': 'date'})['content']
        try:
            date = datetime.fromisoformat(date)
        except ValueError:
            pass  # malformed date, nothing we can do about it :(

    return {
        'title': sanitize(title),
        'desc': sanitize(desc),
        'date': date,
    }


def sanitize(string):
    if string is None:
        return None
    # replace linebreaks with spaces
    string = re.sub(r'\n+', ' ', string)
    # Remove excess whitespace
    string = re.sub(r'\s+', ' ', string)
    return string.strip()


def format_msg(secure, meta):
    title = meta['title']
    desc = meta['desc']
    date = meta['date']
    if title is None:
        return
    msg = 'Preview: '
    if not secure:
        # Color codes: 98,52: White on Red background
        msg += '⚠️ \x02\x0398,52Insecure\x0f '
    msg += '\x02%s\x02' % title[:MAX_TITLE_LENGTH]
    if len(title) > MAX_TITLE_LENGTH:
        msg += '…'
    if desc is not None:
        msg += ' ' + desc[:MAX_DESC_LENGTH]
        if len(desc) > MAX_DESC_LENGTH:
            msg += '…'
    if date is not None:
        msg += ' (%s)' % humanize_time(date)
    return msg


def humanize_time(date):
    if date.utcoffset() is not None:
        date = date + date.utcoffset()
        date = date.replace(tzinfo=None)
    return naturaltime(date)


def is_domain_blacklisted(domain):
    if any([
        domain.startswith('.'),
        # domain.endswith('.'),
        len(domain) < 3,
    ]):
        return True
    for blacklisted_domain in DOMAIN_BLACKLIST:
        if domain.endswith(blacklisted_domain):
            return True
    return False
