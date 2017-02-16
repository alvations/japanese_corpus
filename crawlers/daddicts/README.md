### Requirements

- Jupyer Notebook
- Selenium: `pip install selenium`
- Chrome webdriver: `brew install ChromeDriver`
- SRT/ASS libraries: `pip install pysrt ass`

### Results/Files

- Aligned Sentences (~600k): https://drive.google.com/open?id=0B_bZck-ksdkpWW5SOTJqS0R1eVk
  - Not cleaned
- Cleaned Subtitles (260MB): https://drive.google.com/open?id=0B_bZck-ksdkpRmlNQmNISWN2OFU
  - Added `.srt` and `.ass` file extensions
  - Removed duplicate files
  - Removed files that are not SRT or ASS subtitles
- Raw Subtitle Downloads:
  - Not cleaned
  - Japanese Subs (124MB) https://drive.google.com/open?id=0B_bZck-ksdkpVTdESFhFYURqMzA
  - English Subs (542MB): https://drive.google.com/open?id=0B_bZck-ksdkpNzllSFBNOGM2blU


### What could be improved

- Subtitle distance metric (currently using Hamming distance) could be changed. See [cdist](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html) for available metrics.
- Distance threshold can be tuned to be more strict/lenient with matching
- Handle downloaded zip/rar/tar/archive files that may contain multiple subtitles titles. Currently these are thrown away.
- Better data cleaning.


### Crawling Process

1\. Visit [D-Addicts Listing Page](http://www.d-addicts.com/forums/page/subtitles?sid=c00e06662e59c449c2b2814b22e7bc90)

2\. Get all links on the page listed under "Japanese" and "English" subs. Each link corresponds to a forum topic with uploaded SRTs.

3\. For each forum link, visit the post URL and scrape all "download urls" from the post.

4\. Write an entry to `download_links.jsonlines` with information about SRT downloads links and drama name.

5\. Parse the `download_links.jsonlines` with [jq](https://stedolan.github.io/jq/) and download all SRTs using curl/wget.

```
cat download_links_ja.jsonlines | jq -r '.srt_urls[]' > raw_links_ja.txt
cat download_links_en.jsonlines | jq -r '.srt_urls[]' > raw_links_en.txt
wget -nc -w 1 --random-wait -P ja -i raw_links_ja.txt
wget -nc -w 1 --random-wait -P en -i raw_links_en.txt
```

6\. Use information in the JSON data and SRT files itself to match English and Japanese Subtitles. Note, you can use the downlaod file ids to match files back to JSON records.

### Some Statistics

- 737 Japanese subbed dramas/movies
  - 4941 Japanese SRT/zip/rar files
    - `cat crawlers/daddicts/download_links_ja.jsonlines | jq '.srt_urls[]' | wc -l`
- 1883 English subbed dramas/movies
  - 19122 English SRT/zip/rar files

Conservative estimates:

- English/Japanese Overlap Esimation: 10-20%. ~2000 SRT files
- 500 lines per SRT file => `2000*500 = 1M` total aligned sentences

### Notes & Difficulties

- Some file downloads are SRT files. Some are rar/zip files that may contain multiple subtitles
- How do we match EN-JP dramas? It doesn't look like it's organized by drama so we need to match manually? Is there maybe another site that collects subtitles by drama?

