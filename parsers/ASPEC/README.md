
This directory contains scripts for parsing ASPEC corpus data.

`parse_aspec.py` is a script that takes in a `|||`-seperated ASPEC dataset, e.g.
```
0.879807692307692 ||| N-85A0404936 ||| 3 ||| æåに，åæåæについてèè ||| Finally, the future perspective is described.
```

and produces our internal corpus file format, which is a pair of matching corpus files, one sentence per line. 