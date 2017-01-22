## 2.1M sentance pairs so far

| Source                                                                                                     | Notes                                                                                                            | Status                                          |
|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| [d-addits](http://www.d-addicts.com/forums/page/subtitles?sid=c00e06662e59c449c2b2814b22e7bc90#Japanese) | * ~600 dramas, ~5M sentance pairs,<br>  * fansubs,<br> * japanese & english subs in different parts of same page | not started                                     |
| [OpenSubtitles](http://opus.lingfil.uu.se/OpenSubtitles2016.php)                                         | * 1.4M sentance pairs,<br> * professional translations, 1-1 en/jp matching (in same file)                        | * sentances scraped<br> * have to write parsers |
| [kitsunekko](http://kitsunekko.net/dirlist.php?dir=subtitles%2Fjapanese%2F)                              | * ~600 dramas/movies (largeley incomplete), ~3M pairs<br> * fansubs<br> * en/jp lists on different pages         | not started                                     |
| [nihongo-jimaku](http://nihongo-jimaku.blogspot.jp/)                                                     | * ~225 movies (.25M sentances),<br> * jp only, no en                                                             | debating on whether to include these            |
| [subscene](http://v2.subscene.com/subtitles/a/japanese.aspx)                                             | * ~2000 movies/shows, ~5M raw sentance pairs, ~1.6M usable pairs<br> * mix of fansubs & professional translations                       | * **crawled**<br>* standardized charsets<br>* `.srt` parser done<br>* caption cleaner **done** <br>* caption matcher v1 done <br> * **DONE FOR NOW** |
| [TED talks](https://www.ted.com/talks) | ~100k pairs | * **CRAWLED**<br> * parser v1 done <br> * ~.5M sentance pairs |


### Numbers to beat

I'd like to make this the biggest open-source Japanese-English corpus out there. Looks like ~1M sentance pairs is the number to beat: http://www.phontron.com/japanese-translation-data.php?lang=en

### Roadblocks

* accessing paired translations
  * soln: crawl sub sites, pull down en and jp subs for matched films/tv shows
* Poor translations. I.e. I've seen subs that were generated by running another language's subs through google translate
  * soln: run language model over each movie/show's corpus. if average sentance quality is below some threshold, throw it out
* En/Jp subtitle mismatch. Sometimes the srt files don't have the same number of entries, and entries don't correspond to the same times. 
  * soln: sentance alignment model. run encoder over en/jp srt files. pair up nearby sentances with similar thought vectors
* romanji transliterations
  * soln: throw out



### file formats
* smi
* tmx
* ass
* **srt** (95.3% of subscene subfiles...only use these?)


### observed problems with downloaded subs
* unaligned translations
* transliteration of japanese characters
* broken character encodings (gobblygook)
* stuff that doesn't belong (i.e. "TRANSLATED BY ______")
