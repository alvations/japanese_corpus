# ==== DESCRIPTION
# recursively swaps spaces for underscores in filenames 
#
# ==== USAGE:
# ./spaces_to_underscores.sh [conversion_root/]

subs_root="$1"

find "$1" -type f | while read file; do
    mv "$file" `echo $file | tr ' ' '_'`
done