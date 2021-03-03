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
from dateutil.parser import parse, ParserError
import json
import regex as re
import requests

# Optional support for humanize
try:
    from humanize import naturaltime
except ImportError:
    def naturaltime(x): return x

from supybot import log


# The generic previewer isn't implemented as a Previewer instance
# to ensure it's only used as the last resort.

MAX_SIZE = 1 * 1024 * 1024  # Max size to download per attempt in bytes
TIMEOUT = 10                # Timeout per attempt in seconds
ATTEMPT_INSECURE = True     # Should a connection that fails because of
#                             certificate validation be retried?
MAX_TITLE_LENGTH = 140      # length after which the title will be cut
MAX_DESC_LENGTH = 280       # length after which the description will be cut

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0)' +
           'Gecko/20100101 Firefox/81.0'}

DOMAIN_BLACKLIST = [
    # Blacklist domains that shouldn't be accessed or don't work
    'local',
    'localhost',
    # RFC 2606
    'example',
    'invalid',
    'test',
    # Previewers are available for these:
    'npr.org',
    't.co',
    'twitter.com',
    'youtu.be',
    'youtube.com',
    # Add other non-working domains below:
    'blog.fefe.de',
    'huffpost.com',
    'outline.com',
    'washingtonpost.com',
    'zeit.de',
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

    for chunk in r.iter_content(100*1024):
        data.append(chunk)
        length += len(chunk)
        if length > MAX_SIZE:
            break

    r._content = b''.join(data)
    return r


def get_meta(content):
    soup = BeautifulSoup(content, 'html.parser')
    ld_json = soup.find('script', {'type': 'application/ld+json'})
    if ld_json is not None:
        try:
            ld_json = json.loads(ld_json.contents[0])
        except json.decoder.JSONDecodeError:
            ld_json = None

    title = get_title(ld_json, soup)
    desc = get_desc(ld_json, soup)
    date = get_date(ld_json, soup)

    return {
        'title': sanitize(title),
        'desc': sanitize(desc),
        'date': date,
    }


def get_title(ld_json, soup):
    # Get title from meta tags
    for place in [
        soup.find('meta', {'property': 'og:title'}),
        soup.find('meta', {'property': 'twitter:title'}),
        soup.find('meta', {'name': 'title'}),
        soup.find('meta', {'name': 'DC.Title'}),
    ]:
        if place is not None:
            return place['content']

    # Get title from JSON:
    for prop in ['headline', 'alternativeHeadline', ]:
        if ld_json is not None and prop in ld_json:
            return ld_json[prop]
    # Last chance: title tag
    if soup.title is not None:
        return soup.title.string

    return None


def get_desc(ld_json, soup):
    # Get desc from meta tags
    for place in [
        soup.find('meta', {'property': 'og:description'}),
        soup.find('meta', {'property': 'twitter:description'}),
        soup.find('meta', {'name': 'description'}),
        soup.find('meta', {'name': 'DC.Description'}),
    ]:
        if place is not None:
            return place['content']
    # Get title from JSON:
    for prop in ['description', 'abstract', ]:
        if ld_json is not None and prop in ld_json:
            return ld_json[prop]

    return None


def get_date(ld_json, soup):
    # Date handling from meta tag
    for place in [
        soup.find('meta', {'property': 'article:published_time'}),
        soup.find('meta', {'name': 'date'}),
        soup.find('meta', {'name': 'DC.Date'}),
    ]:
        if place is not None:
            try:
                return parse(place['content'])
            except ParserError:
                pass
    # Get date from json
    for prop in ['datePublished', 'dateCreated', 'dateModified', ]:
        if ld_json is not None and prop in ld_json:
            try:
                return parse(ld_json[prop])
            except ParserError:
                pass

    return None


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
        date = date - date.utcoffset()
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
