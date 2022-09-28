import re
file_name = 'aSH#600000.txt'

k = re.match("^SH.*?\.txt$", file_name)
print(k)