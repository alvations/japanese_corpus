### Requirements

- Jupyer Notebook
- Selenium: `pip install selenium`
- Chrome webdriver: `brew install ChromeDriver`

### Crawling Process

1. Visit [D-Addicts Listing Page](http://www.d-addicts.com/forums/page/subtitles?sid=c00e06662e59c449c2b2814b22e7bc90)
2. Get all links on the page listed under "Japanese" and "English" subs. Each link corresponds to a forum topic with uploaded SRTs.
3. For each forum link, visit the post URL and scrape all "download urls" from the post.
4. Write an entry to `download_links.jsonlines` with information about SRT downloads links and drama name.
5. Parse the `download_links.jsonlines` with [jq](https://stedolan.github.io/jq/) and download all SRTs using curl/wget. (TODO)
6. Use information in the JSON data and SRT files itself to match English and Japanese Subtitles (TODO)

