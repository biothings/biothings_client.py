import sys

if sys.version_info[0] == 3:
    str_types = str
else:
    str_types = (str, unicode)  # NOQA
