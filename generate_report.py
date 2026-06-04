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
API_KEY        = os.environ.get("DEEPSEEK_API_KEY", "").strip()
MODEL_WRITER   = "deepseek-v4-pro"
MODEL_FAST     = "deepseek-v4-flash"
TODAY          = datetime.date.today().strftime("%Y年%m月%d日")
DATE_STR       = datetime.date.today().strftime("%Y-%m-%d")
TARGET_DEEP    = 10
TARGET_BRIEF   = 20
MAX_PER_SOURCE = 6
BATCH_DEEP     = 5
BATCH_SLEEP    = 12   # 批次间等待秒数（防并发限速）
API_CALL_SLEEP = 3    # 每次API调用后基础等待

if not API_KEY:
    print("❌ 未找到 DEEPSEEK_API_KEY 环境变量，请检查 GitHub Secrets")
    sys.exit(1)

# 打印Key末尾4位，便于确认是否读取正确
print(f"✅ API Key 已加载（末尾4位：...{API_KEY[-4:]}）")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")


# ── API 统一调用包装（含重试 + 清晰报错）─────────────
def _chat(model: str, messages: list, max_tokens: int = 4000,
          temperature: float = 0.7) -> str:
    """
    DeepSeek API 统一调用 — 含完整错误处理和自动重试
    401 → Key 带空格 / Key 失效 / DeepSeek 并发触发的临时封禁
    402 → 余额不足
    429 → 请求过快，指数退避重试
    5xx → 服务端错误，等待重试
    """
    from openai import AuthenticationError, RateLimitError, APIStatusError

    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            result = resp.choices[0].message.content
            # 每次成功调用后基础等待，防止连续请求触发限速
            time.sleep(API_CALL_SLEEP)
            return result

        except AuthenticationError as e:
            raw = str(e)
            msg = raw.lower()
            print(f"\n{'='*58}")
            print(f"❌  DeepSeek 401 认证失败（第{attempt}次）")
            print(f"    原始错误：{raw[:120]}")
            print()

            if attempt < max_retries:
                # 401 有时是瞬时并发触发，先等待重试
                wait = 20 * attempt
                print(f"  ⏳ 等待 {wait}s 后重试（{attempt}/{max_retries-1}）…")
                print(f"     注：DeepSeek 高并发时会临时返回 401，等待可恢复")
                print(f"{'='*58}\n")
                time.sleep(wait)
                continue

            # 最后一次仍失败，给出明确指引
            print("  ── 排查步骤 ──────────────────────────────────")
            print("  1. 余额检查（最常见原因）：")
            print("     → platform.deepseek.com → 余额")
            print("     → 如果 ¥0，充值后重新 Run workflow")
            print()
            print("  2. Key 是否带了空格（第二常见）：")
            print("     → 仓库 Settings → Secrets → DEEPSEEK_API_KEY")
            print("     → 删除重建，重新复制粘贴 Key，注意不要带空格")
            print(f"     → 当前 Key 末尾4位：...{API_KEY[-4:]}")
            print()
            print("  3. 如以上正常，等待 30 分钟后重试")
            print("     → DeepSeek 高并发期间会临时拒绝部分请求")
            print(f"{'='*58}\n")
            sys.exit(1)

        except RateLimitError as e:
            wait = 20 * attempt
            print(f"  ⚠️  429 限速（第{attempt}次），等待 {wait}s 后重试…")
            time.sleep(wait)
            if attempt == max_retries:
                print("❌  持续限速，跳过本次调用")
                return ""

        except APIStatusError as e:
            code = e.status_code
            if code == 402:
                print(f"\n{'='*58}")
                print("❌  余额不足（402）")
                print("    → platform.deepseek.com → 充值后重新触发 Actions")
                print(f"{'='*58}\n")
                sys.exit(1)
            elif code >= 500:
                wait = 15 * attempt
                print(f"  ⚠️  服务端错误 {code}（第{attempt}次），{wait}s 后重试…")
                time.sleep(wait)
                if attempt == max_retries:
                    print(f"❌  {code} 持续，跳过")
                    return ""
            else:
                print(f"❌  API 错误 {code}: {e}")
                sys.exit(1)

        except Exception as e:
            print(f"  ⚠️  未知错误（第{attempt}次）: {e}")
            if attempt == max_retries:
                return ""
            time.sleep(8)

    return ""

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
深度长文（10篇）领域分布——严格按此比例选题：
- 半导体/芯片/GPU/算力/HBM    (3篇) — 产业链变化、竞争格局、供应链动态
- 人工智能/大模型/推理          (2篇) — 技术突破、产品发布、能力边界
- 中国科技/国产替代/A股产业链   (2篇) — 国内企业动态、政策影响、投资机会
- 投资/融资/估值/商业模式       (1篇) — 重大融资、并购、市场格局
- 宏观/政策/地缘/出口管制       (1篇) — 影响产业的政策或地缘事件
- 新材料/先进制造/能源/机器人   (1篇) — 产业链前沿或材料创新
"""

BRIEF_DISTRIBUTION = """
快讯简报（20条）领域分布——严格按此比例选题：
- 半导体/芯片/算力/HBM    (5条) — 优先
- 人工智能/大模型          (4条)
- 中国科技/A股/产业链      (3条)
- 投资/融资/并购            (3条)
- 政策/宏观/地缘            (2条)
- 材料/制造/能源/机器人     (2条)
- 其他前沿科技              (1条)
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

请完成两项选题任务。以下领域配额是硬性要求，不是建议，必须严格执行。

## 任务A：深度长文（必须恰好{TARGET_DEEP}条，领域配额不可违反）

硬性配额：
1. 半导体/芯片/GPU/算力/HBM/封装 → 必须3篇（最高优先级）
2. 人工智能/大模型/推理 → 必须2篇
3. 中国科技/国产替代/A股产业链 → 必须2篇
4. 投资/融资/估值 → 必须1篇
5. 宏观/政策/地缘/出口管制 → 必须1篇
6. 新材料/先进制造/能源/机器人 → 必须1篇

重要：软件工程/SaaS/企业服务类不得占用上述名额。如当日半导体新闻不足3条，选相关产业链（HBM/封装/存储/EDA/设备）补充。

## 任务B：快讯简报（必须恰好{TARGET_BRIEF}条，不得与A重复）

硬性配额：
1. 半导体/芯片/算力/HBM → 必须5条
2. 人工智能/大模型 → 必须4条
3. 中国科技/A股/产业链 → 必须3条
4. 投资/融资/并购 → 必须3条
5. 政策/宏观/地缘 → 必须2条
6. 材料/制造/能源/机器人 → 必须2条
7. 其他前沿科技 → 必须1条

仅输出JSON，不要任何解释：
{{
  "deep": [
    {{"index": 编号, "title": "原标题", "source": "来源", "domain": "领域标签", "angle": "深度写作角度（一句话）"}}
  ],
  "brief": [
    {{"index": 编号, "title": "原标题", "source": "来源", "domain": "领域标签"}}
  ]
}}"""

    print(f"  🎯 选题中（Flash）…")
    content = _chat(MODEL_FAST, [{"role": "user", "content": prompt}],
                    max_tokens=3000, temperature=0.3)
    if not content:
        return pool[:TARGET_DEEP], pool[TARGET_DEEP:TARGET_DEEP+TARGET_BRIEF]
    m   = re.search(r'\{[\s\S]+\}', content)
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
SYSTEM_PROMPT_WRITER = """你是一位中国顶级财经记者，同时具备产业研究员和价值投资人的双重视角。你的文章风格参照《财经》杂志、《第一财经》、《哈佛商业评论》中文版的最高水准——沉稳、真实、有判断力、让人读完以后对产业有更深的理解。

━━ 核心写作原则：

① 【沉稳克制】不用感叹号，不堆砌形容词，不说"颠覆性""革命性"等空话。用事实和数字说话，让读者自己得出结论。

② 【产业链思维】每篇文章必须回答：这件事在整条产业链上处于哪个位置？上游/中游/下游谁受益、谁受损？三年后这个方向会走向哪里？

③ 【投资视角】投资人最关心的问题是：谁赚钱？谁会亏？这件事改变了哪家公司的竞争壁垒？估值逻辑是否需要重新定价？

④ 【给人思考空间】文章结尾不说"我们拭目以待"这类废话。给出一个具体的、有见地的判断，让读者产生"没想到还有这个角度"的感觉。

━━ 铁律（违反则重写）：

① 每篇约500字（允许±80字），重点领域（半导体/算力）可适当延伸到600字

② 【最核心铁律】每个专业名词第一次出现时，必须立即在括号内解释，格式：
   名词（通俗解释——为什么对普通投资者重要）
   示例：
   · HBM（高带宽内存——AI训练的"血管"，决定GPU的数据吞吐速度，SK海力士和三星凭此垄断AI供应链上游）
   · CoWoS（晶圆级封装技术——把芯片和内存"焊"在一起的工艺，台积电独家优势，产能瓶颈直接卡住了英伟达交货）
   · 倒装芯片（Flip Chip——先进封装的基础工艺，把芯片倒过来焊接以缩短信号路径，是先进封装的入门门槛）
   解释融入正文，自然流畅，绝不单独列术语表

③ 开头第一句必须是有信息量的结论或判断，禁止用"近日""随着""据悉""日前"开头

④ 结尾必须有【今日启示】：一个具体的、可操作的投资或认知建议，不超过两句话

⑤ 文章结构：核心判断(1段) → 产业背景与链条分析(2段) → 竞争格局与赢家/输家(1段) → 启示(1句)

⑥ 重点关注领域（半导体、算力、AI、材料、产业链）的文章，要重点分析中国视角：国产替代进度、A股相关标的逻辑、地缘政治影响"""


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
    return _chat(
        MODEL_WRITER,
        [{"role": "system", "content": SYSTEM_PROMPT_WRITER},
         {"role": "user",   "content": prompt}],
        max_tokens=8000, temperature=0.72,
    )


def write_briefs(briefs: list[dict]) -> str:
    """Flash模型：一次写完全部快讯（每条~80字）"""
    items = []
    for i, a in enumerate(briefs):
        items.append(
            f"[{i+1:02d}] 来源:【{a['source']}】领域:{a.get('domain','')} "
            f"标题:{a['title']} 摘要:{a['desc'][:120]}"
        )

    prompt = f"""今天是{TODAY}。下面有{len(briefs)}条新闻，请逐条改写为快讯简报，必须输出全部{len(briefs)}条，一条都不能少。

新闻列表：
{chr(10).join(items)}

---

输出格式要求（严格遵守）：
- 每条用"===第N条==="作为分隔符开头（N从1到{len(briefs)}）
- 格式如下：

===第1条===
领域：[领域标签]
标题：[简洁标题，≤15字]
正文：[60-90字，直击要点：发生了什么+为什么重要+数字支撑。专业名词首次出现必须括号解释：名词（解释——为什么重要）]
启示：[一句话，这件事对谁影响最大]

===第2条===
...以此类推直到第{len(briefs)}条

重要：必须输出全部{len(briefs)}条，每条都要有完整的领域/标题/正文/启示四个字段。"""

    print(f"  ⚡ 快讯 ({len(briefs)}条) → {MODEL_FAST}…")
    return _chat(
        MODEL_FAST,
        [{"role": "system", "content": (
              "你是一位顶级财经编辑，为高净值投资人写每日科技快讯。"
              "每条快讯精准有密度，专业名词首次出现必须括号解释：名词（解释——为什么重要）。"
              f"必须严格输出全部{len(briefs)}条，使用===第N条===分隔符格式。")},
         {"role": "user",   "content": prompt}],
        max_tokens=8000, temperature=0.6,
    )


def write_all_deep(deep: list[dict]) -> str:
    """深度长文：分2批写，每批5篇，批次间等待防限速"""
    batches = [deep[i:i+BATCH_DEEP] for i in range(0, len(deep), BATCH_DEEP)]
    parts   = []
    for idx, batch in enumerate(batches, 1):
        parts.append(write_deep_batch(batch, idx, len(batches)))
        if idx < len(batches):
            print(f"  ⏳ 批次间等待 {BATCH_SLEEP}s（防并发限速）…")
            time.sleep(BATCH_SLEEP)
    return "\n\n---\n\n".join(parts)

# ══════════════════════════════════════════════════════
# Step 4 · 生成导读（Flash，快速省钱）
# ══════════════════════════════════════════════════════
def make_header(deep_text: str, selected: list[dict]) -> str:
    """导读生成：用各篇标题+首句摘要构建上下文，避免截断问题"""
    domains = [a.get("domain","") for a in selected]
    domain_list = "、".join(dict.fromkeys(d for d in domains if d))

    # 从 deep_text 提取每篇标题+首句，给AI足够的上下文
    summaries = []
    articles = [a.strip() for a in deep_text.split('\n---\n') if a.strip()]
    for i, art in enumerate(articles[:10], 1):
        # 提取标题行
        title_m = re.search(r'##\s+深度[文章]*\d*[：:]\s*(.+)', art)
        title = title_m.group(1).strip() if title_m else f"文章{i}"
        # 提取领域
        domain_m = re.search(r'\*\*领域\*\*[：:](.+)', art)
        domain = domain_m.group(1).strip() if domain_m else ""
        # 提取正文第一段（去掉标题和来源行）
        body = re.sub(r'^##[^\n]+\n', '', art, count=1)
        body = re.sub(r'\*\*来源\*\*[^\n]+\n', '', body)
        body = body.strip()
        first_para = body[:120].replace('\n', ' ')
        summaries.append(f"{i}. 【{domain}】{title}——{first_para}…")

    summary_text = "\n".join(summaries)

    return _chat(
        MODEL_FAST,
        [{"role": "user", "content": f"""
今天是{TODAY}。以下是今日10篇深度文章的标题和摘要：

{summary_text}

今日覆盖领域：{domain_list}

---

你的任务：写一段每日导读。

第一步：逐字输出这句话，一个字都不能改：
早，今天是{TODAY}，王sir为您汇报今天的重要资讯。

第二步：紧接着写3条今日重要资讯（不换行空行，自然衔接）：
- 每条1-2句，说清楚：发生了什么 + 为什么对投资或产业重要
- 优先选半导体、算力、AI、产业链相关内容
- 最值得关注的1条用**加粗**标出
- 语气：中国顶级财经记者，克制精准，不用感叹号

第三步：最后一行固定格式（单独一行）：
今日关键词：XXX · XXX · XXX

总字数：150-180字（含第一句，不含关键词行）

禁止："早安""大家好""让我们""颠覆性""革命性""历史性"，禁止感叹号。
"""}],
        max_tokens=600, temperature=0.4,
    )

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