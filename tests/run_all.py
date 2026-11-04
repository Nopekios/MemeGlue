import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "examples")
INTERP = os.path.join(ROOT, "meme_interpreter.py")

failed = 0
names = sorted(n for n in os.listdir(EXAMPLES) if n.endswith(".meme"))
for name in names:
    path = os.path.join(EXAMPLES, name)
    r = subprocess.run(
        [sys.executable, INTERP, path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    ok = r.returncode == 0
    if not ok:
        failed += 1
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        print(r.stderr)

print("-" * 32)
print("all " + str(len(names)) + " examples passed" if failed == 0 else str(failed) + " example(s) failed")
sys.exit(1 if failed else 0)
