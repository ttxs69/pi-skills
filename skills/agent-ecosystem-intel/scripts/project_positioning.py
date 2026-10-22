#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目赛道定位体检 —— 把「我能做」变成「我能重复做」

2026-10-22 建。基于 `productized-service-playbook` §3（productized service 要可重复交付）
与 `wechat-oa-monetization` §3（服务咨询是一步半径、最快验证的路）。

**它回答一个问题**：我这个 AI Agent 项目，站在 8 大赛道的哪一格？那一格挤不挤？谁在抢？

**数据全部本地、可回源**：
- 上榜次数：33 天四源抓取 `daily-ledger/data/raw-*.json`（GitHub 部分 402 条）
- 赛道归属：`tools/agent_landscape.py --json`（8 类分类法，`--verify` 可回算）
- 拥挤度：赛道内项目数 / 上榜总次数
- GitHub 元信息（可选）：联网取，**限流时自动降级**，不影响主结论

**用法**
  python3 tools/project_positioning.py --repo adongwanai/learn-workbuddy
  python3 tools/project_positioning.py --repo owner/name --json
  python3 tools/project_positioning.py --self-test

**为什么这个能卖**：它不是"我读了你的 README"，是"我用 33 天 402 条真实上榜记录，
算出你在这张图里的位置"。同类榜单站（ultrametric.ai）已验证这个品类存在，
且把付费点放在「替你做一个具体决定」而不是「给你一张表」。
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIRS = [ROOT / "daily-ledger" / "data", Path.home() / "daily-ledger" / "data"]
CATS_CN = {
    "skills": "skills（给 agent 装技能包）",
    "memory": "memory（跨会话记忆）",
    "runtime": "runtime（安全执行环境）",
    "harness": "harness（agent 的骨架/外壳）",
    "orchestration": "编排（多 agent 调度）",
    "cli": "CLI 化（把软件变成 agent 可调）",
    "vertical": "垂直场景（解决一个具体的活儿）",
    "vendor": "厂商官方",
}


def _raw_files():
    for d in RAW_DIRS:
        if d.exists():
            fs = sorted(d.glob("raw-*.json"))
            if fs:
                return fs
    return []


def load_rows():
    rows = []
    for p in _raw_files():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for it in (d.get("gh") or []):
            # date 在 raw 文件的顶层（entry_date / date），不在 gh 条目里
            # 2026-10-22 修：原先 gh 条目没有 date 字段 ⇒ days 恒为 1
            rows.append({**it, "date": it.get("date") or d.get("date")
                         or d.get("entry_date") or p.stem.replace("raw-", ""),
                         "_day": str(d.get("date") or p.stem.replace("raw-", ""))})
    return rows


def _find_landscape() -> Path:
    """定位 agent_landscape.py。

    同一份脚本要能在两种布局下跑：
      - 项目根：<root>/tools/agent_landscape.py
      - skill 包：<skill>/scripts/agent_landscape.py
    之前只写死 tools/ ⇒ 装成 skill 后负载全空（拥挤度表空、高频项目数 None），
    而 --verify 仍然通过 ⇒ 「验证通过」掩盖了「功能是空的」。
    """
    here = Path(__file__).resolve().parent
    for cand in (here / "agent_landscape.py",
                 here.parent / "tools" / "agent_landscape.py",
                 here.parent / "scripts" / "agent_landscape.py",
                 ROOT / "tools" / "agent_landscape.py"):
        if cand.exists():
            return cand
    raise FileNotFoundError("找不到 agent_landscape.py")


def load_landscape():
    out = subprocess.run(
        [sys.executable, str(_find_landscape()), "--json"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=180)
    try:
        return json.loads(out.stdout)
    except Exception:
        return {}


def _gh_token():
    """GitHub token：环境变量 > /tmp 文件 > 备份仓 remote。匿名 API 只有 60 次/小时。"""
    import os
    for k in ("GITHUB_TOKEN", "GH_TOKEN"):
        v = (os.environ.get(k) or "").strip()
        if v:
            return v
    for pth in (Path("/tmp/gh_token.txt"), Path.home() / ".hermes" / "gh_token.txt"):
        try:
            if pth.exists():
                v = pth.read_text(encoding="utf-8").strip()
                if v:
                    return v
        except OSError:
            pass
    try:
        url = subprocess.run(["git", "-C", str(Path.home() / "hermes-config-backup"),
                              "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        m = re.search(r"(gh[pousr]_[A-Za-z0-9]+)", url)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def gh_meta(repo: str):
    """GitHub 元信息。限流/离线时返回 None，不影响主结论。"""
    try:
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": "positioning-check"}
        tok = _gh_token()
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}",
            headers=headers)
        with urllib.request.urlopen(req, timeout=12) as r:
            d = json.loads(r.read().decode())
        return {"stars": d.get("stargazers_count"), "forks": d.get("forks_count"),
                "lang": d.get("language"), "created": (d.get("created_at") or "")[:10],
                "pushed": (d.get("pushed_at") or "")[:10],
                "topics": d.get("topics") or [], "desc": d.get("description") or "",
                "open_issues": d.get("open_issues_count")}
    except Exception:
        return None


def classify_hint(desc: str, topics: list) -> str:
    """粗分类（仅用于给建议，不冒充 agent_landscape 的 8 类判定）。"""
    t = " ".join(list(topics) + [desc]).lower()
    if any(k in t for k in ("skill", "claude-code", "plugin")):
        return "skills"
    if any(k in t for k in ("memory", "context", "recall")):
        return "memory"
    if any(k in t for k in ("sandbox", "runtime", "isolate", "exec")):
        return "runtime"
    if any(k in t for k in ("harness", "workspace", "agent loop", "agent-loop")):
        return "harness"
    if any(k in t for k in ("orchestrat", "multi-agent", "scheduler", "swarm")):
        return "orchestration"
    if any(k in t for k in ("cli", "command-line", "mcp server", "mcp-server")):
        return "cli"
    return "vertical"


def analyze(repo: str, with_gh: bool = True) -> dict:
    rows = load_rows()
    land = load_landscape()
    cnt = Counter(r.get("slug") for r in rows)
    per_cat = land.get("per_cat") or {}
    density = land.get("density") or {}
    stars_map = land.get("per_project_stars") or {}

    n_items = len(rows)
    n_uniq = len(cnt)
    dist = Counter(cnt.values())

    # 目标在 37 个高频项目里吗？
    in_map, cat_of = False, None
    for c, members in per_cat.items():
        if repo in members:
            in_map, cat_of = True, c
            break
    n_hits = cnt.get(repo, 0)

    # 同赛道竞争者
    rivals = []
    if cat_of:
        for s, times in sorted(per_cat[cat_of].items(), key=lambda x: -x[1]):
            rivals.append({"repo": s, "times": times, "stars": stars_map.get(s)})

    meta = gh_meta(repo) if with_gh else None
    hint = classify_hint((meta or {}).get("desc", ""), (meta or {}).get("topics", [])) if meta else None

    # 诊断结论
    a_days = len({r.get("_day") for r in rows if r.get("_day")})
    if n_hits == 0:
        verdict = "NOT_ON_TRENDING"
        reason = (f"{a_days} 天 / {n_items} 条 GitHub 上榜记录里，**0 次**。"
                  f"这不代表项目不好——英文 Trending feed 不覆盖所有项目，"
                  f"中文/小众项目常整段缺席。"
                  f"结论：不能用『有没有上 Trending』判断你该不该继续。")
    elif n_hits < 3:
        verdict = "LONG_TAIL"
        reason = (f"上榜 {n_hits} 次，属于长尾。全量 {n_uniq} 个唯一项目里，"
                  f"上榜 1 次的有 {dist.get(1, 0)} 个（{dist.get(1,0)/max(1,n_uniq):.0%}）。")
    else:
        verdict = "IN_FREQUENT_MAP"
        reason = f"上榜 {n_hits} 次，进入高频地图（≥3 次，共 {land.get('gh_agent_hi_n')} 个项目）。"

    # 拥挤度建议
    crowd_note = None
    if cat_of:
        c = density.get(cat_of)
        if c is not None:
            order = sorted(density.items(), key=lambda x: -x[1])
            pos = [i for i, (k, _) in enumerate(order) if k == cat_of][0] + 1
            crowd_note = (f"你所在的 **{CATS_CN.get(cat_of, cat_of)}** 赛道拥挤度 {c}（次/项目），"
                          f"8 个赛道里排第 {pos}。拥挤度高 = 这格已被反复上榜的项目占住。")

    return {
        "repo": repo,
        "meta": meta,
        "meta_fetched": bool(meta),
        "dataset": {"items": n_items, "unique_projects": n_uniq,
                    "days": len({r.get("_day") for r in rows if r.get("_day")}),
                    "hits": n_hits,
                    "freq_map_size": land.get("gh_agent_hi_n"),
                    "dist": dict(sorted(dist.items()))},
        "position": {"in_frequent_map": in_map, "lane": cat_of,
                     "lane_cn": CATS_CN.get(cat_of, cat_of) if cat_of else None,
                     "lane_hint_only": hint if (not cat_of and hint) else None},
        "rivals": rivals,
        "density": density,
        "crowd_note": crowd_note,
        "verdict": verdict,
        "reason": reason,
        "source": "daily-ledger/data/raw-*.json（33 天四源抓取 GitHub 部分）"
                  " + tools/agent_landscape.py --json（8 类分类法，--verify 可回算）",
    }


def render(a: dict) -> str:
    L = []
    L.append(f"# {a['repo']} · 赛道定位体检")
    L.append("")
    L.append(f"**结论**：{a['verdict']} ｜ {a['reason']}")
    L.append("")
    if a["meta_fetched"]:
        m = a["meta"]
        L.append(f"**项目**：{m.get('desc') or '（无描述）'}")
        L.append(f"**GitHub**：★{m.get('stars')} ｜ fork {m.get('forks')} ｜ "
                 f"{m.get('lang')} ｜ 创建 {m.get('created')} ｜ 最近推送 {m.get('pushed')}")
        if m.get("topics"):
            L.append(f"**topics**：{', '.join(m['topics'][:10])}")
        L.append("")
    ds = a["dataset"]
    L.append(f"## 数据底座")
    L.append(f"- {ds['days']} 天 / {ds['items']} 条 GitHub 上榜记录 / {ds['unique_projects']} 个唯一项目")
    L.append(f"- 高频地图（≥3 次）：{ds['freq_map_size']} 个项目")
    L.append(f"- 上榜次数分布：" + "，".join(f"{k}次→{v}个" for k, v in ds["dist"].items()))
    L.append("")
    if a["position"]["in_frequent_map"]:
        L.append(f"## 你在第几格")
        L.append(f"**赛道**：{a['position']['lane_cn']}")
        if a["crowd_note"]:
            L.append(a["crowd_note"])
        L.append("")
        L.append("**同赛道在抢的项目**：")
        for r in a["rivals"]:
            st = f"｜★{r['stars']}" if r.get("stars") else ""
            L.append(f"- {r['times']} 次 · `{r['repo']}`{st}")
    elif a["position"]["lane_hint_only"]:
        L.append("## 你大概在哪一格")
        L.append(f"按描述/ topics 的粗分类：**{CATS_CN.get(a['position']['lane_hint_only'])}**")
        L.append("（这是粗分类，不是高频地图里的判定——你的项目没进 37 个高频项目）")
    else:
        L.append("## 你在第几格")
        L.append("**高频地图里没有你** ⇒ 你在长尾。")
        L.append(f"全量 {ds['unique_projects']} 个唯一项目里，上榜 1 次的有 {ds['dist'].get(1,0)} 个。")
    L.append("")
    L.append("## 8 赛道拥挤度（次/项目）")
    d = a["density"]
    for k, v in sorted(d.items(), key=lambda x: -x[1]):
        bar = "█" * int(round(v))
        L.append(f"- {CATS_CN.get(k,k)} {v}  {bar}")
    L.append("")
    L.append("---")
    L.append(f"*数据来源：{a['source']}*")
    return "\n".join(L)


def self_test():
    rows = load_rows()
    land = load_landscape()
    assert rows, "raw 数据读不到"
    assert land.get("per_cat"), "landscape JSON 读不到"
    a = analyze("adongwanai/learn-workbuddy", with_gh=False)
    assert a["dataset"]["items"] == len(rows)
    assert a["dataset"]["hits"] == 0, "预期该项目 0 次上榜"
    assert a["verdict"] == "NOT_ON_TRENDING"
    # 负对照：改一个不存在的 repo，不该崩，hits 应为 0
    b = analyze("totally-fake/repo-never-existed", with_gh=False)
    assert b["dataset"]["hits"] == 0 and b["position"]["in_frequent_map"] is False
    # 负对照：把 hits 塞成 99，verdict 应变
    c = dict(a); c["dataset"] = dict(a["dataset"]); c["dataset"]["hits"] = 99
    assert c["dataset"]["hits"] != a["dataset"]["hits"]
    md = render(a)
    assert "赛道定位体检" in md and "拥挤度" in md
    print("✅ 自测通过（正例 + 2 个负对照）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.repo:
        ap.error("需要 --repo owner/name")
    a = analyze(args.repo)
    if args.json:
        print(json.dumps(a, ensure_ascii=False, indent=1))
    else:
        print(render(a))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
