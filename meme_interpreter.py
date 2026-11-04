import sys

sys.stdout.reconfigure(encoding="utf-8")

VARS = {}

SAY = "say: "
NEED = "need: "
WHEN = "when: "
NO = "no:"
LOOP = "loop: "
ADD = "add: "
SUB = "sub: "
MUL = "mul: "
DIV = "div: "


class MemeGlueError(Exception):
    pass


class StopLoop(Exception):
    pass


def eval_text(raw):
    parts = raw.split('"')
    if len(parts) % 2 == 0:
        raise MemeGlueError("双引号没有闭合 -> " + raw)
    out = []
    for i in range(len(parts)):
        if i % 2 == 0:
            out.append(parts[i])
        else:
            out.append(get_var(parts[i].strip()))
    return "".join(out)


def get_var(name):
    if name not in VARS:
        raise MemeGlueError("变量 " + name + " 不存在")
    return str(VARS[name])


def to_num(tok):
    tok = tok.strip()
    if tok.startswith('"') and tok.endswith('"'):
        tok = get_var(tok[1:-1])
    return float(tok)


def fmt(x):
    return str(int(x)) if x == int(x) else str(x)


def test_cond(raw):
    body = raw.strip()
    for op in (">=", "<=", "==", "!=", ">", "<"):
        i = body.find(op)
        if i > 0:
            a = to_num(body[:i])
            b = to_num(body[i + len(op):])
            if op == ">=":
                return a >= b
            if op == "<=":
                return a <= b
            if op == "==":
                return a == b
            if op == "!=":
                return a != b
            if op == ">":
                return a > b
            return a < b
    raise MemeGlueError("条件无法解析 -> " + body)


def arith(op, body, no):
    parts = body.split()
    if len(parts) != 3:
        raise MemeGlueError("第 %d 行：%s 需要 3 个参数" % (no, op))
    a = to_num(parts[0])
    b = to_num(parts[1])
    name = parts[2]
    if op == "add":
        r = a + b
    elif op == "sub":
        r = a - b
    elif op == "mul":
        r = a * b
    else:
        if b == 0:
            raise MemeGlueError("第 %d 行：除数不能为 0" % no)
        r = a / b
    VARS[name] = fmt(r)


def parse(path):
    root = {"head": -1, "body": "", "no": 0, "kids": []}
    stack = [root]
    for no, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\r\n")
        if not line.strip():
            continue
        if ";" in line or "," in line:
            raise MemeGlueError(
                "第 %d 行：MemeGlue 语言禁止使用逗号和分号，请把你的键盘按键抠掉" % no
            )
        ind = len(line) - len(line.lstrip(" "))
        body = line.lstrip(" ")
        while ind <= stack[-1]["head"]:
            stack.pop()
        node = {"head": ind, "body": body, "no": no, "kids": []}
        stack[-1]["kids"].append(node)
        stack.append(node)
    return root["kids"]


def exec_block(nodes):
    i = 0
    while i < len(nodes):
        node = nodes[i]
        body = node["body"]
        if body.startswith(WHEN):
            ok = test_cond(body[len(WHEN):])
            i += 1
            twin = nodes[i] if i < len(nodes) and nodes[i]["body"].startswith(NO) else None
            if ok:
                exec_block(node["kids"])
            elif twin:
                exec_block(twin["kids"])
            if twin:
                i += 1
            continue
        if body.startswith(LOOP):
            run_loop(body[len(LOOP):], node["kids"], node["no"])
        elif body.startswith(NO):
            raise MemeGlueError("第 %d 行：no 没有匹配的 when" % node["no"])
        elif body.strip() == "stop":
            raise StopLoop
        else:
            exec_stmt(body, node["no"])
        i += 1


def run_loop(arg, kids, no):
    arg = arg.strip()
    if arg == "always":
        while True:
            try:
                exec_block(kids)
            except StopLoop:
                return
    if arg.lstrip("-").isdigit():
        for _ in range(int(arg)):
            try:
                exec_block(kids)
            except StopLoop:
                return
        return
    while test_cond(arg):
        try:
            exec_block(kids)
        except StopLoop:
            return


def exec_stmt(line, no):
    if line.startswith(SAY):
        print(eval_text(line[len(SAY):]))
    elif line.startswith(NEED):
        name, value = line[len(NEED):].split(" ", 1)
        VARS[name] = eval_text(value.strip()) if '"' in value else value.strip()
    elif line.startswith(ADD):
        arith("add", line[len(ADD):], no)
    elif line.startswith(SUB):
        arith("sub", line[len(SUB):], no)
    elif line.startswith(MUL):
        arith("mul", line[len(MUL):], no)
    elif line.startswith(DIV):
        arith("div", line[len(DIV):], no)
    else:
        raise MemeGlueError("第 %d 行：无法识别的语句 -> %s" % (no, line))


if __name__ == "__main__":
    exec_block(parse(sys.argv[1] if len(sys.argv) > 1 else "hello.meme"))
