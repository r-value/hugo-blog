import sys

for i in range(1,len(sys.argv)):
    with open(sys.argv[i], 'r') as f:
        buf = f.readlines()

    lines = []
    begin = False
    for line in buf:
        if line.startswith('```mermaid'):
            lines.append(line.replace('```mermaid', '{{< mermaid >}}'))
            begin = True
        elif line.startswith('```') and begin:
            begin = False
            lines.append(line.replace('```', '{{< /mermaid >}}'))
        else:
            lines.append(line)

    with open(sys.argv[i], 'w') as f:
        f.writelines(lines)
