import re
import sys

for i in range(1,len(sys.argv)):
    with open(sys.argv[i], 'r') as f:
        buf = f.read()

    with open(sys.argv[i], 'w') as f:
        f.write(re.sub(r'(?!\$\$)(?!\\\$)\$.*?\$(?!\\\$)(?!\$\$)', lambda match: match.group(0).replace('*', '\\*'), buf))
