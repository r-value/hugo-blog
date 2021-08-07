import sys

for i in range(1,len(sys.argv)):
    with open(sys.argv[i], 'r') as f:
        buf = f.readlines()

    lines = []
    for line in buf:
        if line.startswith('**注: 本文迁移自'):
            lines.append('{{< admonition type=info title="迁移提示" open=true >}}\n')
            lines.append(line.replace('注: ', ''))
            lines.append('{{< /admonition >}}\n')
        else:
            lines.append(line)

    with open(sys.argv[i], 'w') as f:
        f.writelines(lines)
