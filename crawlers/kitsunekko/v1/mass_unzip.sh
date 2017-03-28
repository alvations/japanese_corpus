# seems like some archives made it through the parser for kitsunekko...
# not too suprising, my parser is fairly brittle after all.
# these commands clean up all the unextracted archives 


cd ~/Documents/kitsunekko_corpus;

find . -name "*.zip" | while read filename; do unzip -o -d "`dirname "$filename"`" "$filename"; done;

find . -name "*.7z" | while read filename; do 7za x -o"`dirname "$filename"`" "$filename"; done;

find . -name '*.rar' -execdir unrar e {} \;