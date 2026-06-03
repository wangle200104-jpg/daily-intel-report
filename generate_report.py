"""
generate_report.py — 每日科技投资深度简报
100个新闻源 → 去重评分 → DeepSeek V4 Pro
  · 10篇深度长文（每篇~500字，三重身份写作）
  · 20条快讯简报（每条~80字，直击要点）
"""
import os, datetime, time, hashlib, re, sys
import xml.etree.ElementTree as ET

try:
    import requests
    from openai import OpenAI
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable,"-m","pip","install",
                           "requests","openai","--break-system-packages","-q"])
    import requests
    from openai import OpenAI

from sources import ALL_SOURCES, KEYWORDS

# ── 配置 ──────────────────────────────────────────────
API_KEY        = os.environ["DEEPSEEK_API_KEY"]
MODEL_WRITER   = "deepseek-v4-pro"    # 写作主力：最强推理+创作
MODEL_FAST     = "deepseek-v4-flash"  # 快速任务：导读、去重判断
TODAY          = datetime.date.today().strftime("%Y年%m月%d日")
DATE_STR       = datetime.date.today().strftime("%Y-%m-%d")
TARGET_DEEP     = 10      # 深度长文数量（~500字，Pro模型）
TARGET_BRIEF    = 20      # 快讯简报数量（~80字，Flash模型）
MAX_PER_SOURCE  = 6       # 每源最多取几条
BATCH_DEEP      = 5       # 深度文章每批写几篇（Pro限速）

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# ══════════════════════════════════════════════════════
# Step 1 · RSS 抓取
# ══════════════════════════════════════════════════════
def _first(entry, *tags):
    """安全取 XML 元素文本，兼容 RSS 2.0 + Atom"""
    for t in tags:
        el = entry.find(t)
        if el is not None and el.text:
            return el.text.strip()
    return ""

def fetch_rss(source: dict) -> list[dict]:
    articles = []
    headers  = {"User-Agent": "Mozilla/5.0 (compatible; IntelBriefBot/3.0)"}
    try:
        r = requests.get(source["url"], timeout=12, headers=headers)
        r.raise_for_status()
        root    = ET.fromstring(r.content)
        entries = root.findall(".//item") \
                  or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for e in entries[:25]:
            title = _first(e,
                "title", "{http://www.w3.org/2005/Atom}title")
            desc  = _first(e,
                "description", "summary",
                "{http://www.w3.org/2005/Atom}summary",
                "{http://www.w3.org/2005/Atom}content")
            link  = _first(e,
                "link", "{http://www.w3.org/2005/Atom}link")
            pub   = _first(e,
                "pubDate", "{http://www.w3.org/2005/Atom}published")
            if not title:
                continue
            combined = (title + " " + desc).lower()
            if not any(k.lower() in combined for k in KEYWORDS):
                continue
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:350]
            articles.append({
                "source":  source["name"],
                "tags":    source["tags"],
                "weight":  source["weight"],
                "title":   title,
                "desc":    desc_clean,
                "link":    link,
                "pub":     pub,
                "uid":     hashlib.md5(title.lower().encode()).hexdigest()[:10],
            })
            if len(articles) >= MAX_PER_SOURCE:
                break
    except Exception as ex:
        print(f"  ⚠️  {source['name']}: {str(ex)[:70]}")
    return articles

def collect_news() -> list[dict]:
    print(f"📡 抓取 {len(ALL_SOURCES)} 个新闻源…")
    pool, seen = [], set()
    for i, src in enumerate(ALL_SOURCES):
        arts = fetch_rss(src)
        new  = [a for a in arts if a["uid"] not in seen]
        for a in new:
            seen.add(a["uid"])
        pool.extend(new)
        if new:
            print(f"  [{i+1:3d}/{len(ALL_SOURCES)}] {src['name']}: +{len(new)} 条")
        time.sleep(0.18)
    pool.sort(key=lambda x: x["weight"], reverse=True)
    print(f"\n✅ 去重后 {len(pool)} 条有效资讯\n")
    return pool

# ══════════════════════════════════════════════════════
# Step 2 · 选题（Flash模型，快速省钱）
# ══════════════════════════════════════════════════════
DEEP_DISTRIBUTION = """
深度长文（10篇）领域分布：
- 人工智能/大模型前沿     (2篇) — 技术突破或产品发布
- 半导体/芯片/GPU/算力    (2篇) — 产业链或竞争格局
- 投资/融资/商业估值      (2篇) — 融资事件或市场动向
- AI智能体/自动化         (1篇) — 应用或工具
- 宏观/政策/地缘          (1篇) — 影响产业的政策
- 中国科技市场            (1篇) — 国内动态
- 开源/开发者生态         (1篇) — 开源模型或工具
"""

BRIEF_DISTRIBUTION = """
快讯简报（20条）领域分布：
- 人工智能/大模型    (5条)
- 半导体/芯片        (4条)
- 投资/融资          (4条)
- 智能体/应用        (3条)
- 政策/宏观          (2条)
- 其他前沿           (2条)
"""

def select_topics(pool: list[dict]) -> tuple[list[dict], list[dict]]:
    """Flash模型一次选题，返回 (deep_10, brief_20) 两个列表"""
    items = []
    for i, a in enumerate(pool[:150]):
        items.append(
            f"[{i+1:03d}] 【{a['source']}】权重{a['weight']} | "
            f"{a['title']} | {a['desc'][:100]}"
        )
    news_text = "\n".join(items)

    prompt = f"""今天是{TODAY}。

以下是从100个新闻源抓取的资讯（共{len(items)}条）：
{news_text}

---

请完成两项选题任务：

## 任务A：深度长文选题（选{TARGET_DEEP}条）
{DEEP_DISTRIBUTION}
选题标准：影响力大、角度独特、值得500字深挖、有投资/商业价值

## 任务B：快讯简报选题（选{TARGET_BRIEF}条，不得与A重复）
{BRIEF_DISTRIBUTION}
选题标准：今日发生、信息密度高、一句话能说清楚

仅输出JSON，不要任何解释：
{{
  "deep": [
    {{"index": 编号, "title": "原标题", "source": "来源", "domain": "领域标签", "angle": "深度写作角度（一句话）"}}
  ],
  "brief": [
    {{"index": 编号, "title": "原标题", "source": "来源", "domain": "领域标签"}}
  ]
}}"""

    resp = client.chat.completions.create(
        model=MODEL_FAST, max_tokens=3000, temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = resp.choices[0].message.content
    m   = re.search(r'\{[\s\S]+\}', raw)
    if not m:
        print("⚠️  选题JSON解析失败，使用权重降级方案")
        return pool[:TARGET_DEEP], pool[TARGET_DEEP:TARGET_DEEP+TARGET_BRIEF]

    import json
    try:
        data     = json.loads(m.group())
        pool_map = {str(i+1): pool[i] for i in range(min(len(pool), 150))}

        def resolve(lst):
            result = []
            for s in lst:
                idx = str(s.get("index", ""))
                if idx in pool_map:
                    art = pool_map[idx].copy()
                    art["angle"]  = s.get("angle", "")
                    art["domain"] = s.get("domain", "")
                    result.append(art)
            return result

        deep  = resolve(data.get("deep",  []))[:TARGET_DEEP]
        brief = resolve(data.get("brief", []))[:TARGET_BRIEF]
        # 去掉 brief 中与 deep 重叠的条目
        deep_uids = {a["uid"] for a in deep}
        brief     = [a for a in brief if a["uid"] not in deep_uids][:TARGET_BRIEF]

        print(f"✅ 选题完成 → 深度 {len(deep)} 篇 · 快讯 {len(brief)} 条")
        return deep, brief
    except Exception as ex:
        print(f"⚠️  选题解析错误: {ex}")
        return pool[:TARGET_DEEP], pool[TARGET_DEEP:TARGET_DEEP+TARGET_BRIEF]

# ══════════════════════════════════════════════════════
# Step 3 · 写作（Pro模型，分批调用）
# ══════════════════════════════════════════════════════
SYSTEM_PROMPT_WRITER = """你是一位集三重身份于一身的顶级写作者：

━━ 身份一：行业大佬（产业洞察）
你在AI/半导体/投资产业摸爬滚打15年，见过泡沫和真金，知道这件事在实际业务中意味着什么。你会用"我们当年做某某项目的时候"这类亲历感说话，不是书斋里的旁观者。

━━ 身份二：资深投资人（商业价值）  
你管理过多支科技基金，看过几百个项目。你的本能是：这件事背后谁赚钱？谁会亏？哪家公司的估值逻辑会被这个新闻改写？你用数字说话，但不是罗列数字——而是让数字讲故事。

━━ 身份三：专业财经记者（通俗易懂）
你在彭博/FT写过报道，懂得把复杂的技术/金融事件翻译给聪明但不是行内人的读者看。你知道"一个比喻胜过一段定义"。你的文章让人想转发。

━━ 铁律（违反则重写）：
① 每篇约500字（允许±80字）
② 每个专业名词**第一次出现时**，必须立即用括号加解释：
   格式："专业名词（通俗解释——为什么重要）"
   示例：
   - LLM（大语言模型——ChatGPT、DeepSeek这类AI的底层技术，能理解和生成人类语言，是当前AI产业最核心的资产）
   - GPU（图形处理器——原本给游戏渲染画面，因为擅长大规模并行计算，成了训练AI的"发动机"，英伟达靠它市值破3万亿）
   - 估值（融资时投资人给公司定的"市场价格"——不等于实际盈利，但决定了创始人拿多少股权、投资人进场成本多少）
   - ARR（年度经常性收入——SaaS公司最核心的健康指标，代表每年稳定进账的金额，增长快慢直接影响估值倍数）
③ 开头一句话必须让人想读下去（不许用"近日"、"随着"、"据悉"开头）
④ 结尾必须有一句明确的【今日启示】（投资/行动/认知建议）
⑤ 语气：自信、有判断力、口语化但不失专业。不装腔，不废话
⑥ 文章结构：核心发现(1段) → 背景解读(2段) → 商业/投资视角(1段) → 启示(1句)"""


def write_deep_batch(articles: list[dict], batch_num: int, total_batches: int) -> str:
    """Pro模型：写一批深度长文（每篇~500字）"""
    items = []
    for i, a in enumerate(articles):
        angle_hint = f"\n   写作角度：{a['angle']}" if a.get("angle") else ""
        items.append(
            f"### 新闻{i+1}（{a.get('domain','未分类')}）\n"
            f"   来源：{a['source']}\n"
            f"   标题：{a['title']}\n"
            f"   摘要：{a['desc'][:200]}{angle_hint}"
        )

    prompt = f"""今天是{TODAY}。第{batch_num}/{total_batches}批，{len(articles)}篇深度长文。

{chr(10).join(items)}

---

每篇输出格式（篇间用"---"分隔）：

## 深度文章[序号]：[标题，≤20字]

**来源**：[媒体] | **领域**：[标签]

[正文~500字，遵守所有铁律]

**今日启示**：[一句话，具体可操作]

---

提醒：每篇独立，专业名词每篇首次出现都要括号解释。"""

    print(f"  📝 深度第{batch_num}批 ({len(articles)}篇) → {MODEL_WRITER}…")
    resp = client.chat.completions.create(
        model=MODEL_WRITER,
        max_tokens=8000,
        temperature=0.72,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_WRITER},
            {"role": "user",   "content": prompt},
        ]
    )
    return resp.choices[0].message.content


def write_briefs(briefs: list[dict]) -> str:
    """Flash模型：一次写完全部快讯（每条~80字）"""
    items = []
    for i, a in enumerate(briefs):
        items.append(
            f"[{i+1:02d}] 【{a['source']}】{a.get('domain','')} | "
            f"{a['title']} | {a['desc'][:120]}"
        )

    prompt = f"""今天是{TODAY}。请将以下{len(briefs)}条新闻逐条改写为快讯简报。

{chr(10).join(items)}

---

每条输出格式（条间用换行分隔，不要额外分隔符）：

**[序号] [领域标签] [标题，≤15字]**
[正文：60-90字。直击要点：发生了什么 + 为什么重要 + 一句数字或事实支撑。语气简洁有力，专业名词首次出现必须括号说明。]
📌 [一句话意义：这件事对谁影响最大？]

---

输出全部{len(briefs)}条，顺序不变。"""

    print(f"  ⚡ 快讯 ({len(briefs)}条) → {MODEL_FAST}…")
    resp = client.chat.completions.create(
        model=MODEL_FAST,
        max_tokens=6000,
        temperature=0.6,
        messages=[
            {"role": "system", "content": (
                "你是一位顶级财经编辑，专门为高净值投资人写每日科技快讯。"
                "每条快讯要精准、有密度、让人一眼抓住核心价值。"
                "专业名词首次出现必须括号解释。语气直接，不废话。"
            )},
            {"role": "user", "content": prompt},
        ]
    )
    return resp.choices[0].message.content


def write_all_deep(deep: list[dict]) -> str:
    """深度长文：分2批写，每批5篇"""
    batches = [deep[i:i+BATCH_DEEP] for i in range(0, len(deep), BATCH_DEEP)]
    parts   = []
    for idx, batch in enumerate(batches, 1):
        parts.append(write_deep_batch(batch, idx, len(batches)))
        if idx < len(batches):
            time.sleep(4)
    return "\n\n---\n\n".join(parts)

# ══════════════════════════════════════════════════════
# Step 4 · 生成导读（Flash，快速省钱）
# ══════════════════════════════════════════════════════
def make_header(articles_text: str, selected: list[dict]) -> str:
    domains = [a.get("domain","") for a in selected]
    domain_list = "、".join(dict.fromkeys(d for d in domains if d))

    resp = client.chat.completions.create(
        model=MODEL_FAST, max_tokens=600, temperature=0.55,
        messages=[{"role":"user","content":f"""
今天是{TODAY}。以下是今日20篇深度文章的内容（节选前2500字）：

{articles_text[:2500]}

---
今日覆盖领域：{domain_list}

请写一段**每日导读**（200字以内），要求：
- 语气像一位睿智的老朋友发给你的早间消息，不是官方通稿
- 用3-4个要点勾出今天最值得知道的事
- 点出今天最值得特别关注的1件事（加粗）
- 最后一行：「今日关键词：XXX · XXX · XXX」（3-5个）
"""}]
    )
    return resp.choices[0].message.content

# ══════════════════════════════════════════════════════
# Step 5 · 保存
# ══════════════════════════════════════════════════════
def save(header: str, body: str, pool_size: int) -> str:
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{DATE_STR}.md"
    content = f"""# 🧠 每日科技投资深度简报 · {TODAY}

> 数据来源：{len(ALL_SOURCES)} 个精选新闻源 · 今日抓取 {pool_size} 条相关资讯  
> 写作模型：**DeepSeek V4 Pro**（选题+导读：V4 Flash）  
> 涵盖：人工智能 · 大模型 · 半导体 · 算力 · 投资 · 智能体 · 政策

---

## 📋 今日导读

{header}

---

{body}

---

*本简报由 GitHub Actions + DeepSeek API 自动生成 · {TODAY}*  
*专业名词解释仅供参考，不构成投资建议*
"""
    with open(path,"w",encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告保存：{path}")
    return path

def update_readme(header: str, body_preview: str) -> None:
    readme = f"""# 🧠 每日科技投资深度简报

> **自动生成** · DeepSeek V4 Pro · 每天北京时间 08:00 更新  
> 100个精选新闻源 · 每日20篇深度文章 · 三重专家身份写作

## 📋 最新一期：{TODAY}

{header}

---

{body_preview[:5000]}

[→ 查看完整报告](reports/{DATE_STR}.md) · [→ 历史报告存档](reports/)

---

## 新闻源体系（100个）

| 层级 | 类别 | 代表来源 | 数量 |
|------|------|----------|------|
| Tier 1 | 顶级财经媒体 | Bloomberg · Reuters · WSJ · FT · 经济学人 | 14 |
| Tier 2 | AI 专属 | OpenAI/Anthropic/DeepMind官博 · arXiv · MIT TR · a16z | 28 |
| Tier 3 | 半导体/算力 | SemiAnalysis · IEEE Spectrum · EE Times | 12 |
| Tier 4 | 投资/创业 | TechCrunch · Crunchbase · CB Insights · Sequoia | 14 |
| Tier 5 | 中文媒体 | 机器之心 · 量子位 · 36氪 · 虎嗅 · 华尔街见闻 | 14 |
| Tier 6 | 前沿专题 | Google News专题聚合 · LessWrong · Papers With Code | 18 |

*由 GitHub Actions + [DeepSeek API](https://platform.deepseek.com) 自动生成*
"""
    with open("README.md","w",encoding="utf-8") as f:
        f.write(readme)
    print("✅ README 更新完成")

# ══════════════════════════════════════════════════════
# Step 5 · 保存（区分深度+快讯两块）
# ══════════════════════════════════════════════════════
def save(header: str, deep_text: str, brief_text: str, pool_size: int) -> str:
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{DATE_STR}.md"
    content = f"""# 🧠 每日科技投资深度简报 · {TODAY}

> 数据来源：{len(ALL_SOURCES)} 个精选新闻源 · 今日抓取 {pool_size} 条相关资讯
> 写作模型：**DeepSeek V4 Pro**（选题+导读：V4 Flash）
> 格式：10篇深度长文（~500字）· 20条快讯简报（~80字）

---

## 📋 今日导读

{header}

---

## 📰 深度长文（10篇）

{deep_text}

---

## ⚡ 快讯简报（20条）

{brief_text}

---

*本简报由 GitHub Actions + DeepSeek API 自动生成 · {TODAY}*
*专业名词解释仅供参考，不构成投资建议*
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告保存：{path}")
    return path


def update_readme(header: str, deep_preview: str, brief_preview: str) -> None:
    readme = f"""# 🧠 每日科技投资深度简报

> **自动生成** · DeepSeek V4 Pro · 每天北京时间 08:00 更新
> 100个精选新闻源 · 10篇深度长文 + 20条快讯简报 · 三重专家身份写作

## 📋 最新一期：{TODAY}

{header}

---

### 深度长文（节选）
{deep_preview[:2500]}

### 快讯简报（节选）
{brief_preview[:1500]}

[→ 查看完整报告](reports/{DATE_STR}.md) · [→ 历史报告存档](reports/)

---

## 新闻源体系（100个）

| 层级 | 类别 | 代表来源 | 数量 |
|------|------|----------|------|
| Tier 1 | 顶级财经媒体 | Bloomberg · Reuters · WSJ · FT · 经济学人 | 14 |
| Tier 2 | AI 专属 | OpenAI/Anthropic/DeepMind官博 · arXiv · MIT TR · a16z | 28 |
| Tier 3 | 半导体/算力 | SemiAnalysis · IEEE Spectrum · EE Times | 12 |
| Tier 4 | 投资/创业 | TechCrunch · Crunchbase · CB Insights · Sequoia | 14 |
| Tier 5 | 中文媒体 | 机器之心 · 量子位 · 36氪 · 虎嗅 · 华尔街见闻 | 14 |
| Tier 6 | 前沿专题 | Google News专题聚合 · LessWrong · Papers With Code | 18 |

*由 GitHub Actions + [DeepSeek API](https://platform.deepseek.com) 自动生成*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("✅ README 更新完成")


# ══════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{'═'*58}")
    print(f"  🧠 每日科技投资深度简报  ·  {TODAY}")
    print(f"  深度：{TARGET_DEEP}篇 × {MODEL_WRITER}")
    print(f"  快讯：{TARGET_BRIEF}条 × {MODEL_FAST}")
    print(f"{'═'*58}\n")

    # 1. 抓取
    pool = collect_news()
    if not pool:
        print("❌ 未抓取到任何资讯，退出"); sys.exit(1)

    # 2. 选题（一次分两档）
    deep_list, brief_list = select_topics(pool)
    print(f"\n📌 深度 {len(deep_list)} 篇 · 快讯 {len(brief_list)} 条，开始写作…\n")

    # 3. 写作
    deep_text  = write_all_deep(deep_list)
    brief_text = write_briefs(brief_list)

    # 4. 导读
    header = make_header(deep_text, deep_list + brief_list)

    # 5. 保存
    save(header, deep_text, brief_text, len(pool))
    update_readme(header, deep_text, brief_text)

    # 6. 推送（微信 + QQ + Server酱）
    from push import push_all
    push_all(header, deep_text, brief_text, DATE_STR)

    print("\n" + "─"*58)
    print("📋 今日导读：")
    print("─"*58)
    print(header)
    print("─"*58)
    print(f"\n🎉 完成！{TARGET_DEEP}篇深度 + {TARGET_BRIEF}条快讯 · 已推送")
