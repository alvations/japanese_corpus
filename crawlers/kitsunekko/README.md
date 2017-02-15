## File descriptions

* `parse_and_match_links.py`: crawling script
* {`en_links.txt`, `jp_links.txt`}: lines of html containing links to subtitle download pages
* {`en_sub_root.html`, `jp_sub_root.html`}: dump of kitsunikko search pages for "japaense" and "english"

## Behavior

`parse_and_match_links.py` takes the html links in `*_links.txt`, downloads the subs from each page, and matches them based on title.

It can be run with `python parse_and_match_links.py en_links.txt jp_links.txt`
