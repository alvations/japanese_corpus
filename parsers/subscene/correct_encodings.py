"""
Many subtitle files have weird ass encodings like SHIFT-JIS. This file should
  bring everything over to utf-8

=== Example usage:

find ~/Documents/japanese_corpus/ -type f | python correct_encodings.py

=== packages used:

https://github.com/chardet/chardet to detect encodings

$ chardetect the_pianist_disk1.srt 
>>>> the_pianist_disk1.srt: SHIFT_JIS with confidence 0.99

iconv -f SHIFT-JIS -t UTF-8 the_pianist_disk1.srt > out.txt
"""



fp = sys.argv[1]
print 'converting %s' % fp
output = os.popen('chardetect %s' % fp).read()
charset = output.split(':'[1].strip().split(' ')[0])              # ugly but chardetect's output is determanistic and meh
os.system('iconv -f %s -t UTF-8 %s > %s' % (charset, fp, fp)  # overwrite with utf-8
print 'converted %s to UTF-8. wrote to %s' % (charset, fp)


