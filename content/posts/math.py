import sys

for i in range(1,len(sys.argv)):
    with open(sys.argv[i], 'r') as f:
        data = f.readlines()

    left = True
    lines = []
    for line in data:
        if line.startswith('$$'):
            if left:
                lines.append('\n<div>\n')
            lines.append(line)
            left = not left
            if left:
                lines.append('</div>\n\n')
        else:
            lines.append(line)
    
    with open(sys.argv[i], 'w') as f:
        f.writelines(lines)
