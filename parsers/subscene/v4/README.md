
### Description

`parser_v4` is the main driver program for this stuff. The parser aligns matching `.srt` files. It then pulls out matching captions from those files. 

* File matching is done with fuzzy string matching on filepaths
* Caption matching is done with crude word-for-word translation, then TF-IDF similarity on the resulting translations


### Requirements

* gawk: `sudo apt-get install gawk`
* joblib: `pip install joblib`
* pysrt: `pip install pysrt`
* numpy: `pip install numpy`
* tqdm: `pip install tqdm`
* guessit: `pip install guessit`
* nltk: `pip install nltk`
* stemmer: `pip install Stemmer`

### Usage: 

`python parser_v4.py [data_loc] [en_out] [ja_out] -t [num_threads (OPTIONAL)]`

**Precondition**: subfiles are organized as follows:
```
root/   (this is your arg)
    title_i/ 
       ja/ 
         .srt files  
       en/
          files                                                                                                                   
    ...