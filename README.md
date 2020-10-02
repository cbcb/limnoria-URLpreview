This plugin looks for an URL posted to channels and responds with a preview of the content.

Only the first URL in each message is previewed.

# Supported Previewers

## Generic

This is the previewer for everything that hasn't a specific previewer.
It assumes the URL points to an HTML document and searches for tags
like <title> and <meta> tags that describe the document.

## Twitter
**Requires API key**
Previews Twitter Status ("Tweets) and Profiles links.

# Requirements

* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse HTML with the `generic` extractor
* [regex](https://bitbucket.org/mrabarnett/mrab-regex/src/hg/) – because regular `re` doesn't handle unicode properly
* Install [humanize](https://github.com/jmoiron/humanize/) to enable nicer timestamps, like "yesterday" instead of a date string.

These can be installed with pip like this
    pip install beautifulsoup4 humanize regex

# Limitations

* This plugin only looks at the first thing that looks vaguely like a URL per message, and gives up if that string isn't a URL.
* some websites don't return anything helpful to a user agent that has JS disabled. Such websites can be added to the blacklist.

# Security

The generic extractor GETs arbitrary URLs.
If the bot can access anything via http(s) that's sensitive and not available
from the general internet, it might be possible for a user to trick it into doing something nasty.
