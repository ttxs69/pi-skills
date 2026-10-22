#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Agent 赛道地图 —— 37 个上榜≥3 次的 agent 项目的归类表（可复核、可质疑）

2026-10-22 建。起因：用户两次否决"读者自己 5 分钟就能发现的结论"。
第三次改成"37 个项目其实是 8 个赛道"—— 这张图只有 33 天对照才拼得出来。

为什么单独建文件而不是塞进 facts_gate：
  归类是人工判断，必须显式、可修改、可被读者质疑；
  facts_gate 只负责校验「文中的数 == 脚本重算的数」。
  所以：这张表是**事实源**，facts_gate 引用它来算赛道数、厂商占比、拥挤度。

用法：
  python3 tools/agent_landscape.py --verify     # 校验表与 33 天原始数据一致
  python3 tools/agent_landscape.py --show       # 打印地图
  python3 tools/agent_landscape.py --json       # 输出 JSON（给 facts_gate 用）
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "data"  # 2026-10-22 打包：相对路径

# 赛道定义。注意：① skills 的 9 个项目全是第三方/个人，厂商一个都没进 —— 这是文章的核心论点之一。
CATS = {
    "skills": {
        "label": "skills｜给 agent 装技能包",
        "slugs": [
            "mattpocock/skills", "addyosmani/agent-skills", "obra/superpowers",
            "cathrynlavery/diagram-design", "cloudflare/security-audit-skill",
            "DietrichGebert/ponytail", "K-Dense-AI/scientific-agent-skills",
            "JuliusBrussee/caveman", "earthtojake/text-to-cad",
        ],
    },
    "memory": {
        "label": "memory｜跨会话记忆",
        "slugs": ["vectorize-io/hindsight", "thedotmack/claude-mem",
                  "akitaonrails/ai-memory", "mksglu/context-mode"],
    },
    "runtime": {
        "label": "runtime｜安全执行环境",
        "slugs": ["coder/coder", "NVIDIA/OpenShell", "google/ax"],
    },
    "harness": {
        "label": "harness｜agent 的骨架/外壳",
        "slugs": ["affaan-m/ECC", "ruvnet/ruflo", "mattpocock/skills"],
    },
    "orchestration": {
        "label": "编排｜多 agent 调度",
        "slugs": ["morluto/rea", "stablyai/orca", "mvschwarz/openrig",
                  "paperclipai/paperclip", "anomalyco/opencode"],
    },
    "cli": {
        "label": "CLI 化｜把软件变成 agent 可调",
        "slugs": ["HKUDS/CLI-Anything", "BuilderIO/agent-native", "superdesigndev/treg",
                  "xerj-org/xerj", "Panniantong/Agent-Reach"],
    },
    "vertical": {
        "label": "垂直场景｜解决一个具体的活儿",
        "slugs": ["MadsLorentzen/ai-job-search", "dream-num/univer",
                  "anthropics/knowledge-work-plugins", "heygen-com/hyperframes",
                  "lyogavin/airllm", "alibaba/open-code-review"],
    },
    "vendor": {
        "label": "厂商官方",
        "slugs": ["anthropics/claude-code", "anthropics/claude-plugins-official",
                  "cursor/plugins", "google/ax", "NVIDIA/OpenShell",
                  "alibaba/open-code-review"],
    },
}

VENDOR_OWNERS = {"anthropics", "google", "NVIDIA", "cursor", "alibaba"}
AGENT_RE = re.compile(r"(agent|agentic|cli|llm|gpt|claude|mcp|copilot|cursor|codex|autonom)", re.I)
MIN_DAYS = 3


def load_gh():
    rows = []
    for f in sorted(LEDGER.glob("raw-*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for it in (d.get("gh") or []):
            it = dict(it)
            it["_day"] = d.get("date")
            rows.append(it)
    return rows


def agent_info(rows):
    info = {}
    for g in rows:
        s = g.get("slug")
        if not s or not AGENT_RE.search(s + " " + (g.get("desc") or "")):
            continue
        d = info.setdefault(s, {"days": 0, "stars": 0, "desc": "", "lang": ""})
        d["days"] += 1
        d["stars"] += g.get("stars_today") or 0
        if len(g.get("desc") or "") > len(d["desc"]):
            d["desc"] = g.get("desc") or ""
        d["lang"] = g.get("lang") or d["lang"]
    return {s: d for s, d in info.items() if d["days"] >= MIN_DAYS}


def stats():
    rows = load_gh()
    info = agent_info(rows)
    covered = set()
    for c in CATS.values():
        covered |= set(c["slugs"])
    vendor = [s for s in info if s.split("/")[0] in VENDOR_OWNERS]
    skills = [s for s in CATS["skills"]["slugs"] if s in info]
    density = {}
    for k, c in CATS.items():
        ss = [s for s in c["slugs"] if s in info]
        density[k] = round(sum(info[s]["days"] for s in ss) / max(1, len(ss)), 1)
    return {
        "gh_items": len(rows),
        # 2026-10-22 加：真实覆盖天数。原先输出标题里把「33 天」**硬编码**，
        # 但数据每天在长（今天采集后已是 34 天）⇒ 文章里的「33 天」是漂移的口径。
        # 天数必须动态算，否则正文与工具输出会对不上。
        "gh_days": len({r.get("_day") for r in rows if r.get("_day")}),
        "gh_agent_hi_n": len(info),
        "landscape_cats": len(CATS),
        "landscape_covered": len(covered & set(info)),
        "landscape_uncovered": sorted(set(info) - covered),
        "landscape_orphan": sorted(covered - set(info)),
        "vendor_n": len(vendor),
        "vendor_pct": round(len(vendor) / max(1, len(info)) * 100),
        "skills_n": len(skills),
        "skills_vendor_n": len([s for s in skills if s.split("/")[0] in VENDOR_OWNERS]),
        "density": density,
        "per_cat": {k: {s: info[s]["days"] for s in c["slugs"] if s in info}
                    for k, c in CATS.items()},
        "per_project_stars": {s: info[s]["stars"] for s in info},
    }


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--show"
    st = stats()
    if mode == "--json":
        print(json.dumps(st, ensure_ascii=False, indent=1))
        return 0
    if mode == "--verify":
        bad = []
        if st["landscape_covered"] != st["gh_agent_hi_n"]:
            bad.append(f"覆盖不全: {st['landscape_covered']}/{st['gh_agent_hi_n']} 漏 {st['landscape_uncovered']}")
        if st["landscape_orphan"]:
            bad.append(f"表里有原始数据没有的: {st['landscape_orphan']}")
        for k, c in CATS.items():
            miss = [s for s in c["slugs"] if s not in st["per_project_stars"]]
            if miss:
                bad.append(f"赛道 {k} 的 slug 不在原始数据里: {miss}")
        if bad:
            for b in bad:
                print("  ✗", b)
            print("❌ 赛道表与 33 天原始数据不一致")
            return 78
        print(f"✅ 赛道表一致：{st['gh_agent_hi_n']} 个项目 / {st['landscape_cats']} 个赛道全覆盖")
        print(f"   厂商官方 {st['vendor_n']}/{st['gh_agent_hi_n']} = {st['vendor_pct']}%"
              f" | skills 赛道厂商占 {st['skills_vendor_n']}/{st['skills_n']}")
        print("   拥挤度(次/项目):", json.dumps(st["density"], ensure_ascii=False))
        return 0
    # --show
    print(f"GitHub Trending agent 赛道地图（{st['gh_items']} 条 / {st.get('gh_days','?')} 天 / "
          f"上榜≥{MIN_DAYS}次的 {st['gh_agent_hi_n']} 个项目 / {st['landscape_cats']} 个赛道）\n")
    for k, c in CATS.items():
        ss = [s for s in c["slugs"] if s in st["per_cat"][k]]
        days = st["per_cat"][k]
        print(f"{c['label']}  ({len(ss)} 个项目, 拥挤度 {st['density'][k]})")
        for s in sorted(ss, key=lambda x: -days[x]):
            print(f"    {days[s]:>2}次  {s}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
