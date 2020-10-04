This plugin looks for an URL posted to channels and responds with a preview of the content.

Only the first URL in each message is previewed.

# Supported Previewers

## Generic

This is the previewer for everything that hasn't a specific previewer.
It assumes the URL points to an HTML document and searches for tags
like \<title\> and \<meta\> tags that describe the document.

Currently searches for name, date and description from these tags:
* `<title>`, `<meta description="name">`, `<meta description="description">` and `<meta description="date">` tags
* [Twitter Summary Cards](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/summary) `<meta>` tags
* [Open Graph](https://ogp.me/) `<meta>` tags


## Twitter
**Requires API key**

previews Twitter Status ("Tweets") and Profiles links.

## YouTube
**Requires API key**

Previews YouTube video links.

# Requirements

* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse HTML with the `generic` extractor
* [python-dateutil](https://github.com/dateutil/dateutil/) for parsing date strings
* [regex](https://bitbucket.org/mrabarnett/mrab-regex/src/hg/) – because regular `re` doesn't handle unicode properly
* Install [humanize](https://github.com/jmoiron/humanize/) to enable nicer timestamps, like "yesterday" instead of a date string.

These can be installed with pip like this

    pip install beautifulsoup4 humanize python-dateutil regex


# Configuration variables
| Name              | Type    | Scope   | Default | Description                                                                       |
|-------------------|---------|---------|---------|-----------------------------------------------------------------------------------|
| `enabled`         | Boolean | channel | `True`  | controls if the plugin is enabled for the channel                                 |
| `generic_enabled` | Boolean | global  | `True`  | controls if the `generic` previewer is enabled                                    |
| `twitter_enabled` | Boolean | global  | `False` | controls if the `twitter` previewer is enabled                                    |
| `twitter_api_key` | String  | global  | `""`    | holds the Twitter API OAuth 2.0 Bearer token required for the `twitter` previewer |
| `youtube_enabled` | Boolean | global  | `False` | controls if the `youtube` previewer is enabled                                    |
| `youtube_api_key` | String  | global  | `""`    | holds the Google Simple API access key required for the `youtube` previewer       |

# Limitations

* This plugin only looks at the first thing that looks vaguely like a URL per message, and gives up if that string can't be previewed.
* some websites don't return anything helpful to a user agent that has JS disabled. Such websites can be added to the blacklist in `previewers/generic.py`.

# Security

The generic extractor GETs arbitrary URLs.
If the bot can access anything via http(s) that's sensitive and not available
from the general internet, it might be possible for a user to trick it into doing something nasty.

# Useful links

* https://modern.ircdocs.horse/formatting.html

# Acknowledgments

Loading of the previewers is based on Guido Diepen's blog post [Implementing a simple plugin framework in Python](https://www.guidodiepen.nl/2019/02/implementing-a-simple-plugin-framework-in-python/). Thank you!
