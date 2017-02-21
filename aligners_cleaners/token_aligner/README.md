## Token Aligner

This paper [[PDF]](https://aclweb.org/anthology/C/C94/C94-2175.pdf) outlines a DP procedure for aligning sentences. 

This paper [[PDF]](https://pdfs.semanticscholar.org/d7a4/97cd9de61617ba55002d0db3435f64149ea0.pdf) and this paper [[PDF]](https://pdfs.semanticscholar.org/e7e8/9205652c87a559f66f9126827a47366591c5.pdf) build on that by presenting a way to score the quality of previously aligned sentences. This method will hencefourth be referred to as the *token aligner*.

## Algorithm Description

It's pretty straightforward. It basically works by counting the number of tokens that could be a translation pair and normalizing twice (once by possible num translation pairs for each token, and again by num tokens in the target sentences). Note, though, the following preproccessing steps 

* Tokenize JP, EN sentences
* Extract *content words* from the JP sentence (nouns, roots of verbs, adjectives. No okurigana)
* Obtain *lemmas* of words in the EN sentence

These JP content words and EN lemmas for each sentence pair are the `J_i` and `E_i` referred to below.
<br/>
<br/>

![Algorithm description](https://raw.githubusercontent.com/rpryzant/japanese_corpus/master/aligners_cleaners/token_aligner/static/fig1.png)

