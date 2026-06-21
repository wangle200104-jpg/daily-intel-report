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
                           "requests", "openai", "tavily-python", "--break-system-packages", "-q"])
    import requests
    from openai import OpenAI

from sources import ALL_SOURCES, KEYWORDS

# ──────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────
API_KEY   = os.environ.get("DEEPSEEK_API_KEY", "").strip()
# Tavily 多 Key 轮换：逗号分隔多个 Key，某个用完（1000次/月）自动切下一个
_tavily_keys_raw = os.environ.get("TAVILY_API_KEY", "").strip()
TAVILY_KEYS      = [k.strip() for k in _tavily_keys_raw.split(",") if k.strip()]
MODEL     = "deepseek-v4-pro"          # 全链路使用同一个 Pro 模型

_now_utc  = datetime.datetime.utcnow()
NOW_HOUR  = (_now_utc.hour + 8) % 24   # 北京时间
# 早班 = 北京09:00（UTC 01:00），午班 = 北京15:30（UTC 07:30）
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

def extract_image(entry) -> str:
    """
    从RSS条目提取图片URL，支持4种格式：
    1. enclosure（Substack等）
    2. media:content / media:thumbnail（IEEE Spectrum/EE Times等）
    3. description 或 content:encoded 里的 <img> 标签
    """
    # 1. enclosure
    enc = entry.find('enclosure')
    if enc is not None:
        url = enc.get('url', '')
        if url and ('image' in enc.get('type', '') or
                    any(url.lower().endswith(x) for x in
                        ['.jpg', '.jpeg', '.png', '.webp', '.gif'])):
            return url

    # 2. media:content / media:thumbnail
    for ns in ['http://search.yahoo.com/mrss/']:
        for tag in ['content', 'thumbnail']:
            el = entry.find(f'{{{ns}}}{tag}')
            if el is not None and el.get('url'):
                u = el.get('url')
                if u.startswith('http'):
                    return u

    # 3. description / content:encoded 里的第一张 img
    for field in ['description',
                  '{http://www.w3.org/2005/Atom}summary',
                  '{http://purl.org/rss/1.0/modules/content/}encoded']:
        el = entry.find(field)
        if el is not None and el.text:
            imgs = re.findall(r'src=["\']([^"\']+)["\']', el.text)
            for img in imgs:
                if (img.startswith('http') and
                        'pixel' not in img and
                        '1x1' not in img and
                        len(img) > 20):
                    return img
    return ""


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
            uid   = hashlib.md5(title.lower().strip().encode()).hexdigest()[:12]
            image = extract_image(e)   # ← 提取来源图片
            articles.append({
                "uid":    uid,
                "title":  title,
                "desc":   re.sub(r"<[^>]+>", "", desc)[:350],
                "source": src["name"],
                "weight": src["weight"],
                "tags":   src.get("tags", []),
                "pub":    pub,
                "link":   link,
                "image":  image,       # 文章封面/配图 URL
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
    # ── 半导体设备（最高优先级，你的核心领域）
    "asml":10, "euv":10, "high-na":10, "光刻机":10,
    "lam research":8, "applied materials":8, "kla":8, "tokyo electron":8,
    "etch":6, "deposition":6, "cvd":6, "pvd":6, "ald":6, "cmp":6,
    "metrology":6, "inspection":6, "process control":6,
    "wafer fab equipment":8, "wfe":8, "设备":5,
    # ── 晶圆制造/代工
    "tsmc":8, "台积电":8, "foundry":6, "wafer":6, "晶圆":6,
    "2nm":8, "3nm":7, "n2":7, "gaa":7, "finfet":5,
    "smic":7, "中芯":7, "samsung foundry":7, "intel foundry":6,
    "cowos":9, "soic":8, "emib":7, "chiplet":8, "3d-ic":8,
    "advanced packaging":8, "先进封装":8,
    # ── 存储芯片
    "hbm":10, "hbm4":10, "hbm3":9, "high bandwidth memory":9,
    "sk hynix":7, "skhynix":7, "micron":6, "samsung memory":6,
    "dram":6, "nand":5, "flash":4, "存储":5,
    # ── GPU/算力芯片
    "nvidia":8, "gpu":8, "blackwell":9, "rubin":9, "gb200":9,
    "h100":7, "h200":7, "b200":9, "amd":6, "intel":5,
    "算力芯片":8, "ai chip":8, "ai加速":7,
    # ── 半导体材料（你的专业背景）
    "sic":9, "silicon carbide":9, "碳化硅":9,
    "gan":8, "gallium nitride":8, "氮化镓":8,
    "compound semiconductor":7, "化合物半导体":7,
    "substrate":6, "衬底":6, "晶圆基板":7,
    "photoresist":7, "光刻胶":7, "etchant":6,
    "rare earth":7, "稀土":7, "critical mineral":7, "关键矿产":7,
    # ── 先进材料
    "solid-state battery":9, "固态电池":9,
    "perovskite":7, "钙钛矿":7,
    "graphene":6, "石墨烯":6,
    "carbon fiber":6, "碳纤维":6,
    "new materials":5, "新材料":5,
    # ── AI/大模型
    "llm":5, "large language model":5, "大模型":5,
    "deepseek":7, "qwen":6, "kimi":5,
    "gpt-5":8, "claude":5, "gemini":5,
    "reasoning":5, "inference":5, "推理":5,
    # ── AI基础设施
    "datacenter":5, "data center":5, "数据中心":5,
    "gigawatt":7, "液冷":6, "liquid cooling":6,
    "ai infrastructure":6, "算力基础设施":6,
    # ── 机器人/具身
    "humanoid":8, "人形机器人":8, "embodied":7, "具身智能":7,
    "harmonic reducer":8, "谐波减速器":8, "rv reducer":7,
    "torque sensor":7, "力矩传感器":7,
    "boston dynamics":6, "optimus":7,
    # ── 中国产业链
    "国产替代":8, "华为":7, "昇腾":8, "ascend":8,
    "中芯国际":7, "export control":8, "出口管制":8,
    "ban":6, "entity list":7,
    # ── 投资/市场
    "billion":4, "funding":4, "ipo":5, "m&a":5, "acquisition":5,
    "chips act":7, "补贴":5, "产业链":5,
}

# 热点加权：这些词出现在标题里额外加分（学自 nocmt 的timeliness评分）
HOTSPOT_TITLE_BONUS = {
    "euv": 4, "hbm4": 4, "asml": 3, "blackwell": 3, "rubin": 3,
    "固态电池": 3, "碳化硅": 3, "出口管制": 3, "人形机器人": 3,
    "2nm": 3, "gaa": 3, "高带宽内存": 3, "wfe": 3,
}

def _title_similar(t1: str, t2: str, threshold: float = 0.65) -> bool:
    """
    标题相似度检测（学自 nocmt/dailynews）
    解决"同一事件换不同标题"的重复问题，比uid更强
    """
    t1 = t1.lower().strip()
    t2 = t2.lower().strip()
    # 包含关系直接判重
    if t1 in t2 or t2 in t1:
        return True
    # 去掉空格/标点后的词集合重叠率
    import re
    w1 = set(re.sub(r"[\s,，。！？:：、\-—()（）]", "", t1))
    w2 = set(re.sub(r"[\s,，。！？:：、\-—()（）]", "", t2))
    if not w1 or not w2:
        return False
    overlap = len(w1 & w2) / min(len(w1), len(w2))
    return overlap > threshold


def score_article(a: dict) -> float:
    """
    多维评分（学自 nocmt/dailynews relevance_score + 热点权重）
    = 来源权重 + 正文关键词 + 标题×1.5 + 热点词bonus
    """
    text  = (a["title"] + " " + a["desc"]).lower()
    title = a["title"].lower()
    score = float(a["weight"])
    for kw, pts in DOMAIN_SCORES.items():
        if kw in text:
            score += pts
    for kw, pts in DOMAIN_SCORES.items():
        if kw in title:
            score += pts * 0.8
    for kw, bonus in HOTSPOT_TITLE_BONUS.items():
        if kw in title:
            score += bonus
    return round(score, 1)

# ──────────────────────────────────────────────────────
# Step 1b  Tavily 实时搜索（多Key自动轮换）
# ──────────────────────────────────────────────────────

# 搜索查询列表：以半导体全产业链为核心（32个，覆盖每一个环节）
# 每次早班/午班各随机选12个执行，保证全面覆盖
TAVILY_QUERIES = [
    # ═══ 1. 光刻 & 制程（产业链最上游、壁垒最高）═══
    "ASML EUV High-NA lithography semiconductor equipment order",
    "2nm GAA CFET transistor node TSMC Samsung Intel process",
    "DUV immersion lithography China domestic 28nm mature node",

    # ═══ 2. 半导体设备 WFE（全球千亿美元市场）═══
    "Applied Materials etching deposition CVD PVD semiconductor revenue",
    "Lam Research etch semiconductor equipment market share",
    "KLA metrology inspection process control semiconductor",
    "Tokyo Electron Screen Holdings semiconductor equipment Japan",
    "AMEC NAURA ACM Research China semiconductor equipment domestic",

    # ═══ 3. 晶圆代工 Foundry（产能 & 制程竞赛）═══
    "TSMC foundry revenue utilization rate capacity Arizona Japan",
    "Samsung foundry GAA yield rate advanced node order",
    "Intel foundry IFS 18A restructuring external customer",
    "SMIC China 7nm foundry capacity expansion revenue",
    "GlobalFoundries UMC mature node automotive IoT capacity",

    # ═══ 4. 存储芯片（HBM = AI时代最大增量）═══
    "HBM4 HBM3E SK Hynix Samsung Micron bandwidth AI GPU",
    "DRAM price DDR5 supply demand contract forecast",
    "NAND flash 3D QLC Kioxia Western Digital Samsung",
    "YMTC CXMT China memory DRAM NAND domestic production",

    # ═══ 5. 先进封装（算力瓶颈，台积电核心增长点）═══
    "CoWoS SoIC advanced packaging capacity TSMC AI chip",
    "chiplet UCIe 3D IC EMIB Foveros hybrid bonding Intel AMD",
    "OSAT ASE Amkor JCET backend packaging revenue",

    # ═══ 6. 半导体材料（你的专业方向）═══
    "silicon wafer SUMCO Shin-Etsu substrate price supply",
    "photoresist EUV CMP slurry etchant gas semiconductor materials",
    "SiC silicon carbide Wolfspeed Infineon power device wafer",
    "GaN gallium nitride power semiconductor RF 5G chip",

    # ═══ 7. EDA & IP（设计工具 + 架构授权）═══
    "Synopsys Cadence EDA semiconductor design AI chip revenue",
    "ARM RISC-V chip architecture IP licensing Qualcomm Apple",

    # ═══ 8. GPU / AI算力（半导体最大下游驱动力）═══
    "NVIDIA Blackwell Rubin GB200 B300 GPU revenue datacenter AI",
    "AMD MI350 Intel Gaudi Qualcomm AI accelerator chip compete",
    "Huawei Ascend 910C Cambricon Hygon China domestic AI chip GPU",

    # ═══ 9. 地缘政治 & 出口管制（影响整个产业格局）═══
    "semiconductor export control BIS entity list China restriction",
    "CHIPS Act subsidy Intel TSMC Samsung fab US policy billion",

    # ═══ 10. 半导体投资 & 市场数据 ═══
    "semiconductor revenue forecast market SEMI WSTS industry growth",
    "semiconductor acquisition merger funding capex WFE spending",

    # ═══ 11. 汽车 & 功率半导体 ═══
    "automotive chip ADAS autonomous driving SiC IGBT power",

    # ═══ 12. 具身智能（次要聚焦）═══
    "humanoid robot embodied AI Figure Optimus Tesla production",

    # ═══ 13. AI大模型（算力需求的直接驱动）═══
    "LLM DeepSeek Qwen open source AI training compute inference",
]

# 优先抓取的国际权威域名（半导体 + 顶级财经为主）
TAVILY_DOMAINS = [
    # 全球顶级财经
    "bloomberg.com", "reuters.com", "ft.com", "wsj.com",
    "nikkei.com", "economist.com", "caixinglobal.com",
    # 半导体专业媒体（最核心的8个）
    "semianalysis.com", "asianometry.com", "eetimes.com",
    "semiengineering.com", "digitimes.com", "thelec.net",
    "semiwiki.com", "anysilicon.com",
    # 工程 & IEEE
    "spectrum.ieee.org", "eetimes.eu", "eenewseurope.com",
    # 硬件 & 算力
    "tomshardware.com", "anandtech.com", "theregister.com",
    "hpcwire.com", "datacenterknowledge.com", "datacenterdynamics.com",
    # 科技综合
    "techcrunch.com", "technologyreview.com", "wired.com",
    "arstechnica.com", "venturebeat.com",
    # 中国科技英文
    "scmp.com",
    # 学术 & 材料
    "nature.com",
    # 行业协会
    "semi.org", "semiconductors.org",
]


def _get_tavily_client():
    """
    多Key轮换：逐个尝试 TAVILY_KEYS，遇到429/额度用完就切下一个。
    返回 (client, key_index) 或 (None, -1)
    """
    if not TAVILY_KEYS:
        return None, -1
    try:
        from tavily import TavilyClient
    except ImportError:
        print("  ⏭ tavily-python 未安装")
        return None, -1

    for i, key in enumerate(TAVILY_KEYS):
        try:
            c = TavilyClient(api_key=key)
            # 用一个轻量查询测试Key是否有效
            c.search(query="test", max_results=1, search_depth="basic")
            print(f"  🔑 Tavily Key #{i+1}/{len(TAVILY_KEYS)} 有效")
            return c, i
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "limit" in err or "quota" in err or "exceeded" in err:
                print(f"  ⚠️ Key #{i+1} 额度已用完，尝试下一个…")
                continue
            elif "401" in err or "invalid" in err or "unauthorized" in err:
                print(f"  ⚠️ Key #{i+1} 无效，跳过")
                continue
            else:
                # 其他错误也试试下一个
                print(f"  ⚠️ Key #{i+1} 错误: {str(e)[:50]}，尝试下一个…")
                continue

    print("  ❌ 所有 Tavily Key 均不可用")
    return None, -1


def collect_tavily(seen_uids: set, seen_titles: list) -> list[dict]:
    """
    用 Tavily Search API 实时搜索最新半导体/AI/算力/具身智能热点。
    - 多Key自动轮换（某个Key月度1000次额度用完→自动切下一个）
    - 只搜最近24小时的新闻（time_range="day"）
    - 优先国际权威媒体
    - 与RSS去重后合并
    """
    tavily_client, key_idx = _get_tavily_client()
    if tavily_client is None:
        print("  ⏭ Tavily 不可用，跳过实时搜索")
        return []

    articles = []
    total_new = 0
    api_errors = 0

    # 早班/午班使用不同查询子集，确保全天覆盖全产业链
    seed = int(hashlib.md5(f"{DATE_STR}-{SESSION}-tavily".encode()).hexdigest(), 16)
    rng  = random.Random(seed)
    queries = TAVILY_QUERIES[:]
    rng.shuffle(queries)
    # 每次执行12个查询（32个查询池，早晚班各12个，基本不重复）
    queries = queries[:12]

    print(f"\n🔍 Tavily 实时搜索（Key #{key_idx+1}，{len(queries)} 个查询）…")

    for i, query in enumerate(queries, 1):
        try:
            resp = tavily_client.search(
                query=query,
                topic="news",              # 新闻模式
                search_depth="advanced",   # 深度搜索
                max_results=5,
                time_range="day",          # ← 核心：只要24小时内
                include_images=True,
                include_domains=TAVILY_DOMAINS,
            )
            results = resp.get("results", [])
            batch_new = 0

            for r in results:
                title = (r.get("title") or "").strip()
                url   = (r.get("url") or "")
                if not title or len(title) < 10:
                    continue

                uid = hashlib.md5(title.lower().encode()).hexdigest()[:12]
                if uid in seen_uids:
                    continue
                if any(_title_similar(title, t) for t in seen_titles[-300:]):
                    continue

                # 从URL提取来源域名
                import urllib.parse
                domain = urllib.parse.urlparse(url).netloc.replace("www.", "")

                desc = (r.get("content") or "")[:350]
                # 尝试拿图片
                image = ""
                imgs = resp.get("images", [])
                if imgs and isinstance(imgs, list):
                    for img in imgs:
                        if isinstance(img, str) and img.startswith("http"):
                            image = img
                            break

                articles.append({
                    "uid":    uid,
                    "title":  title,
                    "desc":   desc,
                    "source": f"Tavily·{domain[:20]}",
                    "weight": 9,
                    "tags":   ["tavily", "realtime"],
                    "pub":    "",
                    "link":   url,
                    "image":  image,
                })
                seen_uids.add(uid)
                seen_titles.append(title)
                batch_new += 1

            total_new += batch_new
            if batch_new:
                print(f"  [{i}/{len(queries)}] \"{query[:35]}…\" → +{batch_new}")
            time.sleep(0.3)

        except Exception as e:
            err = str(e).lower()
            api_errors += 1
            if "429" in err or "limit" in err or "quota" in err:
                print(f"  ⚠️ Key #{key_idx+1} 额度用完（查询{i}），剩余查询跳过")
                break
            else:
                print(f"  ⚠️ 查询{i}失败: {str(e)[:50]}")
                if api_errors >= 3:
                    print("  ⚠️ 连续失败过多，停止Tavily搜索")
                    break
                time.sleep(1)

    print(f"✅ Tavily 搜索完成：+{total_new} 条实时新闻")
    return articles


# ──────────────────────────────────────────────────────
# Step 1+2 综合：RSS + Tavily → 评分 → 去重 → 分层候选池
# ──────────────────────────────────────────────────────
def collect_news(used_uids: set) -> list[dict]:
    print(f"\n📡 {SESSION} 抓取 {len(SESSION_SOURCES)}/{len(ALL_SOURCES)} 个源…")
    pool, seen_uids, seen_titles = [], set(), []

    for i, src_item in enumerate(SESSION_SOURCES, 1):
        arts = fetch_source(src_item)
        new  = []
        for a in arts:
            if a["uid"] in seen_uids:
                continue
            # 标题相似度去重（学自 nocmt/dailynews）
            is_dup = any(_title_similar(a["title"], t) for t in seen_titles[-200:])
            if is_dup:
                continue
            seen_uids.add(a["uid"])
            seen_titles.append(a["title"])
            new.append(a)
        pool.extend(new)
        src = src_item  # 保持命名一致
        if new:
            print(f"  [{i:2d}/{len(SESSION_SOURCES)}] {src['name']}: +{len(new)}")
        time.sleep(0.15)

    print(f"\n✅ RSS抓取完成：{len(pool)} 条")

    # Step 1b: Tavily 实时搜索补充（抓最新24h热点）
    tavily_arts = collect_tavily(seen_uids, seen_titles)
    if tavily_arts:
        pool.extend(tavily_arts)
        print(f"  📊 合并：RSS {len(pool)-len(tavily_arts)} + Tavily {len(tavily_arts)} = {len(pool)} 条")

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
               "lam","kla","applied materials","tokyo electron","micron","sk hynix",
               "cowos","chiplet","packaging","foundry","wafer","euv","dram","nand",
               "eda","sic","gan","ascend","smic","ymtc","cxmt","intel","samsung",
               "算力","芯片","半导体","封装","存储","制程","光刻","晶圆","昇腾",
               "中芯","设备","碳化硅","氮化镓","hpc","datacenter"]
    AI_KW   = ["llm","gpt","claude","gemini","deepseek","openai","anthropic",
               "large language","大模型","人工智能","ai agent","inference"]
    ROBOT_KW = ["robot","humanoid","embodied","optimus","figure","reducer",
                "人形机器人","具身智能","减速器","谐波","机器人"]
    MAT_KW  = ["materials","battery","solid-state","rare-earth","新材料",
               "稀土","固态电池","perovskite","钙钛矿","graphene","石墨烯"]
    CN_KW   = ["china","chinese","华为","中国","国产","a股","产业链","国产替代"]

    def tag(a):
        t = (a["title"] + " " + a["desc"]).lower()
        if any(k in t for k in SEMI_KW):   return "semi"   # 半导体优先级最高
        if any(k in t for k in ROBOT_KW):  return "robot"
        if any(k in t for k in MAT_KW):    return "mat"
        if any(k in t for k in CN_KW):     return "cn"
        if any(k in t for k in AI_KW):     return "ai"
        return "other"

    buckets = {"semi": [], "ai": [], "robot": [], "mat": [], "cn": [], "other": []}
    for a in sorted(pool, key=lambda x: x["score"], reverse=True):
        buckets[tag(a)].append(a)

    print(f"  分桶 → 半导体:{len(buckets['semi'])} AI:{len(buckets['ai'])} "
          f"机器人:{len(buckets['robot'])} 材料:{len(buckets['mat'])} "
          f"中国:{len(buckets['cn'])} 其他:{len(buckets['other'])}")

    # 构建候选池：半导体绝对优先，机器人严格限额（最多5条进池）
    candidate, seen2 = [], set()
    for cat, quota in [("semi",120), ("ai",15), ("cn",15),
                       ("mat",10), ("robot",5), ("other",5)]:
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

━━ 选题任务（半导体产业占80%，是绝对核心）━━

A. 深度长文（恰好{N_DEEP}条）— 半导体必须占8篇：
  1. 半导体设备/光刻/制程/晶圆代工         → 必须3篇（ASML/AMAT/Lam/KLA/TSMC/三星代工）
  2. HBM/先进封装/存储芯片                 → 必须2篇（HBM4/CoWoS/SK海力士/美光）
  3. GPU/算力芯片/AI加速器                 → 必须2篇（英伟达/AMD/华为昇腾/寒武纪）
  4. 中国半导体/国产替代/出口管制/材料     → 必须1篇（中芯/光刻胶/SiC/稀土）
  5. AI大模型/具身智能/投资（与芯片相关）  → 必须2篇
  核心原则：10篇中至少8篇必须直接与半导体产业链相关（设备/制程/封装/存储/算力芯片/材料/EDA）
  优先级：推特/X上讨论度最高的半导体热点话题优先选
  禁止：纯软件/SaaS/社交媒体/消费电子/非芯片话题占用名额

B. 精选快讯（恰好{N_BRIEF}条，不与A重复）— 半导体必须占8条：
  1. 半导体设备/晶圆代工/封装/制程  → 必须4条
  2. HBM/存储/GPU/算力芯片         → 必须2条
  3. 中国半导体/国产替代/材料       → 必须2条
  4. AI/投资/并购/政策             → 必须2条

仅输出 JSON，不要其他任何文字：
{{
  "deep":  [{{"idx":编号,"title":"原标题","source":"来源","domain":"领域标签","angle":"写作角度（机器人类必须含产业链上下游）"}}],
  "brief": [{{"idx":编号,"title":"原标题","source":"来源","domain":"领域标签"}}]
}}"""

    print("  🎯 选题中（Pro）…")
    raw = _chat([{"role": "user", "content": prompt}],
                max_tokens=3000, temperature=0.2,
                system="你是专注半导体全产业链的资深选题编辑。半导体设备/制程/封装/存储/算力芯片是绝对核心，10篇深度长文中必须有8篇直接与半导体产业链相关，只有2篇可以是相关的AI/具身智能/投资话题。优先选推特/X上讨论度最高的半导体热点。")

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

    # 验证半导体配额（目标80% = 8篇）
    SEMI_CHECK = ["semiconductor","chip","gpu","hbm","tsmc","nvidia","amd",
                  "asml","lam","kla","applied materials","tokyo electron",
                  "samsung","intel","micron","sk hynix","foundry","wafer",
                  "cowos","chiplet","packaging","euv","dram","nand","eda",
                  "sic","gan","ascend","cambricon","smic","ymtc","cxmt",
                  "算力","芯片","半导体","封装","制程","光刻","存储","晶圆",
                  "昇腾","中芯","设备","碳化硅","氮化镓"]
    # 机器人/具身智能词 —— 这类最多只保留1篇，其余强制替换为半导体
    ROBOT_CHECK = ["robot","humanoid","embodied","optimus","figure",
                   "机器人","具身","减速器","谐波","reducer","actuator"]
    def is_semi(a):
        t = (a.get("title","") + a.get("desc","") + a.get("domain","")).lower()
        return any(k in t for k in SEMI_CHECK)
    def is_robot(a):
        t = (a.get("title","") + a.get("desc","") + a.get("domain","")).lower()
        return any(k in t for k in ROBOT_CHECK) and not is_semi(a)

    # 步骤1：机器人文章最多保留1篇，多余的标记为待替换
    robot_arts = [a for a in deep if is_robot(a)]
    if len(robot_arts) > 1:
        for a in robot_arts[1:]:
            if a in deep:
                deep.remove(a)
        print(f"  🤖 机器人文章超额，移除 {len(robot_arts)-1} 篇（最多保留1篇）")

    # 步骤2：半导体不足8篇，从候选池补充
    semi_cnt = sum(1 for a in deep if is_semi(a))
    if semi_cnt < 8:
        used = {x["uid"] for x in deep}
        # 候选池：优先评分高的半导体文章
        pool_semi = [a for a in pool if is_semi(a) and a["uid"] not in used]
        # 待替换：非半导体文章（机器人优先替换，其次其他非核心）
        non_core  = sorted([a for a in deep if not is_semi(a)],
                           key=lambda x: (0 if is_robot(x) else 1))
        add = min(8 - semi_cnt, len(pool_semi))
        for i in range(add):
            if i < len(non_core):
                deep.remove(non_core[i])
            pool_semi[i]["domain"] = pool_semi[i].get("domain") or "半导体"
            pool_semi[i]["angle"]  = "从产业链和投资角度分析对全球及中国芯片产业的影响"
            deep.append(pool_semi[i])
        deep = deep[:N_DEEP]
        print(f"  ⚡ 半导体配额补充 +{add} 篇（目标8/10篇，当前候选池半导体{len(pool_semi)}篇）")

    semi_final = sum(1 for a in deep if is_semi(a))
    domains = [a.get("domain","?") for a in deep]
    print(f"✅ 选题完成 → 深度 {len(deep)} 篇（半导体 {semi_final} 篇）· 快讯 {len(brief)} 条")
    print(f"   领域：{' | '.join(domains)}")
    return deep, brief

# ──────────────────────────────────────────────────────
# Step 5  写作
# ──────────────────────────────────────────────────────
WRITER_SYSTEM = """你是中国顶级财经记者，具备产业研究员和价值投资人的双重视角。
文章风格参照《财经》杂志和《第一财经》最高水准：沉稳、真实、有判断力。

━━ 三重身份 ━━
① 产业研究员：每篇必须回答——这件事在整条产业链哪个位置？上中下游谁受益谁受损？
② 价值投资人：谁赚钱？谁会亏？哪家公司的竞争壁垒被改变？估值逻辑需要重新定价吗？
③ 财经记者：结论先行，数字精准，把复杂的技术/金融事件翻译给聪明但非行内人的读者。

━━ 专业名词解释规范（最核心铁律）━━
每个专业名词第一次出现，立即在括号内解释，格式：
  名词（通俗解释——为什么对投资者重要）

强制要求的示例（必须用这种格式，不能单独列术语表）：
  · EUV光刻机（极紫外光刻——制造7nm以下芯片的唯一工具，全球只有ASML会造，一台价值2亿美元）
  · HBM（高带宽内存——AI训练的"血管"，决定GPU吞吐速度，SK海力士和三星垄断90%以上供应）
  · CoWoS（台积电的晶圆级封装技术——把GPU和HBM"焊"在同一基板上，英伟达AI芯片的核心工艺）
  · 谐波减速器（机器人关节的核心精密零件——决定运动精度和寿命，日本Harmonic Drive长期垄断）
  · GaN（氮化镓——新一代功率半导体材料，充电效率比硅高30%，国内英诺赛科等在快速追赶）
  · SiC（碳化硅——耐高温高压的功率器件材料，电动车逆变器的核心，比亚迪、特斯拉都在大量用）
  · GAA（环绕栅极晶体管——替代FinFET的下一代芯片架构，2nm及以下节点的关键工艺）
  · WFE（晶圆制造设备——ASML/AMAT/LAM等公司卖给芯片厂的机器，AI驱动下全球市场规模超千亿美元）

━━ 文章铁律 ━━
① 每篇约500字（±80字），半导体/设备类可延伸至600字
② 开头第一句必须是有信息量的结论，禁止"近日""随着""据悉""日前"
③ 结尾必须有【今日启示】：具体可操作的产业或认知建议，≤2句
④ 文章结构：核心判断(1段) → 产业背景与链条(2段) → 竞争格局/赢家输家(1段) → 启示
⑤ 重点领域必须有中国视角：国产替代进度、A股产业链意义、地缘政治影响
⑥ 禁止感叹号、禁止"颠覆性""革命性""里程碑式"等空洞词

━━ 数据准确性铁律（最高优先级，违反等于失职）━━
⚠️ 以下规则优先级高于一切写作要求：
① 所有数字（金额/市值/市占率/产能/营收/增速/百分比）必须100%来自原文摘要
   → 原文说"营收增长15%"你才能写15%，不能凭记忆写成"约20%"
   → 原文说"投资50亿美元"你才能写50亿，不能四舍五入写成"近60亿"
② 如果原文没有提供具体数字，必须写"具体数据未披露"或改写为定性描述
   → 绝对禁止凭印象、凭常识、凭历史数据杜撰任何数字
③ 公司名称、产品型号、工艺节点必须与原文完全一致
   → 原文写"HBM3E"不能写成"HBM4"，原文写"3nm"不能写成"2nm"
④ 如果对任何事实不确定，宁可模糊表述也不能写一个可能错误的数字
⑤ 每篇文章末尾必须标注 **来源**：[来源名称]，方便读者溯源验证
⑥ 营收/利润等财务数据必须标明币种（美元/人民币/韩元）和时间周期（季度/年度）

━━ 机器人/具身智能专项 ━━
涉及机器人的文章必须分析产业链：
上游零部件（电机/谐波减速器/RV减速器/力矩传感器/视觉芯片）
→ 中游（本体制造/系统集成）
→ 下游（汽车制造/物流/半导体厂/服务业）
中国各环节的优劣势、国产化率、代表公司（不做股票推荐）"""

def write_batch(articles: list[dict], batch_num: int, total: int) -> str:
    items = []
    for i, a in enumerate(articles, 1):
        items.append(
            f"### 文章{i}（{a.get('domain','科技')}）\n"
            f"来源：{a['source']}\n"
            f"原文链接：{a.get('link','')}\n"
            f"标题：{a['title']}\n"
            f"摘要：{a['desc']}\n"
            f"写作角度：{a.get('angle','从产业链和投资角度深度分析')}"
        )
    prompt = (f"今天是{TODAY}（{SESSION}）。请按照写作要求，"
              f"为以下{len(articles)}篇文章逐一撰写深度分析：\n\n"
              + "\n\n".join(items)
              + f"\n\n---\n"
              f"⚠️ 数据准确性（最高优先级）：\n"
              f"1. 所有数字（营收/增速/产能/市占率/金额）必须100%来自上方每篇的'摘要'原文\n"
              f"2. 原文没有的数字→写'具体数据未披露'，绝对禁止凭记忆或常识杜撰\n"
              f"3. 公司名/产品型号/工艺节点→必须与原文完全一致，不能混淆\n"
              f"4. 财务数据必须标明币种和时间（如'2026Q1营收XX亿美元'）\n\n"
              f"输出格式：每篇以 ## 深度{(batch_num-1)*5+1 if len(articles)>1 else batch_num}：[标题] 开头，篇间用 \\n---\\n 分隔。"
              f"每篇末尾标注 **来源**：[来源名称]")
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
        items.append(
            f"[{i:02d}|评分{a.get('score',0):.0f}] "
            f"【{a['source']}】{a['title']} | {a['desc'][:120]}"
        )

    prompt = f"""今天是{TODAY}。以下是按热度评分排序的{len(briefs)}条精选新闻，逐条改写为快讯，必须全部输出。

{chr(10).join(items)}

━━ 输出格式（每条用 ===第N条=== 分隔）━━

===第1条===
领域：[半导体设备/晶圆制造/HBM/AI算力/大模型/材料/机器人/投资/政策/产业链 中选一]
标题：[≤15字，必须含核心事实或数字]
正文：[75-100字，必须包含：
  - 具体数字/金额/比例/百分比
  - 专业名词括号即时解释：名词（解释——为什么重要），禁止单独列术语表
  - 产业链影响（谁受益/谁受损）]
启示：[1句，点明对哪个产业链环节影响最大]

===第2条===
... 以此类推到第{len(briefs)}条，不可省略。"""

    print(f"  ⚡ 精选快讯 {len(briefs)} 条 → Pro…")
    return _chat([{"role": "user", "content": prompt
                   + "\n\n⚠️ 数据铁律：每条快讯里的数字（金额/百分比/产能/增速）"
                   "必须100%来自原文摘要。原文没有具体数字→改写为定性描述，"
                   "绝对禁止凭印象杜撰。宁可不写数字也不能写一个可能错的数字。"},
                 ],
                 max_tokens=5000, temperature=0.5,
                 system=(
                     "你是顶级财经编辑，为高净值投资人写精选科技快讯。"
                     "铁律：所有数字必须严格来自原文摘要，不得编造或推测。"
                     "如果原文无具体数字，用定性描述替代。"
                     "专业名词首次出现必须括号解释：名词（解释——为什么重要）。"
                     f"必须输出全部{len(briefs)}条，使用===第N条===分隔。"
                 ))

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
# Step 6b  生成推特文案（中英双语）
# ──────────────────────────────────────────────────────
def make_twitter_posts(deep_list: list, brief_list: list) -> dict:
    """
    生成每日推特文案：
    - main_cn  中文主推（含图片提示）
    - main_en  英文主推
    - thread   Thread长推（5条）
    保存到 reports/twitter_YYYY-MM-DD_SESSION.txt
    """
    arts = "\n".join(
        f"{i}. 【{a.get('domain','科技')}】{a['title'][:45]}"
        for i, a in enumerate(deep_list[:10], 1)
    )
    briefs = "\n".join(
        f"{i}. {a['title'][:40]}"
        for i, a in enumerate(brief_list[:5], 1)
    )
    # 今日评分最高文章的图片作为推特配图提示
    top_img = next((a.get("image","") for a in deep_list if a.get("image")), "")

    prompt = f"""今天是{TODAY}（{SESSION}）。以下是今日科技投资简报的核心内容：

深度文章：
{arts}

今日快讯（前5条）：
{briefs}

━━ 任务：生成推特(X)发帖文案 ━━
请输出3部分内容，每部分之间用 ---SPLIT--- 分隔：

【第1部分】中文主推（200字以内，适合X平台）
格式：
- 开头：今日科技产业信号 📡 {TODAY}
- 2-3个核心判断，用 🔹 开头，每个一行
- 要有具体数字或事件
- 产业链视角：谁受益/谁承压
- 结尾：#AI #半导体 #产业链 @wangsir1w
- 不用感叹号，克制精准

---SPLIT---

【第2部分】英文主推（240字以内）
同样内容英文版，面向全球读者：
- 开头：Today's key signals from the chip & AI supply chain 📡
- 核心判断（英文）
- 结尾：#Semiconductor #AIChip #ChinaTech @wangsir1w

---SPLIT---

【第3部分】Thread长推（5条，每条用 [N/5] 标注）
[1/5] 半导体/算力最重要动态
[2/5] 第二重要消息
[3/5] 材料/机器人方向
[4/5] 中国产业链视角（国产替代/A股）
[5/5] 总结+引导关注：更多产业链深度分析 @wangsir1w 微信13973780026

要求：每条都有具体数字，禁止感叹号，每条≤240字"""

    print("  🐦 生成推特文案 → Pro…")
    raw = _chat([{"role": "user", "content": prompt}],
                max_tokens=2000, temperature=0.6,
                system=(
                    "你是中英双语科技投资账号运营者，"
                    "把复杂产业链信息浓缩成高传播力推文。"
                    "风格：观点明确、数字精准、克制不夸张。"
                ))

    parts = [p.strip() for p in (raw or "").split("---SPLIT---")]
    result = {
        "main_cn": parts[0] if len(parts) > 0 else "",
        "main_en": parts[1] if len(parts) > 1 else "",
        "thread":  parts[2] if len(parts) > 2 else "",
        "top_img": top_img,   # 推荐配图URL
    }

    # 保存到文件
    os.makedirs("reports", exist_ok=True)
    twitter_path = f"reports/twitter_{DATE_STR}_{SESSION}.txt"
    with open(twitter_path, "w", encoding="utf-8") as f:
        f.write(f"配图建议: {top_img}\n\n")
        f.write(f"=== 主推（中文）===\n{result['main_cn']}\n\n")
        f.write(f"=== 主推（英文）===\n{result['main_en']}\n\n")
        f.write(f"=== Thread长推 ===\n{result['thread']}\n")
    print(f"✅ 推特文案已保存：{twitter_path}")
    return result


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
    print(f"  Tavily：{'✅ ' + str(len(TAVILY_KEYS)) + '个Key' if TAVILY_KEYS else '❌ 未配置'}")
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

    # Step 6b: 推特文案（中英双语，含配图建议）
    twitter = make_twitter_posts(deep_list, brief_list)
    if twitter["main_cn"]:
        print("\n" + "─"*55)
        print("🐦 今日推特中文主推：")
        print("─"*55)
        print(twitter["main_cn"])
        print("─"*55)
        if twitter["top_img"]:
            print(f"📷 推荐配图：{twitter['top_img'][:80]}")
        print("─"*55)

    # Step 7: 保存
    _, new_uids = save(header, deep_text, brief_text,
                       len(pool), deep_list, brief_list)
    save_history(history, new_uids)
    update_readme(header, deep_text)

    # 生成 GitHub Pages 静态网页
    page_url = ""
    try:
        from page_generator import publish_page
        page_url = publish_page(header, deep_text, brief_text,
                                deep_list=deep_list)
        print(f"🌐 网页已生成：{page_url}")
    except Exception as e:
        print(f"  ⚠️ 页面生成失败（不影响推送）: {e}")

    # 推送（传入deep_list用于文章配图，传入page_url用于网页链接）
    from push import push_all
    push_all(header, deep_text, brief_text, DATE_STR,
             deep_list=deep_list, page_url=page_url)

    print("\n" + "─"*60)
    print(f"📋 {SESSION} 导读：")
    print("─"*60)
    print(header[:400])
    print("─"*60)
    print(f"\n🎉 {SESSION}完成！{N_DEEP}篇深度 + {N_BRIEF}条精选快讯 已推送")
