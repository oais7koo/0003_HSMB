import io, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

sq = oh = dash = star = other = 0
orphan_lines = []
in_code = False

for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith("```"):
        in_code = not in_code
        continue
    if in_code or not s or s.startswith(("|", "#", "---", ">", "[그림", "*(")):
        continue
    if s.startswith("□"):
        sq += 1
    elif s.startswith("○"):
        oh += 1
    elif s.startswith("- ") or s == "-":
        dash += 1
    elif s.startswith("* "):
        star += 1
    elif re.match(r"^[가-힣A-Za-z]", s) and len(s) > 20:
        other += 1
        if other <= 20:
            orphan_lines.append((i, s[:80]))

print(f"□ 소제목: {sq}건")
print(f"○ 중항목: {oh}건")
print(f"- 소항목: {dash}건")
print(f"* 출처주석: {star}건")
print(f"마커없는 본문 후보: {other}건")
for ln, body in orphan_lines:
    print(f"  line {ln}: {body}")
