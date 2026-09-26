import re, sys
src = open(sys.argv[1]).read().split('\n')
pat = re.compile(r'^(?!\s)(?!(?:struct|enum|class|if|for|while|switch|return|else|template)\b)([A-Za-z_][\w:<>\s\*&,]*?[\s\*&]+(\w+)\s*\([^;{}]*\))\s*\{')
protos, first = [], None
for i, l in enumerate(src):
    m = pat.match(l)
    if m:
        if first is None: first = i
        sig = re.sub(r'=\s*[^,)]+', '', m.group(1))   # drop default args
        protos.append(sig + ';')
out = src[:first] + protos + src[first:]
open(sys.argv[2], 'w').write('\n'.join(out))
print(f"{len(protos)} prototypes inserted above line {first+1}")
