
subs_root="$1"

find "$1" -type f | while read file; do
    mv "$file" `echo $file | tr ' ' '_'`
done