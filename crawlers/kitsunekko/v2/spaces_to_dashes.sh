
find "$1" -type f | while read file; do
    mv "$file" `echo "$file" | tr ' ' '-'`
done
