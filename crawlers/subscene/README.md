

## File summary 
   * `data/crawled_jp_results/*`: manually downloaded search result pages. pages come from a query for japanese subs
   * `extract_page_urls.py`: takes the above result pages as input. greps each for links to download pages
   * `get_english_seeds.py`: creates parallel en download pages for each jp download page
   * `data/urls/*`: all the download pages for en & jp
   * `crawler.py`: steps through each download page, downloading subs and joining on title as you go. this script optionally lets you skip to an artbitrary title number, in case you had to cut a run short or something.


## Instructions

`python extract_page_urls.py > data/seeds/jp.txt`

`python get_english_seeds.py data/seeds/jp.txt > data/seeds/en.txt`

`python download_subs.py data/seeds/jp.txt data/seeds/jp.txt [OPTIONAL INDEX TO START AT]`