"""
generate_report.py — 每日科技投资深度简报
100个新闻源 → 分层采样 → DeepSeek V4 Pro
  · 10篇深度长文（每篇~500字）
  · 20条快讯简报（每条~80字）
  · 每天09:00 + 16:00 各推一次，内容不同
  · 3天内不重复同一篇文章
"""
import os, datetime, time, hashlib, re, sys, json
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
MODEL_FAST     = "deepseek-v4-pro"   # 全部用Pro

NOW_HOUR       = datetime.datetime.utcnow().hour + 8  # 北京时间
NOW_HOUR       = NOW_HOUR % 24
# 时段判断：UTC 01:xx = 北京 09:xx（早班），UTC 08:xx = 北京 16:xx（午班）
SESSION        = "午班" if NOW_HOUR >= 14 else "早班"

TODAY          = datetime.date.today().strftime("%Y年%m月%d日")
DATE_STR       = datetime.date.today().strftime("%Y-%m-%d")
TARGET_DEEP    = 10
TARGET_BRIEF   = 10   # 粉丝反馈：宁缺毋滥，从20条减为10条精华
MAX_PER_SOURCE = 6
BATCH_DEEP     = 5
BATCH_SLEEP    = 12
API_CALL_SLEEP = 3
SOURCES_PER_SESSION = 30  # 每次推送随机选30个源，早晚班各不同

# ── 历史去重配置 ──────────────────────────────────────
HISTORY_FILE   = "reports/published_uids.json"   # 已发布uid记录
HISTORY_DAYS   = 3    # 保留最近N天的记录
NEWS_MAX_DAYS  = 3    # 只抓取最近N天内的新闻

if not API_KEY:
    print("❌ 未找到 DEEPSEEK_API_KEY 环境变量，请检查 GitHub Secrets")
    sys.exit(1)

print(f"✅ API Key 已加载（末尾4位：...{API_KEY[-4:]}）")
print(f"📅 当前时段：{SESSION}（北京时间约 {NOW_HOUR:02d}:00）")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")


# ══════════════════════════════════════════════════════
# 随机选源：早班/午班各取不同的30个源
# 策略：按 Tier 分层加权随机，保证每 Tier 都有覆盖
# ══════════════════════════════════════════════════════

def pick_session_sources(session: str, n: int = SOURCES_PER_SESSION) -> list[dict]:
    """
    从 ALL_SOURCES（104个）按分层加权随机选 n 个源。
    早班/午班使用不同的随机种子，确保每次选出不同的源组合。
    同一天同一时段种子固定，重跑结果一致。
    """
    import random
    import hashlib

    # 种子 = 日期 + 时段，保证同天同时段结果一致，早晚班不同
    seed_str = f"{DATE_STR}-{session}"
    seed_int = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed_int)

    # 按权重分层，高权重源必须保留，低权重源随机抽样
    weight10 = [s for s in ALL_SOURCES if s["weight"] == 10]   # 17个 → 全要
    weight9  = [s for s in ALL_SOURCES if s["weight"] == 9]    # 29个 → 抽8个
    weight8  = [s for s in ALL_SOURCES if s["weight"] == 8]    # 35个 → 抽7个
    weight7  = [s for s in ALL_SOURCES if s["weight"] <= 7]    # 23个 → 抽5个

    # 从低权重层随机抽取
    # 总计：17 + 8 + 7 + 5 = 37，再精简到30
    picked = (
        weight10 +                             # 全部17个高质量源
        rng.sample(weight9, min(8, len(weight9))) +
        rng.sample(weight8, min(7, len(weight8))) +
        rng.sample(weight7, min(5, len(weight7)))
    )

    # 如果超过n个，再随机裁到n个（但保留全部weight10）
    if len(picked) > n:
        # 必须保留weight10，从其他里随机裁
        must_keep = weight10[:]
        optional  = [s for s in picked if s not in must_keep]
        need_more = max(0, n - len(must_keep))
        picked    = must_keep + rng.sample(optional, min(need_more, len(optional)))

    rng.shuffle(picked)  # 打乱顺序，避免每次同样的抓取顺序

    source_names = [s["name"] for s in picked]
    print(f"🎲 {session}随机选源：{len(picked)}/{len(ALL_SOURCES)} 个")
    print(f"   权重10全选({len(weight10)}) + 其他随机抽取")
    print(f"   首5个：{', '.join(source_names[:5])}…")
    return picked


# 选出本次时段的源
SESSION_SOURCES = pick_session_sources(SESSION, SOURCES_PER_SESSION)


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
# 历史去重模块 — 3天内不重复，早班/午班内容不同
# ══════════════════════════════════════════════════════

def load_published_history() -> dict:
    """
    读取已发布文章的uid记录。
    结构：{
      "2026-06-04_早班": ["uid1", "uid2", ...],
      "2026-06-04_午班": ["uid1", ...],
      ...
    }
    只保留最近 HISTORY_DAYS 天的记录。
    """
    os.makedirs("reports", exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            data = json.load(f)
        # 清理超过HISTORY_DAYS天的旧记录
        cutoff = datetime.date.today() - datetime.timedelta(days=HISTORY_DAYS)
        cleaned = {}
        for key, uids in data.items():
            # key格式: "2026-06-04_早班" 或 "2026-06-04_午班"
            date_part = key.split("_")[0]
            try:
                record_date = datetime.date.fromisoformat(date_part)
                if record_date >= cutoff:
                    cleaned[key] = uids
            except ValueError:
                pass
        return cleaned
    except Exception as e:
        print(f"  ⚠️  读取历史记录失败: {e}")
        return {}


def get_published_uids(history: dict) -> set:
    """获取过去HISTORY_DAYS天内所有已发布的uid集合"""
    all_uids = set()
    for uids in history.values():
        all_uids.update(uids)
    print(f"📋 历史记录：{len(history)} 个时段，共 {len(all_uids)} 个已发布uid")
    # 打印最近记录
    sorted_keys = sorted(history.keys(), reverse=True)[:5]
    for k in sorted_keys:
        print(f"   {k}: {len(history[k])} 篇")
    return all_uids


def save_published_uids(history: dict, new_uids: list) -> None:
    """将本次发布的uid追加到历史记录"""
    session_key = f"{DATE_STR}_{SESSION}"
    history[session_key] = new_uids
    os.makedirs("reports", exist_ok=True)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"✅ 历史记录已更新：{session_key} → {len(new_uids)} 篇")
    except Exception as e:
        print(f"  ⚠️  写入历史记录失败: {e}")


def is_recent_news(pub_date_str: str, max_days: int = 3) -> bool:
    """判断新闻是否在最近max_days天内"""
    if not pub_date_str:
        return True  # 没有日期的新闻默认保留
    # 尝试解析常见日期格式
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",   # RSS标准
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",          # ISO8601
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ]
    today = datetime.date.today()
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(pub_date_str.strip(), fmt)
            article_date = dt.date() if hasattr(dt, 'date') else dt
            if hasattr(article_date, 'date'):
                article_date = article_date.date()
            delta = (today - article_date).days
            return delta <= max_days
        except (ValueError, TypeError):
            continue
    return True  # 解析失败默认保留


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
                "pubDate", "updated",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated")
            if not title:
                continue
            # ── 时效过滤：只保留最近NEWS_MAX_DAYS天内的新闻 ──
            if pub and not is_recent_news(pub, NEWS_MAX_DAYS):
                continue
            combined = (title + " " + desc).lower()
            if not any(k.lower() in combined for k in KEYWORDS):
                continue
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:350]
            uid = hashlib.md5(title.lower().strip().encode()).hexdigest()[:12]
            articles.append({
                "source":  source["name"],
                "tags":    source["tags"],
                "weight":  source["weight"],
                "title":   title,
                "desc":    desc_clean,
                "link":    link,
                "pub":     pub,
                "uid":     uid,
            })
            if len(articles) >= MAX_PER_SOURCE:
                break
    except Exception as ex:
        print(f"  ⚠️  {source['name']}: {str(ex)[:70]}")
    return articles

def collect_news(published_uids: set = None) -> list[dict]:
    """
    用本时段随机选出的30个源抓取新闻，早晚班各不同。
    published_uids: 过去3天已发布的uid集合，排除重复文章。
    """
    if published_uids is None:
        published_uids = set()

    sources = SESSION_SOURCES
    print(f"📡 {SESSION} 抓取 {len(sources)} 个源（来自{len(ALL_SOURCES)}个总源库，最近{NEWS_MAX_DAYS}天内容）…")
    pool, seen = [], set()
    for i, src in enumerate(sources):
        arts = fetch_rss(src)
        new  = [a for a in arts if a["uid"] not in seen]
        for a in new:
            seen.add(a["uid"])
        pool.extend(new)
        if new:
            print(f"  [{i+1:2d}/{len(sources)}] {src['name']}: +{len(new)} 条")
        time.sleep(0.18)

    print(f"\n✅ 去重后 {len(pool)} 条有效资讯")

    # ── 排除已发布文章 ──
    before_filter = len(pool)
    pool = [a for a in pool if a["uid"] not in published_uids]
    excluded = before_filter - len(pool)
    if excluded > 0:
        print(f"  🚫 排除已发布文章：{excluded} 条 → 剩余 {len(pool)} 条新鲜内容")

    if len(pool) < 30:
        print(f"  ⚠️  新鲜内容不足30条（{len(pool)}条），放宽历史限制")
        # 放宽：只排除今天已发布的（不排除昨天的）
        today_prefix = DATE_STR
        # 找今天已发布的uid
        today_uids = set()
        history = load_published_history()
        for key, uids in history.items():
            if key.startswith(today_prefix):
                today_uids.update(uids)
        # 从原始pool重新过滤（只排除今天的）
        pool = [a for a in [x for x in pool] if a["uid"] not in today_uids]
        print(f"  📖 放宽后剩余：{len(pool)} 条")

    # ── 分层采样 ──
    SEMI_KEYS = ['semiconductor','chip','gpu','hbm','tsmc','nvidia','amd','intel',
                 'arm','asml','qualcomm','算力','芯片','半导体','封装','存储','制程',
                 'fab','wafer','foundry','eda','litho']
    AI_KEYS   = ['ai','llm','gpt','claude','gemini','deepseek','openai','anthropic',
                 '大模型','人工智能','机器学习','neural','transformer','inference']
    CN_KEYS   = ['china','chinese','华为','中国','国产','A股','腾讯','阿里','百度',
                 '小米','字节','比亚迪','宁德','中芯','紫光']
    MAT_KEYS  = ['material','材料','新材料','碳纤维','钛','锂','稀土','先进制造',
                 'robot','机器人','energy','能源','electric','电池']

    def tag_article(a):
        text = (a.get('title','') + ' ' + a.get('desc','')).lower()
        tag_str = ' '.join(a.get('tags', [])).lower()
        combined = text + ' ' + tag_str
        if any(k in combined for k in SEMI_KEYS): return 'semi'
        if any(k in combined for k in CN_KEYS):   return 'china'
        if any(k in combined for k in MAT_KEYS):  return 'material'
        if any(k in combined for k in AI_KEYS):   return 'ai'
        return 'other'

    buckets = {'semi': [], 'ai': [], 'china': [], 'material': [], 'other': []}
    for a in sorted(pool, key=lambda x: x['weight'], reverse=True):
        buckets[tag_article(a)].append(a)

    print(f"  领域分布 → 半导体:{len(buckets['semi'])} AI:{len(buckets['ai'])} "
          f"中国:{len(buckets['china'])} 材料:{len(buckets['material'])} 其他:{len(buckets['other'])}")

    candidate, seen2 = [], set()
    for cat, quota in [('semi',40), ('ai',30), ('china',30), ('material',20), ('other',30)]:
        for a in buckets[cat][:quota]:
            if a['uid'] not in seen2:
                candidate.append(a)
                seen2.add(a['uid'])

    if len(candidate) < 150:
        for a in sorted(pool, key=lambda x: x['weight'], reverse=True):
            if a['uid'] not in seen2:
                candidate.append(a)
                seen2.add(a['uid'])
            if len(candidate) >= 150: break

    print(f"✅ 候选池 {len(candidate)} 条（分层采样，已排除历史重复）\n")
    return candidate

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

def get_recent_topics() -> list[str]:
    """
    读取最近3天的报告文件，提取已经写过的主题关键词。
    返回类似 ['OpenAI生物防御', '英伟达Blackwell出口管制', '台积电涨价'] 这样的主题列表。
    """
    topics = []
    today = datetime.date.today()
    for days_ago in range(1, HISTORY_DAYS + 1):
        d = today - datetime.timedelta(days=days_ago)
        date_str = d.strftime("%Y-%m-%d")
        # 早班/午班/无时段 三种格式都试
        for suffix in ['_早班', '_午班', '']:
            path = f"reports/{date_str}{suffix}.md"
            if not os.path.exists(path):
                continue
            try:
                with open(path, encoding='utf-8') as f:
                    text = f.read()
                # 提取所有深度文章标题
                titles = re.findall(r'##\s+深度[文章]*\d*[：:]\s*(.+)', text)
                topics.extend(titles)
            except Exception:
                continue
    return topics[:40]  # 最多带40条


def select_topics(pool: list[dict]) -> tuple[list[dict], list[dict]]:
    """Pro模型一次选题，返回 (deep_10, brief_10) 两个列表"""
    items = []
    for i, a in enumerate(pool[:150]):
        items.append(
            f"[{i+1:03d}] 【{a['source']}】权重{a['weight']} | "
            f"{a['title']} | {a['desc'][:100]}"
        )
    news_text = "\n".join(items)

    # 读取最近3天已写过的主题，作为禁选清单
    recent_topics = get_recent_topics()
    forbidden_block = ""
    if recent_topics:
        forbidden_list = "\n".join(f"  • {t}" for t in recent_topics)
        forbidden_block = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ 主题去重清单（过去3天已写过的文章标题，共{len(recent_topics)}篇）

{forbidden_list}

【硬性规则】今天的10篇深度长文，**主题或核心事件**不得与上面任何一篇重复。
- 同一公司的同类事件视为重复（如已经写过"OpenAI生物防御"，今天不能再写"OpenAI生物安全""OpenAI预防滥用"等任何角度）
- 同一技术/产品的不同侧面视为重复（如已写过"台积电涨价"，今天不能再写"台积电产能紧张"等关联报道）
- 必须切换到全新的事件/公司/技术方向
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(f"📋 历史主题排除：过去3天已写过 {len(recent_topics)} 篇，今天必须切换主题")

    prompt = f"""今天是{TODAY}。
{forbidden_block}
以下是从100个新闻源抓取的资讯（共{len(items)}条）：
{news_text}

---

请完成两项选题任务。以下领域配额是硬性要求，不是建议，必须严格执行。

## 任务A：深度长文（必须恰好{TARGET_DEEP}条，领域配额不可违反）

硬性配额：
1. 半导体/芯片/GPU/算力/HBM/封装 → 必须3篇（最高优先级）
2. 人工智能/大模型/推理/Agent → 必须2篇
3. AI+人形机器人/具身智能/工业自动化 → 必须2篇（AI如何落地物理世界，必须分析上下游产业链）
4. 中国科技/国产替代/A股产业链 → 必须1篇
5. 投资/融资/估值/商业模式 → 必须1篇
6. 宏观/政策/地缘/出口管制/新材料 → 必须1篇

规则：
- 软件工程/SaaS/企业服务不得占用上述名额
- 同一公司同一事件类的文章一天只能写1篇（如 OpenAI 生物防御类，写过就不能再换角度重写）
- "AI+人形机器人"2篇写作角度：AI技术如何驱动机器人，产业链上游（电机/减速器/传感器）→ 中游（系统集成/本体）→ 下游（应用场景）各有哪些代表公司
- 如某领域当日无新闻，可往相关产业链方向找替代

## 任务B：精选快讯（必须恰好{TARGET_BRIEF}条，不得与A重复，宁缺毋滥）

注意：只选信息价值最高的{TARGET_BRIEF}条，每条必须有具体数字或具体事件，没有实质信息量的不要。

硬性配额（共{TARGET_BRIEF}条）：
1. 半导体/芯片/算力/HBM → 必须3条
2. 人工智能/大模型/机器人 → 必须3条
3. 中国科技/A股/产业链 → 必须2条
4. 投资/融资/并购/政策 → 必须2条

仅输出JSON，不要任何解释：
{{
  "deep": [
    {{"index": 编号, "title": "原标题", "source": "来源", "domain": "领域标签", "angle": "深度写作角度（机器人类必须注明产业链视角）"}}
  ],
  "brief": [
    {{"index": 编号, "title": "原标题", "source": "来源", "domain": "领域标签"}}
  ]
}}"""

    print(f"  🎯 选题中（Pro）…")
    content = _chat(MODEL_FAST,
                    [{"role": "system", "content":
                      "你是一位专注半导体和AI产业的选题编辑。"
                      "你必须严格按照用户给出的硬性配额执行，不得自行调整领域比例。"
                      "半导体/芯片/算力是最高优先级，必须保证名额。"},
                     {"role": "user", "content": prompt}],
                    max_tokens=3000, temperature=0.2)
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

        # ── 验证并强制半导体配额 ──
        SEMI_KEYS = ['semiconductor','chip','gpu','hbm','tsmc','nvidia','算力',
                     '芯片','半导体','封装','存储','制程','wafer','eda']
        def is_semi(a):
            text = (a.get('title','') + ' ' + a.get('desc','') + ' ' +
                    a.get('domain','')).lower()
            return any(k in text for k in SEMI_KEYS)

        semi_in_deep = [a for a in deep if is_semi(a)]
        if len(semi_in_deep) < 3:
            # 从候选池里补充半导体文章
            pool_semi = [a for a in pool if is_semi(a) and
                         a["uid"] not in {x["uid"] for x in deep}]
            needed = 3 - len(semi_in_deep)
            # 替换掉deep里非核心领域的文章
            non_core = [a for a in deep if not is_semi(a) and
                        a.get('domain','') not in ['人工智能','大模型','中国科技','国产替代']]
            replace_count = min(needed, len(non_core), len(pool_semi))
            for i in range(replace_count):
                deep.remove(non_core[i])
                pool_semi[i]['domain'] = pool_semi[i].get('domain','') or '半导体'
                pool_semi[i]['angle']  = '从产业链和投资角度分析此事件对中国算力/芯片产业的影响'
                deep.append(pool_semi[i])
            print(f"⚡ 半导体配额补充：+{replace_count}篇 → 总计{len([a for a in deep if is_semi(a)])}篇")

        print(f"✅ 选题完成 → 深度 {len(deep)} 篇 · 快讯 {len(brief)} 条")
        # 打印领域分布供核查
        deep_domains = [a.get('domain','未分类') for a in deep]
        print(f"   深度领域分布: {', '.join(deep_domains)}")
        return deep, brief
    except Exception as ex:
        print(f"⚠️  选题解析错误: {ex}")
        return pool[:TARGET_DEEP], pool[TARGET_DEEP:TARGET_DEEP+TARGET_BRIEF]

# ══════════════════════════════════════════════════════
# Step 3 · 写作（Pro模型，分批调用）
# ══════════════════════════════════════════════════════
SYSTEM_PROMPT_WRITER = """你是一位中国顶级财经记者，同时具备产业研究员和价值投资人的双重视角。你的文章风格参照《财经》杂志、《第一财经》、《哈佛商业评论》中文版的最高水准——沉稳、真实、有判断力、让人读完以后对产业有更深的理解。

━━ 核心写作原则：

① 【沉稳克制】不用感叹号，不堆砌形容词，不说"颠覆性""革命性"等空话。用事实和数字说话。

② 【产业链思维】每篇文章必须回答：这件事在整条产业链上处于哪个位置？上游/中游/下游谁受益、谁受损？

③ 【投资视角】谁赚钱？谁会亏？哪家公司的竞争壁垒被改变？

④ 【人形机器人/具身智能专项】凡涉及机器人的文章必须分析：
   - AI与机器人的连接点（感知/决策/控制哪个环节AI在发挥作用）
   - 产业链结构：上游零部件（电机、谐波减速器、RV减速器、力矩传感器、视觉芯片）→ 中游本体与系统集成 → 下游应用场景（汽车/物流/服务业）
   - 中国产业链位置：哪些环节有优势，哪些依赖进口
   - 代表性企业：只梳理产业链各环节代表公司帮助理解结构，不做股票推荐

━━ 铁律（违反则重写）：

① 每篇约500字（±80字）

② 【最核心铁律】每个专业名词第一次出现时，必须立即在括号内解释：
   名词（通俗解释——为什么对普通投资者重要）
   示例：
   · HBM（高带宽内存——AI训练的"血管"，决定GPU数据吞吐速度，SK海力士和三星垄断供应链上游）
   · 谐波减速器（机器人关节核心精密零件——决定运动精度，日本Harmonic Drive长期垄断，国内绿的谐波在追赶）
   · 力矩传感器（让机器人有"触觉"的零件——具身智能的关键，国内汉威科技、柯力传感等在突破）
   解释融入正文，自然流畅，绝不单独列术语表

③ 开头第一句必须是有信息量的结论，禁止用"近日""随着""据悉""日前"开头

④ 结尾必须有【今日启示】：一个具体可操作的产业或投资建议，不超过两句话

⑤ 文章结构：核心判断(1段) → 产业背景与链条分析(2段) → 竞争格局/赢家输家(1段) → 启示(1句)

⑥ 重点领域必须分析中国视角：国产替代、A股产业链、地缘政治"""


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

    print(f"  ⚡ 快讯 ({len(briefs)}条) → {MODEL_FAST}（Pro）…")
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
    """
    导读生成：直接从 selected（选题阶段的文章对象）构造摘要，
    不再从 deep_text（拼接后的长文）反向解析——因为分隔符匹配不稳定会导致空输出。
    """
    domains = [a.get("domain","") for a in selected if a.get("domain")]
    domain_list = "、".join(dict.fromkeys(domains)) if domains else "AI/半导体/产业"

    # 直接用 selected 前10篇（即深度文章列表）构造摘要
    summaries = []
    for i, a in enumerate(selected[:10], 1):
        title  = a.get('title', f'文章{i}')[:50]
        domain = a.get('domain', '科技')
        desc   = a.get('desc', '')[:140].replace('\n', ' ')
        summaries.append(f"{i}. 【{domain}】{title} —— {desc}")

    summary_text = "\n".join(summaries)
    if not summary_text.strip():
        # 兜底：万一selected为空也不能让导读为空
        summary_text = "（今日选题数据缺失，按通用框架生成导读）"

    prompt = f"""今天是{TODAY}。以下是今日10篇深度文章的标题和摘要：

{summary_text}

今日覆盖领域：{domain_list}

---

任务：写一段每日导读，严格按下面三步执行。

【第一步】导读必须以这句话开头，逐字输出，一个字都不能省：

早，今天是{TODAY},王sir为您汇报今天的重要资讯。

【第二步】紧接着写一段正文（约150字），点出今日3条最重要资讯：
- 每条用"·"分隔，1-2句说清楚发生了什么+为什么对投资或产业重要
- 优先半导体/算力/AI/机器人/产业链内容
- 用**加粗**标出今天最值得关注的1条
- 风格：中国顶级财经记者，沉稳克制，不用感叹号，不用"颠覆性""革命性"等空话

【第三步】最后一行（单独一行）输出关键词：
今日关键词：XXX · XXX · XXX · XXX

整体输出示例（参照格式但不要复制内容）：

早，今天是2026年XX月XX日,王sir为您汇报今天的重要资讯。今日**台积电再次表态AI需求超预期并明示先进制程将涨价**，全球GPU/手机/汽车芯片BOM成本面临上行压力·英伟达Blackwell GPU出口管制被参议院传唤，中美算力割裂加深·索尼携手台积电推出边缘AI图像传感器，端侧推理产业链迎来新的价值锚点。

今日关键词：先进制程涨价 · 算力管制 · 边缘AI · 产业链

注意：第一步那句话必须原样输出，不能改成"早上好"或加任何前缀。如果省略这句话，整段导读视为失败。"""

    return _chat(
        MODEL_FAST,
        [{"role": "system", "content":
          "你是中国顶级财经记者，写作沉稳精准。你的任务是写每日导读。"
          "用户的第一步指令是'逐字输出一句话'，你必须严格执行，不得省略或改写。"},
         {"role": "user", "content": prompt}],
        max_tokens=800, temperature=0.4,
    )

# ══════════════════════════════════════════════════════
# Step 5 · 保存
# ══════════════════════════════════════════════════════
def save(header: str, body: str, pool_size: int) -> str:
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{DATE_STR}.md"
    content = f"""# 🧠 每日科技投资深度简报 · {TODAY}

> 数据来源：{len(SESSION_SOURCES)}/{len(ALL_SOURCES)} 个精选新闻源 · 今日抓取 {pool_size} 条相关资讯  
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
def save(header: str, deep_text: str, brief_text: str,
         pool_size: int, deep_list: list, brief_list: list) -> tuple:
    """
    保存报告，返回 (报告路径, 本次发布的uid列表)
    报告名区分时段：2026-06-04_早班.md / 2026-06-04_午班.md
    """
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{DATE_STR}_{SESSION}.md"
    content = f"""# 🧠 每日科技投资简报 · {TODAY} · {SESSION}

> 数据来源：{len(SESSION_SOURCES)}/{len(ALL_SOURCES)} 个精选新闻源 · 候选池 {pool_size} 条
> 写作模型：**DeepSeek V4 Pro**（全链路）
> 发布时段：{SESSION} · 格式：10篇深度长文 + 20条快讯

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

*由 GitHub Actions + DeepSeek API 自动生成 · {TODAY} {SESSION}*
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告保存：{path}")

    # 收集本次发布的所有uid
    published = [a["uid"] for a in deep_list] + [a["uid"] for a in brief_list]
    return path, published


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
    print(f"  🧠 每日科技投资简报  ·  {TODAY}  ·  {SESSION}")
    print(f"  深度：{TARGET_DEEP}篇 × {MODEL_WRITER}")
    print(f"  快讯：{TARGET_BRIEF}条 × {MODEL_FAST}")
    print(f"  去重范围：最近 {HISTORY_DAYS} 天 · 新闻时效：{NEWS_MAX_DAYS} 天")
    print(f"{'═'*58}\n")

    # 0. 读取历史已发布uid（用于去重）
    history       = load_published_history()
    published_uids = get_published_uids(history)

    # 1. 抓取（排除已发布内容）
    pool = collect_news(published_uids)
    if not pool:
        print("❌ 未抓取到任何新鲜资讯，退出"); sys.exit(1)

    # 2. 选题（硬性配额 + 主题去重）
    deep_list, brief_list = select_topics(pool)
    print(f"\n📌 深度 {len(deep_list)} 篇 · 快讯 {len(brief_list)} 条，开始写作…\n")

    # 3. 写作（全部Pro模型）
    deep_text  = write_all_deep(deep_list)
    brief_text = write_briefs(brief_list)

    # 4. 导读（用 deep_list 而不是截断的 deep_text）
    header = make_header(deep_text, deep_list)

    # 5. 保存报告 + 记录已发布uid
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/{DATE_STR}_{SESSION}.md"
    content = f"""# 🧠 每日科技投资简报 · {TODAY} · {SESSION}

> 数据来源：{len(SESSION_SOURCES)}/{len(ALL_SOURCES)} 个精选新闻源（随机分层采样）
> 写作模型：DeepSeek V4 Pro（全链路）
> 发布时段：{SESSION}

---

## 📋 今日导读

{header}

---

## 📰 深度长文（{TARGET_DEEP}篇）

{deep_text}

---

## ⚡ 精选快讯（{TARGET_BRIEF}条）

{brief_text}

---

*由 GitHub Actions + DeepSeek API 自动生成 · {TODAY} {SESSION}*
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告保存：{report_path}")

    # 记录已发布uid，用于明天去重
    new_uids = [a["uid"] for a in deep_list] + [a["uid"] for a in brief_list]
    save_published_uids(history, new_uids)

    # 更新README
    update_readme(header, deep_text, brief_text)

    # 6. 推送微信
    from push import push_all
    push_all(header, deep_text, brief_text, DATE_STR)

    print("\n" + "─"*58)
    print(f"📋 {SESSION} 导读：")
    print("─"*58)
    print(header[:300])
    print("─"*58)
    print(f"\n🎉 {SESSION}完成！{TARGET_DEEP}篇深度 + {TARGET_BRIEF}条快讯 · 已推送")
