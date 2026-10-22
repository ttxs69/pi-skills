---
name: agent-ecosystem-intel
description: "Use when deciding which layer of the AI agent stack to build on, whether a project is in a crowded lane, or who else is building in the same space."
version: 1.0.0
license: MIT
---

# AI Agent Ecosystem Intel

**34 天真实数据 + 8 赛道分类法 —— 用来回答「我该做哪一层 / 我这格挤不挤 / 谁在同一条赛道上」。**

这不是通用 AI 能做的事。分类法按「**这个项目替换掉 agent 工作流的哪一步**」分，
不是按技术栈（不是「Python 项目」「RAG 框架」）。通用模型会按技术栈分，因为那是 README 里写的。

---

## When to use

- 要做 AI agent 工具，**不知道该做哪一层**（skills / memory / 编排 / CLI 化 / 垂直场景 / runtime / harness / 厂商官方）
- 已经做了，**想知道这一层挤不挤**、厂商有没有占位
- 想找**竞品**、同赛道还有谁在跑
- 要判断某个项目**值不值得跟**

**不适用**：写代码、查文档、调 API。

---

## 8 条赛道（按「替换 agent 工作流哪一步」分）

| 赛道 | 它替换掉哪一步 | 项目数 | 拥挤度（次/项目） |
|---|---|---|---|
| **skills** | 给 agent 装技能包 | 9 | 6.2 |
| **memory** | 跨会话记忆 | 4 | 6.8 |
| **runtime** | 安全执行环境 | 3 | 3.7 |
| **harness** | agent 的骨架/外壳 | 3 | **7.3**（最挤） |
| **编排** | 多 agent 调度 | 5 | 5.4 |
| **CLI 化** | 把软件变成 agent 可调 | 5 | 4.0 |
| **垂直场景** | 解决一个具体的活儿 | 6 | 4.5 |
| **厂商官方** | 官方自有栈 | 7 | 4.2 |

**拥挤度 = 该赛道所有项目上榜次数 ÷ 项目数。** 越高 = 这格已被反复上榜的项目占住。

**厂商官方只占 7/37 = 19%。而 skills 赛道 9 个项目，厂商占 0。**

---

## 怎么用（三条命令）

### 1. 我的项目在哪一格

```bash
python3 scripts/project_positioning.py --repo owner/repo
```

输出：上榜次数、在第几格、该格拥挤度、同赛道在抢的项目（含星数）。

**如果输出 `NOT_ON_TRENDING`**：不是项目不好，是英文 Trending feed 不覆盖所有项目
（中文/小众项目常整段缺席）。**不能用「有没有上 Trending」判断该不该继续。**

### 2. 整个赛道的实时分布

```bash
python3 scripts/agent_landscape.py            # 人读的表
python3 scripts/agent_landscape.py --json     # 机器读
python3 scripts/agent_landscape.py --verify   # 校验赛道表与原始数据一致
```

### 3. 校验数据可信

```bash
python3 scripts/agent_landscape.py --verify
```

输出 `✅ 赛道表一致：37 个项目 / 8 个赛道全覆盖` 才说明数据自洽。

---

## 数据底座（可回源）

- **34 天**四源抓取的 GitHub Trending 原始记录，**402 条，一条没删**（`data/raw-*.json`）
- **37 个**上榜 ≥3 次的高频项目，逐个人工归类到 8 条赛道
- 每条赛道拥挤度由上榜次数现算，不是估计值
- 厂商判定按 owner 是否为厂商组织（不是按名字像不像）

**原始数据随包附上 ⇒ 任何结论都能自己复算。**

---

## 例：一次真实输出

```
$ python3 scripts/project_positioning.py --repo morluto/rea
# morluto/rea · 赛道定位体检
**结论**：IN_FREQUENT_MAP ｜ 上榜 10 次，进入高频地图（≥3 次，共 37 个项目）。

## 你在第几格
**赛道**：编排（多 agent 调度）
同赛道在抢的项目：
- 10 次 · morluto/rea
- 5 次 · mvschwarz/openrig
- 5 次 · paperclipai/paperclip
```

---

## 谁在用这招的判断（为什么这些赛道值得看）

- **harness 最挤（7.3）** —— 说明「agent 的外壳」这个想法已被反复尝试，不是空白
- **runtime 最空（3.7）** —— 安全执行环境只有 3 个项目反复上榜
- **skills 赛道厂商占 0** —— 官方没下场，但拥挤度 6.2 说明民间已经很卷
- 「拥挤」不等于「有价值」—— 拥挤说明**需求被验证过**，但也说明**你要的差异化更难**

---

## 更新数据

包里的 `data/raw-*.json` 是快照。要更新：

1. 按同格式追加新的 `raw-YYYYMMDD.json`（顶层 `date` + `gh` 数组，每项含 `slug`/`desc`/`lang`/`stars_today`）
2. `python3 scripts/agent_landscape.py --verify` —— 若报「表里有原始数据没有的」，说明新出现了没归类的项目，需要人工判断赛道
3. 赛道表在 `scripts/agent_landscape.py` 的 `CATS` 常量里

**人工归类是这个 skill 的核心价值，不要自动化掉它。**
