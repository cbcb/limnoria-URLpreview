## Dev version
* `generic` previewer: now favours other tags over json-ld due to some websites offering very poor data there
* `generic` previewer: now understands even more `meta`-tags related to dates
* `generic` previewer: corrected the assumption that pages wouldn't contain `null` values in ld-json
* `generic` previewer: now tries several different user agents if no interesting metadata is found

## Version 1.1
* added previewer for `npr.org`
* `generic` previewer now understands json-ld
* `generic` previewer now understands `<meta property="article:published_time" …>`  OpenGraph tags 
* `generic` previewer now understands Dublin Core tags
* Updated ignore list for `generic` previewer

## Version 1.0

* First release
* Comes with previewers `generic`, `YouTube` and `Twitter`
* Also comes with a minimal `example` previewer
