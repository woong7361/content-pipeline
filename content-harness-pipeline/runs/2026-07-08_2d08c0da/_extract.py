import re
p=r"C:/Users/PC-220627-03/Desktop/project/my/architecture-thinking/content-harness-pipeline/runs/2026-07-08_2d08c0da/output/index.html"
h=open(p,encoding="utf-8").read()
m=re.search(r"<script>(.*)</script>", h, re.S)
open(r"C:/Users/PC-220627-03/Desktop/project/my/architecture-thinking/content-harness-pipeline/runs/2026-07-08_2d08c0da/_check.js","w",encoding="utf-8").write(m.group(1))
print("bytes", len(h))
print("scenes:", re.findall(r'data-qa-scene="([^"]+)"', h))
print("has hook:", "window.__contentHarnessShowScene" in h)
print("asset refs:", sorted(set(re.findall(r'assets/([a-z0-9_]+\.png)', h))))
