"""人工复核辅助：按信号导出每条候选的判定上下文。
用法：python review_context.py candidates.jsonl <日志目录> <输出目录>
"""
import json, sys, glob, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_alignment import load_turns

cands, logdir, outdir = sys.argv[1:4]
os.makedirs(outdir, exist_ok=True)
cache, files = {}, {}
def clip(s, n):
    s = re.sub(r"\s*\n\s*", " ⏎ ", s.replace("\r", "\n").replace("\x00", ""))
    return re.sub(r"[ \t　]{3,}", "  ", s)[:n]
for n, l in enumerate(open(cands, encoding="utf-8")):
    c = json.loads(l)
    f = glob.glob(os.path.join(logdir, c["session"] + "*.jsonl"))[0]
    if f not in cache:
        cache[f] = load_turns(f)
    turns, results = cache[f][0], cache[f][1]
    t = turns[c["turn"]]
    if c["signal"] not in files:  # 不能用 setdefault：它每次都会重新 open(..., "w")，截断文件留下 NUL 空洞
        files[c["signal"]] = open(os.path.join(outdir, f"review_{c['signal']}.md"), "w", encoding="utf-8")
    out = files[c["signal"]]
    out.write(f"\n## id={n} {c['signal']} {c.get('category','')} {c.get('flags','')} session={c['session']} turn={c['turn']} ts={c['ts']}\n")
    out.write("用户原话（本会话截至本轮，旧→新）：\n")
    for k in range(max(0, c["turn"] - 4), c["turn"] + 1):
        out.write(f"- U{k}: {clip(turns[k]['user'], 500)}\n")
    if c["signal"] == "UA":
        before = [e[1] for e in t["events"][: c["ev"]] if e[0] == "text"]
        out.write(f"动作前助手最后一段话：{clip(before[-1], 500) if before else '（无）'}\n")
        out.write(f"动作：{c['tool']} → {clip(c['what'], 500)}\n结果报错：{c['failed']}\n")
    elif c["signal"] == "FA":
        out.write(f"overlap={c['overlap']}\n被判为归因的句子：{clip(c['sentence'], 400)}\n")
    else:
        texts = [e[1] for e in t["events"] if e[0] == "text"]
        tools = [(e[2], clip(str(e[3].get('command') or e[3].get('file_path') or ''), 140), results.get(e[1], (None,))[0]) for e in t["events"] if e[0] == "tool"]
        out.write("本轮最后 6 次工具调用（名称, 参数, 是否报错）：\n")
        for x in tools[-6:]:
            out.write(f"  - {x}\n")
        out.write(f"mentions_failure={c.get('mentions_failure')}\n最终回复：{clip(texts[-1], 1500)}\n")
for fh in files.values():
    fh.close()
print({k: v.name for k, v in files.items()})
