# Description

This project aims to produce a large corpus of parallel EN-JA sentences. It is motivated by the paucity of freely available data in machine translation, especially for uncommon language pairs. 


We have ~3.4 million sentences now, making it **the biggest EN-JA corpus of all time!**

We harvested these data by 

1. Crawling the web for English and Japanese subtitles
2. Matching subtitles that correspond to the same title and spoken phrase
3. Cleaning the matched data




# Status

| Source                                                                                                     | Notes                                                                                                            | Status                                          |
|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| [d-addicts](http://www.d-addicts.com/forums/page/subtitles?sid=c00e06662e59c449c2b2814b22e7bc90#Japanese) | * ~600 dramas, ~5M sentance pairs,<br>  * fansubs,<br> * japanese & english subs in different parts of same page | * **crawled**<br/>* **parsed** <br/>* **matched**<br/>* 620408 pairs                                  |
| [OpenSubtitles](http://opus.lingfil.uu.se/OpenSubtitles2016.php)                                         | * 1.4M sentance pairs,<br> * professional translations, 1-1 en/jp matching (in same file)                        | * **crawled**<br/>* **parsed**<br/>* **matched**<br/>* * 1381339 pairs  |
| [kitsunekko](http://kitsunekko.net/dirlist.php?dir=subtitles%2Fjapanese%2F)                              | * ~600 dramas/movies (largeley incomplete), ~3M pairs<br> * fansubs<br> * en/jp lists on different pages         | * **crawled**<br/>* **parsed**<br/>* **matched(?)** <br/> * 161792 |
| [subscene](http://v2.subscene.com/subtitles/a/japanese.aspx)                                             | * ~2000 movies/shows, ~5M raw sentance pairs, ~1.3M usable pairs<br> * mix of fansubs & professional translations                       | * **crawled**<br/>* **parsed**<br/>* **matched(?)** <br/> * 810678 pairs |



