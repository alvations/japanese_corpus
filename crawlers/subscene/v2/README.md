

### Requirements

* selenium: `pip install selenium`
* chrome webdriver: `brew install ChromeDriver`
* python-magic: `pip install python-magic`
* magic: `brew install libmagic`
* tqdm: `pip install tqdm`
* pyunpack: `pip install pyunpack`

### Steps:

```
# crawl ja an en subs
python crawler.py urls/ja.txt > JA_LOG
python crawler.py urls/en.txt > EN_LOG

# convert to utf8
find out/ -type f | python all_to_utf8.py


```

### Results/files:


### Crawling process:

1. Visit [subscene browse page](https://subscene.com/browse)
2. Filters -> japanese -> save
3. Download each result page
4. Follow steps outlined in `../v1/` to get download pages (in `urls/`)
5. download each resource, unzip, and convert to SRT with `crawler.py`


### Resources

* might be useful: http://sapir.psych.wisc.edu/wiki/index.php/Extracting_and_analyzing_subtitles
