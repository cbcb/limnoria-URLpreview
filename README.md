This is a plugin for the [Limnoria IRC Bot](https://github.com/ProgVal/Limnoria). It looks for URLs posted in the channel and responds with a preview of the linked content.

## Bundled Previewers

### Generic

This is the previewer for everything that hasn't a specific previewer.
It assumes the URL points to an HTML document and searches for tags
like \<title\> and \<meta\> tags that describe the document.

Currently searches for name, date and description from these tags:
* [schema.org](https://schema.org/) data found in [json-ld](https://json-ld.org/) `<script>` tags
* `<title>`, `<meta description="name">`, `<meta description="description">` and `<meta description="date">` tags
* [Twitter Summary Cards](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/summary) `<meta>` tags
* [Open Graph](https://ogp.me/) `<meta>` tags
* [Dublin Core](https://www.dublincore.org) `<meta>` tags


### Twitter
**Requires API key**

previews Twitter Status ("Tweets") and Profiles links.

### YouTube
**Requires API key**

previews YouTube video links.

### NPR

rewrites URLs to `npr.org` to `text.npr.org` equivalents to avoid the cookie consent page, then uses the `generic` previewer on them.

## Requirements
* [requests](https://2.python-requests.org/en/master/) to connect
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to parse HTML with the `generic` extractor
* [python-dateutil](https://github.com/dateutil/dateutil/) for parsing date strings
* [regex](https://bitbucket.org/mrabarnett/mrab-regex/src/hg/) – because regular `re` doesn't handle unicode properly
* Install [humanize](https://github.com/jmoiron/humanize/) to enable nicer timestamps, like "yesterday" instead of a date string.

## Installation

Install the requirements in the environment where limnoria runs – if you use pip you can copy this:

    pip install beautifulsoup4 humanize python-dateutil regex

Then place the files from this repo into `plugins/URLpreviewer` and tell your bot to `load URLpreviewer`.

## Configuration variables
| Name              | Type    | Scope   | Default | Description                                                                       |
|-------------------|---------|---------|---------|-----------------------------------------------------------------------------------|
| `enabled`         | Boolean | channel | `True`  | controls if the plugin is enabled for the channel                                 |
| `generic_enabled` | Boolean | global  | `True`  | controls if the `generic` previewer is enabled                                    |
| `twitter_enabled` | Boolean | global  | `False` | controls if the `twitter` previewer is enabled                                    |
| `twitter_api_key` | String  | global  | `""`    | holds the Twitter API OAuth 2.0 Bearer token required for the `twitter` previewer |
| `youtube_enabled` | Boolean | global  | `False` | controls if the `youtube` previewer is enabled                                    |
| `youtube_api_key` | String  | global  | `""`    | holds the Google Simple API access key required for the `youtube` previewer       |

## Limitations

* This plugin only looks at the first thing that looks vaguely like a URL per message, and gives up if that string can't be previewed.
* some websites don't return anything helpful to a user agent that has JS disabled. Such websites can be added to the blacklist in `previewers/generic.py`.

## Security

The generic extractor GETs arbitrary URLs.
If the bot can access anything via http(s) that's sensitive and not available
from the general internet, it might be possible for a user to trick it into doing something nasty.

## Useful links

* https://modern.ircdocs.horse/formatting.html

## Acknowledgments

Loading of the previewers is based on Guido Diepen's blog post [Implementing a simple plugin framework in Python](https://www.guidodiepen.nl/2019/02/implementing-a-simple-plugin-framework-in-python/). Thank you!
