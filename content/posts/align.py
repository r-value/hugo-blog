import sys

for i in range(1,len(sys.argv)):
    with open(sys.argv[i], 'r') as f:
        data = f.readlines()

    lines = []
    for line in data:
        if line.startswith(r'\begin{align}') or line.startswith(r'\end{align}'):
            lines.append(line.replace('align','aligned'))
        else:
            lines.append(line)
    
    with open(sys.argv[i], 'w') as f:
        f.writelines(lines)
