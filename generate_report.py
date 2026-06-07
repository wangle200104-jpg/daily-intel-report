"""
generate_report.py  v10  —  每日科技投资简报
架构：Pipeline 模式（参考 arxiv-sanity + ai-news-aggregator 最佳实践）

Step 0  随机选源      pick_session_sources()
Step 1  抓取新闻      collect_news()          → list[Article]
Step 2  文章评分      score_articles()         → list[Article] 按分排序
Step 3  历史去重      filter_published()       → list[Article]
Step 4  选题          select_topics()          → (deep[], brief[])
Step 5  写作          write_all_deep() / write_briefs()
Step 6  生成导读      make_header()
Step 7  保存 + 推送   save() / push_all()

聚焦领域：半导体 · 算力 · 材料 · 人工智能
推送：早班09:00 + 午班16:00，每次随机30个源，内容不重复
"""

# ──────────────────────────────────────────────────────
# 依赖
# ──────────────────────────────────────────────────────
import os, sys, json, time, datetime, hashlib, re, random
import xml.etree.ElementTree as ET

try:
    import requests
    from openai import OpenAI
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "requests", "openai", "--break-system-packages", "-q"])
    import requests
    from openai import OpenAI

from sources import ALL_SOURCES, KEYWORDS

# ──────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────
API_KEY   = os.environ.get("DEEPSEEK_API_KEY", "").strip()
MODEL     = "deepseek-v4-pro"          # 全链路使用同一个 Pro 模型

_now_utc  = datetime.datetime.utcnow()
NOW_HOUR  = (_now_utc.hour + 8) % 24  # 北京时间
SESSION   = "午班" if NOW_HOUR >= 14 else "早班"
TODAY     = datetime.date.today().strftime("%Y年%m月%d日")
DATE_STR  = datetime.date.today().strftime("%Y-%m-%d")

N_DEEP    = 10    # 深度长文篇数
N_BRIEF   = 10    # 精选快讯条数（宁缺毋滥）
N_SOURCES = 30    # 每次随机选源数
BATCH     = 5     # 长文每批写几篇
BATCH_GAP = 12    # 批次间隔（秒，防并发限速）
CALL_GAP  = 3     # 每次 API 调用后的基础间隔

HISTORY_FILE = "reports/published_uids.json"
HISTORY_DAYS = 3   # 保留最近 N 天的去重记录
NEWS_DAYS    = 3   # 只抓最近 N 天的新闻

if not API_KEY:
    print("❌ 未找到 DEEPSEEK_API_KEY，请检查 GitHub Secrets")
    sys.exit(1)

print(f"✅ API Key ...{API_KEY[-4:]}  |  {SESSION}  |  {TODAY}")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# ──────────────────────────────────────────────────────
# Step 0  随机选源（早班/午班使用不同种子）
# ──────────────────────────────────────────────────────
def pick_session_sources(n: int = N_SOURCES) -> list[dict]:
    """
    分层加权随机选源。
    策略来自 ai-news-aggregator 最佳实践：
      - 权重10（顶级源）全部保留
      - 其余层按比例随机抽取
    早班/午班使用不同随机种子 → 覆盖不同新闻面
    """
    seed = int(hashlib.md5(f"{DATE_STR}-{SESSION}".encode()).hexdigest(), 16) % (2**31)
    rng  = random.Random(seed)

    w10 = [s for s in ALL_SOURCES if s["weight"] == 10]
    w9  = [s for s in ALL_SOURCES if s["weight"] == 9]
    w8  = [s for s in ALL_SOURCES if s["weight"] == 8]
    w7  = [s for s in ALL_SOURCES if s["weight"] <= 7]

    picked = (w10
              + rng.sample(w9, min(6, len(w9)))
              + rng.sample(w8, min(5, len(w8)))
              + rng.sample(w7, min(3, len(w7))))

    if len(picked) > n:
        must   = w10[:]
        others = [s for s in picked if s not in must]
        picked = must + rng.sample(others, max(0, n - len(must)))

    rng.shuffle(picked)
    print(f"🎲 {SESSION}选源 {len(picked)}/{len(ALL_SOURCES)} 个"
          f"（权重10全选{len(w10)}个）")
    return picked

SESSION_SOURCES = pick_session_sources()

# ──────────────────────────────────────────────────────
# API 统一调用（含完整错误处理 + 自动重试）
# ──────────────────────────────────────────────────────
def _chat(messages: list, max_tokens: int = 4000, temperature: float = 0.7,
          system: str = "") -> str:
    from openai import AuthenticationError, RateLimitError, APIStatusError

    if system:
        messages = [{"role": "system", "content": system}] + messages

    for attempt in range(1, 5):
        try:
            resp = client.chat.completions.create(
                model=MODEL, max_tokens=max_tokens,
                temperature=temperature, messages=messages,
            )
            time.sleep(CALL_GAP)
            return resp.choices[0].message.content or ""

        except AuthenticationError:
            print(f"\n❌ 401 认证失败（第{attempt}次）")
            if attempt < 3:
                print(f"  等待 {20*attempt}s 重试（DeepSeek 高并发时会临时拒绝）…")
                time.sleep(20 * attempt)
            else:
                print("  请检查：1) platform.deepseek.com 余额  2) GitHub Secret DEEPSEEK_API_KEY")
                sys.exit(1)

        except RateLimitError:
            wait = 20 * attempt
            print(f"  ⚠️ 429 限速，等 {wait}s…")
            time.sleep(wait)

        except APIStatusError as e:
            if e.status_code == 402:
                print("❌ 余额不足，请充值 platform.deepseek.com")
                sys.exit(1)
            elif e.status_code >= 500:
                time.sleep(15 * attempt)
            else:
                print(f"❌ API {e.status_code}: {e}")
                sys.exit(1)

        except Exception as e:
            print(f"  ⚠️ 未知错误（{attempt}次）: {e}")
            time.sleep(8)

    return ""

# ──────────────────────────────────────────────────────
# 历史去重模块
# ──────────────────────────────────────────────────────
def load_history() -> dict:
    os.makedirs("reports", exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            data = json.load(f)
        cutoff = datetime.date.today() - datetime.timedelta(days=HISTORY_DAYS)
        return {k: v for k, v in data.items()
                if datetime.date.fromisoformat(k.split("_")[0]) >= cutoff}
    except Exception:
        return {}

def get_used_uids(history: dict) -> set:
    used = set()
    for uids in history.values():
        used.update(uids)
    print(f"📋 历史去重：{len(history)} 个时段，已发布 {len(used)} 篇")
    return used

def save_history(history: dict, new_uids: list) -> None:
    history[f"{DATE_STR}_{SESSION}"] = new_uids
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"✅ 历史记录已更新：{DATE_STR}_{SESSION} → {len(new_uids)} 篇")

def get_past_titles() -> list[str]:
    """读取近3天报告里的所有深度文章标题，用于主题级去重"""
    titles = []
    today  = datetime.date.today()
    for d in range(1, HISTORY_DAYS + 1):
        ds = (today - datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        for sfx in ["_早班", "_午班", ""]:
            p = f"reports/{ds}{sfx}.md"
            if not os.path.exists(p):
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    text = f.read()
                titles += re.findall(r"##\s+深度[文章]*\d*[：:]\s*(.+)", text)
            except Exception:
                pass
    return titles[:40]

# ──────────────────────────────────────────────────────
# Step 1  RSS 抓取
# ──────────────────────────────────────────────────────
def _text(entry, *tags) -> str:
    for t in tags:
        el = entry.find(t)
        if el is not None and el.text:
            return el.text.strip()
    return ""

def is_recent(pub: str) -> bool:
    if not pub:
        return True
    fmts = ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]
    today = datetime.date.today()
    for fmt in fmts:
        try:
            dt   = datetime.datetime.strptime(pub.strip(), fmt)
            date = dt.date() if hasattr(dt, "date") else dt
            if hasattr(date, "date"):
                date = date.date()
            return (today - date).days <= NEWS_DAYS
        except Exception:
            pass
    return True

def fetch_source(src: dict) -> list[dict]:
    articles, headers = [], {"User-Agent": "IntelBriefBot/4.0"}
    try:
        r = requests.get(src["url"], timeout=12, headers=headers)
        r.raise_for_status()
        root    = ET.fromstring(r.content)
        entries = (root.findall(".//item")
                   or root.findall(".//{http://www.w3.org/2005/Atom}entry"))
        for e in entries[:20]:
            title = _text(e, "title", "{http://www.w3.org/2005/Atom}title")
            desc  = _text(e, "description", "summary",
                          "{http://www.w3.org/2005/Atom}summary",
                          "{http://www.w3.org/2005/Atom}content")
            link  = _text(e, "link", "{http://www.w3.org/2005/Atom}link")
            pub   = _text(e, "pubDate", "updated",
                          "{http://www.w3.org/2005/Atom}published",
                          "{http://www.w3.org/2005/Atom}updated")
            if not title:
                continue
            if pub and not is_recent(pub):
                continue
            combined = (title + " " + desc).lower()
            if not any(k.lower() in combined for k in KEYWORDS):
                continue
            uid = hashlib.md5(title.lower().strip().encode()).hexdigest()[:12]
            articles.append({
                "uid":    uid,
                "title":  title,
                "desc":   re.sub(r"<[^>]+>", "", desc)[:350],
                "source": src["name"],
                "weight": src["weight"],
                "tags":   src.get("tags", []),
                "pub":    pub,
                "link":   link,
            })
            if len(articles) >= 6:
                break
    except Exception as ex:
        print(f"  ⚠️  {src['name']}: {str(ex)[:60]}")
    return articles

# ──────────────────────────────────────────────────────
# Step 2  文章评分（参考 arxiv-sanity TF-IDF 思路）
# ──────────────────────────────────────────────────────
# 领域关键词权重表（匹配越多分越高）
DOMAIN_SCORES = {
    # 半导体/算力（最高优先级）
    "semiconductor": 5, "chip": 5, "gpu": 5, "hbm": 6, "tsmc": 5,
    "nvidia": 5, "amd": 4, "intel": 4, "asml": 6, "euv": 6,
    "cowos": 6, "chiplet": 5, "packaging": 5, "foundry": 5, "3nm": 5,
    "datacenter": 4, "compute": 4, "算力": 5, "芯片": 5, "半导体": 5,
    "封装": 5, "存储": 4, "制程": 5, "光刻": 6,
    # 材料（你的专业背景）
    "materials": 4, "battery": 4, "solid-state": 5, "rare-earth": 5,
    "sic": 5, "gan": 5, "graphene": 4, "perovskite": 4,
    "新材料": 5, "碳化硅": 5, "稀土": 5, "固态电池": 5,
    # AI
    "llm": 3, "model": 2, "inference": 3, "training": 3, "agent": 3,
    "deepseek": 4, "大模型": 3, "人工智能": 3,
    # 机器人/具身
    "humanoid": 5, "robot": 4, "embodied": 5, "reducer": 5,
    "人形机器人": 5, "具身智能": 5, "减速器": 5,
    # 投资/产业链
    "billion": 3, "funding": 3, "investment": 3, "supply chain": 4,
    "产业链": 4, "国产替代": 4,
    # 地缘/出口管制
    "export control": 5, "ban": 3, "sanction": 4, "出口管制": 5,
}

def score_article(a: dict) -> float:
    text  = (a["title"] + " " + a["desc"]).lower()
    score = float(a["weight"])  # 基础分 = 来源权重
    for kw, pts in DOMAIN_SCORES.items():
        if kw in text:
            score += pts
    # 标题命中额外加分
    title_lower = a["title"].lower()
    for kw, pts in DOMAIN_SCORES.items():
        if kw in title_lower:
            score += pts * 0.5
    return round(score, 2)

# ──────────────────────────────────────────────────────
# Step 1+2 综合：抓取 → 评分 → 去重 → 分层候选池
# ──────────────────────────────────────────────────────
def collect_news(used_uids: set) -> list[dict]:
    print(f"\n📡 {SESSION} 抓取 {len(SESSION_SOURCES)}/{len(ALL_SOURCES)} 个源…")
    pool, seen = [], set()

    for i, src in enumerate(SESSION_SOURCES, 1):
        arts = fetch_source(src)
        new  = [a for a in arts if a["uid"] not in seen]
        for a in new:
            seen.add(a["uid"])
        pool.extend(new)
        if new:
            print(f"  [{i:2d}/{len(SESSION_SOURCES)}] {src['name']}: +{len(new)}")
        time.sleep(0.15)

    print(f"\n✅ 抓取完成：{len(pool)} 条")

    # 排除历史已发布
    before = len(pool)
    pool   = [a for a in pool if a["uid"] not in used_uids]
    if before - len(pool) > 0:
        print(f"  🚫 排除已发布 {before-len(pool)} 条 → 剩余 {len(pool)} 条新鲜内容")

    # 文章评分
    for a in pool:
        a["score"] = score_article(a)

    # 分层候选池（保证各领域都有足够候选）
    SEMI_KW = ["semiconductor","chip","gpu","hbm","tsmc","nvidia","amd","asml",
               "cowos","chiplet","packaging","foundry","算力","芯片","半导体",
               "封装","存储","制程","光刻","euv","hpc","datacenter"]
    AI_KW   = ["llm","gpt","claude","gemini","deepseek","openai","anthropic",
               "large language","大模型","人工智能","ai agent","inference"]
    MAT_KW  = ["materials","battery","solid-state","rare-earth","sic","gan",
               "新材料","碳化硅","稀土","固态电池","robot","humanoid","embodied",
               "人形机器人","具身智能","减速器"]
    CN_KW   = ["china","chinese","华为","中国","国产","a股","产业链","国产替代"]

    def tag(a):
        t = (a["title"] + " " + a["desc"]).lower()
        if any(k in t for k in SEMI_KW):  return "semi"
        if any(k in t for k in MAT_KW):   return "mat"
        if any(k in t for k in CN_KW):    return "cn"
        if any(k in t for k in AI_KW):    return "ai"
        return "other"

    buckets = {"semi": [], "ai": [], "mat": [], "cn": [], "other": []}
    for a in sorted(pool, key=lambda x: x["score"], reverse=True):
        buckets[tag(a)].append(a)

    print(f"  分桶 → 半导体:{len(buckets['semi'])} AI:{len(buckets['ai'])} "
          f"材料机器人:{len(buckets['mat'])} 中国:{len(buckets['cn'])} 其他:{len(buckets['other'])}")

    # 构建候选池：半导体优先，各桶按比例抽取
    candidate, seen2 = [], set()
    for cat, quota in [("semi",50), ("ai",30), ("mat",30), ("cn",25), ("other",20)]:
        for a in buckets[cat][:quota]:
            if a["uid"] not in seen2:
                candidate.append(a)
                seen2.add(a["uid"])

    # 不足则补充
    if len(candidate) < 100:
        for a in sorted(pool, key=lambda x: x["score"], reverse=True):
            if a["uid"] not in seen2:
                candidate.append(a)
                seen2.add(a["uid"])
            if len(candidate) >= 100:
                break

    # 最终按评分排序
    candidate.sort(key=lambda x: x["score"], reverse=True)
    print(f"✅ 候选池 {len(candidate)} 条（按评分排序，半导体优先）\n")
    return candidate

# ──────────────────────────────────────────────────────
# Step 4  选题
# ──────────────────────────────────────────────────────
def select_topics(pool: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Pro 模型一次完成选题。
    加入：① 主题去重清单（3天内已写过的文章标题）
          ② 硬性领域配额（不能随意变更）
          ③ 评分排序后的候选摘要
    """
    # 候选摘要（只取前150条，评分已排序）
    items = []
    for i, a in enumerate(pool[:150], 1):
        items.append(
            f"[{i:03d}|分{a['score']:.0f}] 【{a['source']}】"
            f"{a['title']} | {a['desc'][:80]}"
        )
    news_text = "\n".join(items)

    # 历史主题禁选清单
    past_titles = get_past_titles()
    forbidden   = ""
    if past_titles:
        fl = "\n".join(f"  · {t}" for t in past_titles)
        forbidden = f"""
⛔ 【主题去重清单】以下是过去{HISTORY_DAYS}天已写过的{len(past_titles)}篇文章标题，今天不得重复：
{fl}

规则：同一公司的同类事件 = 重复（如已写"OpenAI生物防御"，则任何OpenAI生物安全角度都不能选）
"""
        print(f"📋 主题去重：{len(past_titles)} 条历史标题已告知 AI")

    prompt = f"""今天是{TODAY}，时段：{SESSION}。
{forbidden}
以下是按评分排序的候选新闻（共{len(items)}条，评分越高优先级越高）：
{news_text}

━━ 选题任务 ━━

A. 深度长文（恰好{N_DEEP}条）— 硬性配额，不可违反：
  1. 半导体/芯片/GPU/算力/HBM/封装/光刻  → 必须3篇
  2. 人工智能/大模型/推理/Agent           → 必须2篇
  3. AI+人形机器人/具身智能/产业链        → 必须2篇（写明上下游：电机/减速器→本体→应用）
  4. 中国科技/国产替代/A股产业链          → 必须1篇
  5. 投资/融资/估值/商业模式              → 必须1篇
  6. 宏观/政策/地缘/出口管制/新材料       → 必须1篇
  禁止：软件工程/SaaS/企业服务 占用上述名额

B. 精选快讯（恰好{N_BRIEF}条，不与A重复）— 宁缺毋滥，每条必须有具体数字：
  1. 半导体/芯片/算力/HBM  → 必须3条
  2. AI/大模型/机器人      → 必须3条
  3. 中国科技/A股/产业链   → 必须2条
  4. 投资/融资/并购/政策   → 必须2条

仅输出 JSON，不要其他任何文字：
{{
  "deep":  [{{"idx":编号,"title":"原标题","source":"来源","domain":"领域标签","angle":"写作角度（机器人类必须含产业链上下游）"}}],
  "brief": [{{"idx":编号,"title":"原标题","source":"来源","domain":"领域标签"}}]
}}"""

    print("  🎯 选题中（Pro）…")
    raw = _chat([{"role": "user", "content": prompt}],
                max_tokens=3000, temperature=0.2,
                system="你是专注半导体和AI产业的资深选题编辑。必须严格按配额执行，半导体/算力是最高优先级。")

    if not raw:
        print("  ⚠️ 选题返回空，使用评分前N条兜底")
        return pool[:N_DEEP], pool[N_DEEP:N_DEEP+N_BRIEF]

    # 解析JSON
    try:
        m    = re.search(r'\{[\s\S]+\}', raw)
        data = json.loads(m.group(0)) if m else {}
    except Exception:
        data = {}

    uid_map = {i+1: a for i, a in enumerate(pool[:150])}

    def resolve(lst):
        result, seen = [], set()
        for item in lst:
            idx = item.get("idx", 0)
            a   = uid_map.get(idx)
            if a and a["uid"] not in seen:
                a = dict(a)
                a["domain"] = item.get("domain", a.get("domain", ""))
                a["angle"]  = item.get("angle", "")
                result.append(a)
                seen.add(a["uid"])
        return result

    deep  = resolve(data.get("deep",  []))[:N_DEEP]
    brief = resolve(data.get("brief", []))[:N_BRIEF]

    # 深度和快讯去重
    deep_uids = {a["uid"] for a in deep}
    brief     = [a for a in brief if a["uid"] not in deep_uids][:N_BRIEF]

    # 验证半导体配额
    SEMI_CHECK = ["semiconductor","chip","gpu","hbm","tsmc","nvidia",
                  "算力","芯片","半导体","封装","制程","光刻","asml"]
    def is_semi(a):
        t = (a.get("title","") + a.get("desc","") + a.get("domain","")).lower()
        return any(k in t for k in SEMI_CHECK)

    semi_cnt = sum(1 for a in deep if is_semi(a))
    if semi_cnt < 3:
        pool_semi = [a for a in pool if is_semi(a) and a["uid"] not in {x["uid"] for x in deep}]
        non_core  = [a for a in deep if not is_semi(a)
                     and a.get("domain","") not in ["人工智能","大模型","中国科技"]]
        add = min(3 - semi_cnt, len(non_core), len(pool_semi))
        for i in range(add):
            deep.remove(non_core[i])
            pool_semi[i]["domain"] = "半导体"
            pool_semi[i]["angle"]  = "从产业链和投资角度分析对中国算力/芯片产业的影响"
            deep.append(pool_semi[i])
        print(f"  ⚡ 半导体配额补充 +{add} 篇")

    domains = [a.get("domain","?") for a in deep]
    print(f"✅ 选题完成 → 深度 {len(deep)} 篇 · 快讯 {len(brief)} 条")
    print(f"   领域：{' | '.join(domains)}")
    return deep, brief

# ──────────────────────────────────────────────────────
# Step 5  写作
# ──────────────────────────────────────────────────────
WRITER_SYSTEM = """你是一位中国顶级财经记者，同时具备产业研究员和价值投资人的双重视角。
文章风格参照《财经》杂志、《第一财经》最高水准——沉稳、真实、有判断力。

━━ 核心原则 ━━
① 【克制】不用感叹号，不堆砌形容词，不说"颠覆性""革命性"。数字说话。
② 【产业链思维】每篇必须回答：这件事在整条产业链哪个位置？上中下游谁受益谁受损？
③ 【投资视角】谁赚钱？谁会亏？哪家公司的竞争壁垒被改变？
④ 【机器人专项】涉及机器人/具身智能的文章必须分析：
   AI与机器人的连接点 → 产业链（上游：电机/谐波减速器/力矩传感器/视觉芯片
   → 中游：本体制造/系统集成 → 下游：汽车/物流/制造）→ 中国各环节竞争力

━━ 铁律 ━━
① 每篇约500字（±80字）
② 【最核心】每个专业名词第一次出现必须括号解释：名词（解释——为什么重要）
   示例：HBM（高带宽内存——AI训练的"血管"，SK海力士和三星垄断供应链上游）
         谐波减速器（机器人关节精密零件——决定运动精度，日本Harmonic Drive长期垄断）
③ 开头第一句必须是有信息量的结论，禁止"近日""随着""据悉"
④ 结尾必须有【今日启示】：具体可操作的产业或投资建议，不超过两句
⑤ 结构：核心判断(1段) → 产业背景与链条分析(2段) → 竞争格局/赢家输家(1段) → 启示"""

def write_batch(articles: list[dict], batch_num: int, total: int) -> str:
    items = []
    for i, a in enumerate(articles, 1):
        items.append(
            f"### 文章{i}（{a.get('domain','科技')}）\n"
            f"来源：{a['source']}\n"
            f"标题：{a['title']}\n"
            f"摘要：{a['desc']}\n"
            f"写作角度：{a.get('angle','从产业链和投资角度深度分析')}"
        )
    prompt = (f"今天是{TODAY}（{SESSION}）。请按照写作要求，"
              f"为以下{len(articles)}篇文章逐一撰写深度分析：\n\n"
              + "\n\n".join(items)
              + f"\n\n---\n输出格式：每篇以 ## 深度{(batch_num-1)*5+1 if len(articles)>1 else batch_num}：[标题] 开头，篇间用 \\n---\\n 分隔。")
    print(f"  📝 深度批次 {batch_num}/{total}（{len(articles)}篇）→ Pro…")
    return _chat([{"role": "user", "content": prompt}],
                 max_tokens=8000, temperature=0.72, system=WRITER_SYSTEM)

def write_all_deep(deep: list[dict]) -> str:
    batches = [deep[i:i+BATCH] for i in range(0, len(deep), BATCH)]
    parts   = []
    for i, batch in enumerate(batches, 1):
        parts.append(write_batch(batch, i, len(batches)))
        if i < len(batches):
            print(f"  ⏳ 批次间等待 {BATCH_GAP}s…")
            time.sleep(BATCH_GAP)
    return "\n\n---\n\n".join(parts)

def write_briefs(briefs: list[dict]) -> str:
    items = []
    for i, a in enumerate(briefs, 1):
        items.append(f"[{i:02d}] 【{a['source']}】{a['title']} | {a['desc'][:120]}")

    prompt = f"""今天是{TODAY}。以下是{len(briefs)}条精选新闻，逐条改写为快讯，必须全部输出。

{chr(10).join(items)}

输出格式（每条用 ===第N条=== 分隔）：

===第1条===
领域：[标签]
标题：[≤15字，必须含具体数字或关键事实]
正文：[70-100字，必须有：具体数字/金额/比例 + 为什么重要 + 产业链影响。专业名词括号解释]
启示：[一句话，点明对产业链哪个环节影响最大]

以此类推到第{len(briefs)}条，不可省略任何一条。"""

    print(f"  ⚡ 精选快讯 {len(briefs)} 条 → Pro…")
    return _chat([{"role": "user", "content": prompt}],
                 max_tokens=5000, temperature=0.55,
                 system="你是顶级财经编辑，为高净值投资人写精选快讯。每条必须有具体数字和产业链意义。")

# ──────────────────────────────────────────────────────
# Step 6  生成导读
# ──────────────────────────────────────────────────────
def make_header(deep_list: list[dict]) -> str:
    """直接用选题对象构造摘要，避免从深度长文反向解析的不稳定性"""
    summaries = []
    for i, a in enumerate(deep_list[:N_DEEP], 1):
        summaries.append(f"{i}. 【{a.get('domain','科技')}】{a['title'][:50]} — {a['desc'][:100]}")

    prompt = f"""今天是{TODAY}，{SESSION}。以下是今日{N_DEEP}篇深度文章的摘要：

{chr(10).join(summaries)}

━━ 任务 ━━

【第一步】必须逐字输出（不得省略、不得改写）：
早，今天是{TODAY}，王sir为您汇报今天的重要资讯。

【第二步】紧接着写约150字正文：
· 点出今日3条最重要资讯，每条1-2句（发生了什么 + 为什么重要）
· 半导体/算力/材料/机器人产业链优先
· 今天最值得关注的1条用**加粗**标出
· 风格：《财经》杂志记者，克制精准，不用感叹号

【第三步】最后单独一行：
今日关键词：XXX · XXX · XXX · XXX

严格禁止：早安/大家好/让我们/颠覆性/革命性，禁止感叹号。"""

    print("  📋 生成导读 → Pro…")
    return _chat([{"role": "user", "content": prompt}],
                 max_tokens=700, temperature=0.4,
                 system="你是中国顶级财经记者。必须严格执行第一步指令，逐字输出固定句，不得省略或改写。")

# ──────────────────────────────────────────────────────
# Step 7  保存 + 更新 README
# ──────────────────────────────────────────────────────
def save(header: str, deep_text: str, brief_text: str,
         pool_size: int, deep_list: list, brief_list: list) -> tuple:
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{DATE_STR}_{SESSION}.md"
    content = f"""# 🧠 每日科技投资简报 · {TODAY} · {SESSION}

> 来源：{len(SESSION_SOURCES)}/{len(ALL_SOURCES)} 个精选源（随机分层采样）· 候选 {pool_size} 条
> 模型：DeepSeek V4 Pro（全链路）· 聚焦：半导体/算力/材料/AI

---

## 📋 今日导读

{header}

---

## 📰 深度长文（{N_DEEP}篇）

{deep_text}

---

## ⚡ 精选快讯（{N_BRIEF}条）

{brief_text}

---
*{TODAY} {SESSION} · @wangsir1w*
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告：{path}")

    published = [a["uid"] for a in deep_list + brief_list]
    return path, published


def update_readme(header: str, deep_text: str) -> None:
    preview = (deep_text[:800] + "…") if len(deep_text) > 800 else deep_text
    content = f"""# 🧠 每日科技投资简报

> 聚焦：半导体 · 算力 · 材料 · 人工智能  
> 推送：每天 09:00 + 16:00  
> 作者：王sir @wangsir1w

## 最新简报 · {TODAY} {SESSION}

{header}

---

{preview}

---
*由 GitHub Actions + DeepSeek V4 Pro 自动生成*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

# ──────────────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'═'*60}")
    print(f"  🧠 每日科技投资简报  ·  {TODAY}  ·  {SESSION}")
    print(f"  模型：{MODEL}  |  深度：{N_DEEP}篇  |  快讯：{N_BRIEF}条")
    print(f"  去重：{HISTORY_DAYS}天  |  新闻时效：{NEWS_DAYS}天")
    print(f"{'═'*60}\n")

    # Step 0: 已在顶部执行（SESSION_SOURCES）

    # Step 1+2: 抓取 + 评分
    history    = load_history()
    used_uids  = get_used_uids(history)
    pool       = collect_news(used_uids)

    if not pool:
        print("❌ 候选池为空，退出"); sys.exit(1)

    # Step 4: 选题
    deep_list, brief_list = select_topics(pool)
    print(f"\n📌 深度 {len(deep_list)} 篇 · 快讯 {len(brief_list)} 条，开始写作…\n")

    # Step 5: 写作
    deep_text  = write_all_deep(deep_list)
    brief_text = write_briefs(brief_list)

    # Step 6: 导读
    header = make_header(deep_list)

    # Step 7: 保存
    _, new_uids = save(header, deep_text, brief_text,
                       len(pool), deep_list, brief_list)
    save_history(history, new_uids)
    update_readme(header, deep_text)

    # 推送
    from push import push_all
    push_all(header, deep_text, brief_text, DATE_STR)

    print("\n" + "─"*60)
    print(f"📋 {SESSION} 导读：")
    print("─"*60)
    print(header[:400])
    print("─"*60)
    print(f"\n🎉 {SESSION}完成！{N_DEEP}篇深度 + {N_BRIEF}条精选快讯 已推送")
