# AI Agent Ecosystem Intel

**回答 agent 生态里最贵的三个问题：我该做哪一层、这格挤不挤、谁在同赛道。**

基于 **34 天真实抓取数据**（402 条 GitHub Trending 记录，一条没删）+ **8 赛道分类法**。

---

## What this skill does

给 agent 一张**能自己算出来的生态地图**：

1. **8 条赛道**，按「这个项目替换掉 agent 工作流的哪一步」分类 —— 不是按技术栈
2. **每条赛道的拥挤度**（次/项目），现算，不是估计
3. **37 个高频项目**逐个人工归类 + 同赛道竞品清单
4. **随包附 34 天原始数据** ⇒ 每个结论都能自己复算

## When it activates

- 「我要做一个 AI agent 工具，该做哪一层？」
- 「skills / memory / 编排 / CLI 化 / runtime / harness，我选哪个？」
- 「这个方向是不是已经挤满了？」
- 「同赛道还有谁在做？」

**不激活于**：写代码、查文档、调 API、通用问答。

---

## Why this isn't something generic AI does

分类法的主观判断是**人工的**：

> 按技术栈分（"这是 Python 项目"、"这是 RAG 框架"）是通用模型会做的事，因为那正是 README 里写的。
> 按「它替换掉 agent 工作流的哪一步」分，是另一回事 —— 一个 skills 项目和 CLI 化项目技术栈可能一样，
> 但它们在 agent 系统里占的位置完全不同。

**拥挤度同理**：不是按 star 排（star 衡量的是采纳，不是 AI readiness），
是按「多少个项目在这条赛道上反复上了 Trending」。

---

## Example usage

```bash
$ python3 scripts/project_positioning.py --repo morluto/rea
```

```
**结论**：IN_FREQUENT_MAP ｜ 上榜 10 次，进入高频地图（≥3 次，共 37 个项目）。

## 你在第几格
**赛道**：编排（多 agent 调度）
你所在的编排赛道拥挤度 5.4，8 个赛道里排第 4。
拥挤度高 = 这格已被反复上榜的项目占住。

**同赛道在抢的项目**：
- 10 次 · morluto/rea｜★255022
- 5 次 · mvschwarz/openrig｜★2851
- 5 次 · paperclipai/paperclip｜★12773
```

```bash
$ python3 scripts/agent_landscape.py --verify
✅ 赛道表一致：37 个项目 / 8 个赛道全覆盖
   厂商官方 7/37 = 19% | skills 赛道厂商占 0/9
   拥挤度(次/项目): {"skills": 6.2, "memory": 6.8, "runtime": 3.7, "harness": 7.3, ...}
```

更多真实输出在 `examples/`。

---

## 目录结构

```
SKILL.md
scripts/
  project_positioning.py   # 单项目定位（可独立运行）
  agent_landscape.py       # 全赛道分布 + --verify 自检
data/
  raw-2026*.json           # 34 天原始抓取记录（402 条）
  landscape.json           # 机器读的赛道分布
examples/
  example-positioning.md
  example-landscape.txt
```

## 验证数据可信

```bash
python3 scripts/agent_landscape.py --verify
```

必须输出 `✅ 赛道表一致` 才说明赛道表与随包原始数据自洽。

## 更新数据

1. 追加 `data/raw-YYYYMMDD.json`（格式：`date` + `gh` 数组，项含 `slug`/`desc`/`lang`/`stars_today`）
2. 跑 `--verify`。若报「表里有原始数据没有的」，说明出现了没归类的新项目 —— **需要人工判断赛道**
3. 赛道表在 `scripts/agent_landscape.py` 的 `CATS` 常量

**人工归类是核心价值，不要自动化掉。**

---

## 数据说明与边界

- 数据源：GitHub Trending（daily/devops/AI 榜），2026-09-18 ~ 10-22，共 34 天
- 上榜 ≥3 次的判为「高频项目」（共 37 个）
- 厂商判定按 owner 是否为厂商组织
- 拥挤度 = 赛道内项目上榜次数合计 ÷ 项目数
- **本包不含** X/Twitter 数据（2026-02 起 X API 改纯按量计费）
- 结论基于英文 Trending feed，**中文/小众项目可能整段缺席**
  ⇒ `NOT_ON_TRENDING` 不等于项目不好
