"""
sources.py — 100个精选高质量新闻源
分6层，每层按信号质量排序
Google News专题搜索：覆盖付费墙媒体 + 专题聚合
"""

# ══════════════════════════════════════════════════════
# Tier 1 · 顶级财经媒体（14个）
# 策略：Google News代理绕付费墙 + 直连RSS双保险
# ══════════════════════════════════════════════════════
TIER1_FINANCIAL_MEDIA = [
    {"name": "Bloomberg 彭博社",          "weight": 10, "tags": ["macro","finance","investment"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com+AI+OR+semiconductor+OR+chip+OR+investment&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Reuters 路透社",            "weight": 10, "tags": ["macro","geopolitics","finance"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com+AI+OR+tech+OR+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Wall Street Journal WSJ",   "weight": 9,  "tags": ["finance","tech","investment"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:wsj.com+AI+OR+chip+OR+funding&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Financial Times 金融时报",  "weight": 9,  "tags": ["macro","finance","analysis"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:ft.com+AI+finance+economy&ceid=US:en&hl=en-US&gl=US"},
    {"name": "The Economist 经济学人",    "weight": 9,  "tags": ["macro","analysis","deep-dive"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:economist.com&ceid=US:en&hl=en-US&gl=US"},
    {"name": "New York Times Tech",       "weight": 8,  "tags": ["tech","AI","policy"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:nytimes.com+AI+OR+tech+OR+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Bloomberg Tech RSS",        "weight": 9,  "tags": ["tech","AI","finance"],
     "url": "https://feeds.bloomberg.com/technology/news.rss"},
    {"name": "Yahoo Finance",             "weight": 7,  "tags": ["stocks","finance","earnings"],
     "url": "https://finance.yahoo.com/news/rssindex"},
    {"name": "MarketWatch",               "weight": 7,  "tags": ["stocks","macro","finance"],
     "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
    {"name": "Barron's",                  "weight": 7,  "tags": ["investment","stocks","analysis"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:barrons.com+AI+OR+tech&ceid=US:en"},
    {"name": "Forbes Tech & AI",          "weight": 7,  "tags": ["tech","AI","business"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:forbes.com+AI+chip+investment&ceid=US:en"},
    {"name": "Business Insider Tech",     "weight": 7,  "tags": ["tech","AI","startups"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:businessinsider.com+AI+chip&ceid=US:en"},
    {"name": "The Diff (Byrne Hobart)",   "weight": 9,  "tags": ["macro","finance","deep-dive"],
     "url": "https://www.thediff.co/feed/"},
    {"name": "Ben Evans Newsletter",      "weight": 9,  "tags": ["tech","strategy","VC"],
     "url": "https://www.ben-evans.com/benedictevans/rss.xml"},
]

# ══════════════════════════════════════════════════════
# Tier 2 · AI / 大模型 专属（28个）
# 覆盖：大厂官博 + 顶级研究机构 + 独立分析师
# ══════════════════════════════════════════════════════
TIER2_AI_SOURCES = [
    # 大厂官方（行业风向标）
    {"name": "OpenAI 官方博客",           "weight": 10, "tags": ["AI","LLM","GPT"],
     "url": "https://openai.com/news/rss.xml"},
    {"name": "Anthropic 官方新闻",        "weight": 10, "tags": ["AI","Claude","safety"],
     "url": "https://www.anthropic.com/news/rss"},
    {"name": "Google DeepMind",           "weight": 9,  "tags": ["AI","research","AGI"],
     "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Google AI Blog",            "weight": 9,  "tags": ["AI","research","Google"],
     "url": "https://blog.google/technology/ai/rss/"},
    {"name": "Meta AI Blog",              "weight": 9,  "tags": ["AI","LLM","open-source"],
     "url": "https://ai.meta.com/blog/rss/"},
    {"name": "Microsoft AI Blog",         "weight": 8,  "tags": ["AI","Copilot","Azure"],
     "url": "https://blogs.microsoft.com/ai/feed/"},
    {"name": "NVIDIA 开发者博客",         "weight": 9,  "tags": ["GPU","AI","compute"],
     "url": "https://blogs.nvidia.com/feed/"},
    {"name": "AWS AI Blog",               "weight": 8,  "tags": ["cloud","AI","AWS"],
     "url": "https://aws.amazon.com/blogs/aws/feed/"},
    {"name": "Together AI Blog",          "weight": 8,  "tags": ["AI","inference","open-source"],
     "url": "https://www.together.ai/blog/rss.xml"},
    {"name": "Hugging Face 博客",         "weight": 9,  "tags": ["AI","open-source","models"],
     "url": "https://huggingface.co/blog/feed.xml"},
    # 学术与研究机构
    {"name": "arXiv cs.AI 学术论文",      "weight": 8,  "tags": ["AI","papers","research"],
     "url": "https://rss.arxiv.org/rss/cs.AI"},
    {"name": "arXiv cs.LG 机器学习",      "weight": 8,  "tags": ["ML","papers","research"],
     "url": "https://rss.arxiv.org/rss/cs.LG"},
    {"name": "MIT Technology Review AI",  "weight": 9,  "tags": ["AI","analysis","society"],
     "url": "https://www.technologyreview.com/feed/"},
    {"name": "MIT News AI",               "weight": 8,  "tags": ["AI","academic","research"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:mit.edu+AI+research&ceid=US:en"},
    {"name": "Stanford HAI",              "weight": 8,  "tags": ["AI","policy","research"],
     "url": "https://news.google.com/rss/search?q=when:24h+Stanford+AI+research+HAI&ceid=US:en"},
    {"name": "BAIR Blog 伯克利AI",        "weight": 8,  "tags": ["AI","robotics","research"],
     "url": "https://bair.berkeley.edu/blog/feed.xml"},
    {"name": "Papers With Code",          "weight": 8,  "tags": ["AI","papers","code"],
     "url": "https://paperswithcode.com/rss"},
    {"name": "Epoch AI 算力趋势",         "weight": 9,  "tags": ["AI","compute","scaling"],
     "url": "https://epochai.org/feed.xml"},
    # 顶级独立分析师
    {"name": "Stratechery (Ben Thompson)","weight": 10, "tags": ["tech","strategy","analysis"],
     "url": "https://stratechery.com/feed/"},
    {"name": "Import AI (Jack Clark)",    "weight": 9,  "tags": ["AI","policy","expert"],
     "url": "https://importai.substack.com/feed"},
    {"name": "Ahead of AI (Raschka)",     "weight": 9,  "tags": ["AI","LLM","practitioner"],
     "url": "https://magazine.sebastianraschka.com/feed"},
    {"name": "Simon Willison's Weblog",   "weight": 8,  "tags": ["AI","LLM","tools"],
     "url": "https://simonwillison.net/atom/everything/"},
    {"name": "Interconnects (N. Lambert)","weight": 9,  "tags": ["AI","LLM","RLHF"],
     "url": "https://www.interconnects.ai/feed"},
    {"name": "Ethan Mollick One Useful Thing","weight": 9,"tags": ["AI","society","practical"],
     "url": "https://www.oneusefulthing.org/feed"},
    {"name": "The Decoder",               "weight": 8,  "tags": ["AI","news","analysis"],
     "url": "https://the-decoder.com/feed/"},
    {"name": "Exponential View",          "weight": 8,  "tags": ["AI","tech","future"],
     "url": "https://www.exponentialview.co/feed"},
    # 行业媒体
    {"name": "VentureBeat AI",            "weight": 8,  "tags": ["AI","industry","products"],
     "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "The Gradient",              "weight": 8,  "tags": ["AI","deep-dive","research"],
     "url": "https://thegradient.pub/rss/"},
]

# ══════════════════════════════════════════════════════
# Tier 3 · 半导体 / 芯片 / 算力（12个）
# ══════════════════════════════════════════════════════
TIER3_SEMICONDUCTOR = [
    {"name": "SemiAnalysis 深度分析",     "weight": 10, "tags": ["semiconductor","AI","supply-chain"],
     "url": "https://semianalysis.com/feed/"},
    {"name": "IEEE Spectrum",             "weight": 10,  "tags": ["semiconductor","engineering"],
     "url": "https://spectrum.ieee.org/feeds/feed.rss"},
    {"name": "EE Times",                  "weight": 10,  "tags": ["semiconductor","chips","design"],
     "url": "https://www.eetimes.com/feed/"},
    {"name": "Semiconductor Engineering", "weight": 10,  "tags": ["semiconductor","EDA","process"],
     "url": "https://semiengineering.com/feed/"},
    {"name": "Fierce Electronics",        "weight": 9,  "tags": ["electronics","semiconductor"],
     "url": "https://www.fierceelectronics.com/rss/xml"},
    {"name": "The Register 硬件",         "weight": 7,  "tags": ["hardware","chips","tech"],
     "url": "https://www.theregister.com/headlines.atom"},
    {"name": "Tom's Hardware",            "weight": 7,  "tags": ["GPU","CPU","hardware"],
     "url": "https://www.tomshardware.com/feeds/all"},
    {"name": "GNews: NVIDIA GPU AI",      "weight": 10, "tags": ["GPU","NVIDIA","compute"],
     "url": "https://news.google.com/rss/search?q=when:24h+NVIDIA+GPU+AI+chip+H100+B200&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: TSMC Intel AMD",     "weight": 10,  "tags": ["fab","semiconductor","supply-chain"],
     "url": "https://news.google.com/rss/search?q=when:24h+TSMC+OR+Intel+OR+AMD+semiconductor+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 中国半导体芯片",     "weight": 10,  "tags": ["China","semiconductor","geopolitics"],
     "url": "https://news.google.com/rss/search?q=when:24h+China+semiconductor+chip+ban+export+control&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 数据中心算力",       "weight": 10,  "tags": ["datacenter","compute","AI-infra"],
     "url": "https://news.google.com/rss/search?q=when:24h+data+center+AI+power+compute+infrastructure+billion&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 量子计算",           "weight": 7,  "tags": ["quantum","computing","future"],
     "url": "https://news.google.com/rss/search?q=when:24h+quantum+computing+AI+breakthrough&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: HBM存储芯片",       "weight": 10, "tags": ["HBM","memory","Samsung","SKhynix"],
     "url": "https://news.google.com/rss/search?q=when:24h+HBM+OR+高带宽内存+OR+SK海力士+OR+三星存储&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 先进封装CoWoS",      "weight": 10, "tags": ["packaging","CoWoS","chiplet","advanced"],
     "url": "https://news.google.com/rss/search?q=when:24h+CoWoS+OR+先进封装+OR+chiplet+OR+台积电封装&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 国产芯片算力替代",    "weight": 10, "tags": ["China","chip","domestic","替代"],
     "url": "https://news.google.com/rss/search?q=when:24h+华为昇腾+OR+寒武纪+OR+海光+OR+燧原+OR+国产GPU+OR+算力替代&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 材料新能源",          "weight": 9,  "tags": ["material","battery","energy","新材料"],
     "url": "https://news.google.com/rss/search?q=when:24h+新材料+OR+碳纤维+OR+锂电池+OR+固态电池+OR+稀土+OR+材料创新&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
]

# ══════════════════════════════════════════════════════
# Tier 4 · 投资 / VC / 一级市场（14个）
# ══════════════════════════════════════════════════════
TIER4_INVESTMENT = [
    {"name": "TechCrunch 融资新闻",       "weight": 9,  "tags": ["VC","funding","startups"],
     "url": "https://techcrunch.com/category/venture/feed/"},
    {"name": "TechCrunch AI",             "weight": 8,  "tags": ["AI","startups","products"],
     "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "Crunchbase News",           "weight": 9,  "tags": ["VC","M&A","funding"],
     "url": "https://news.crunchbase.com/feed/"},
    {"name": "CB Insights 研究",          "weight": 9,  "tags": ["VC","market-research","AI"],
     "url": "https://www.cbinsights.com/research/feed/"},
    {"name": "a16z Blog 顶级VC",          "weight": 10, "tags": ["VC","AI","investment-thesis"],
     "url": "https://a16z.com/feed/"},
    {"name": "Sequoia Capital",           "weight": 9,  "tags": ["VC","portfolio","AI"],
     "url": "https://www.sequoiacap.com/news/feed/"},
    {"name": "Axios Pro Rata",            "weight": 8,  "tags": ["VC","deals","PE"],
     "url": "https://www.axios.com/feeds/feed.rss"},
    {"name": "Hacker News Top",           "weight": 8,  "tags": ["tech","AI","startups"],
     "url": "https://news.ycombinator.com/rss"},
    {"name": "The Information (GNews)",   "weight": 9,  "tags": ["tech","insider","AI"],
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:theinformation.com&ceid=US:en"},
    {"name": "GNews: AI融资独角兽",       "weight": 9,  "tags": ["VC","AI","unicorn"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+startup+funding+series+valuation+billion&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI IPO上市",         "weight": 8,  "tags": ["IPO","AI","public-market"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+company+IPO+listing+valuation&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 科技并购M&A",        "weight": 8,  "tags": ["M&A","acquisition","tech"],
     "url": "https://news.google.com/rss/search?q=when:24h+tech+AI+acquisition+merger+billion&ceid=US:en&hl=en-US&gl=US"},
    {"name": "AI Business",               "weight": 7,  "tags": ["AI","enterprise","business"],
     "url": "https://aibusiness.com/rss.xml"},
    {"name": "Robotics & Automation News","weight": 7,  "tags": ["robotics","AI","automation"],
     "url": "https://roboticsandautomationnews.com/feed/"},
]

# ══════════════════════════════════════════════════════
# Tier 5 · 中文优质媒体（14个）
# ══════════════════════════════════════════════════════
TIER5_CHINESE_MEDIA = [
    {"name": "机器之心",                  "weight": 9,  "tags": ["AI","LLM","research-news"],
     "url": "https://www.jiqizhixin.com/rss"},
    {"name": "量子位",                    "weight": 8,  "tags": ["AI","LLM","industry"],
     "url": "https://www.qbitai.com/feed"},
    {"name": "36氪",                      "weight": 8,  "tags": ["AI","investment","startups"],
     "url": "https://36kr.com/feed"},
    {"name": "虎嗅网",                    "weight": 8,  "tags": ["tech","business","analysis"],
     "url": "https://www.huxiu.com/rss/0.xml"},
    {"name": "钛媒体",                    "weight": 7,  "tags": ["AI","tech","investment"],
     "url": "https://www.tmtpost.com/rss"},
    {"name": "雷锋网 AI",                 "weight": 7,  "tags": ["AI","robots","chips"],
     "url": "https://www.leiphone.com/feed"},
    {"name": "华尔街见闻",               "weight": 8,  "tags": ["finance","macro","investment"],
     "url": "https://wallstreetcn.com/rss"},
    {"name": "Pandaily 中国科技英文",     "weight": 7,  "tags": ["China-tech","AI","startups"],
     "url": "https://pandaily.com/feed/"},
    {"name": "Technode 中国科技",         "weight": 7,  "tags": ["China-tech","AI","policy"],
     "url": "https://technode.com/feed/"},
    {"name": "South China Morning Post Tech","weight": 7,"tags": ["China","tech","policy"],
     "url": "https://www.scmp.com/rss/5/feed"},
    {"name": "GNews: 中国AI大模型",       "weight": 9,  "tags": ["China","AI","LLM"],
     "url": "https://news.google.com/rss/search?q=when:24h+China+AI+large+language+model+DeepSeek+Qwen&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 中美科技竞争",       "weight": 8,  "tags": ["US-China","tech","geopolitics"],
     "url": "https://news.google.com/rss/search?q=when:24h+US+China+tech+competition+AI+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 国产大模型",         "weight": 8,  "tags": ["China","AI","LLM"],
     "url": "https://news.google.com/rss/search?q=when:24h+DeepSeek+OR+Qwen+OR+Kimi+OR+Doubao+AI+model&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 中国智能体",         "weight": 7,  "tags": ["China","AI-agent","robotics"],
     "url": "https://news.google.com/rss/search?q=when:24h+China+AI+robot+autonomous+agent&ceid=US:en&hl=en-US&gl=US"},
]

# ══════════════════════════════════════════════════════
# Tier 6 · 前沿专题 Google News（18个）
# 覆盖：AI应用垂直 + 政策监管 + 前沿议题
# ══════════════════════════════════════════════════════
TIER6_FRONTIER_TOPICS = [
    {"name": "GNews: 开源大模型",         "weight": 9,  "tags": ["open-source","LLM","release"],
     "url": "https://news.google.com/rss/search?q=when:24h+open+source+LLM+model+release+weights&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI智能体Agent",      "weight": 9,  "tags": ["AI-agent","autonomous","agentic"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+agent+autonomous+agentic+workflow&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI机器人具身",       "weight": 8,  "tags": ["robotics","embodied","AI"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+robot+humanoid+embodied+intelligence&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI监管政策",         "weight": 8,  "tags": ["AI","regulation","policy"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+regulation+policy+government+law&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI医疗健康",         "weight": 8,  "tags": ["AI","healthcare","biotech"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+healthcare+medical+drug+discovery+biotech&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI安全对齐",         "weight": 8,  "tags": ["AI-safety","alignment","risk"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+safety+alignment+risk+AGI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 微软AI产品",         "weight": 8,  "tags": ["Microsoft","Copilot","AI"],
     "url": "https://news.google.com/rss/search?q=when:24h+Microsoft+Copilot+AI+Azure+OpenAI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: Google AI产品",      "weight": 8,  "tags": ["Google","Gemini","AI"],
     "url": "https://news.google.com/rss/search?q=when:24h+Google+Gemini+AI+Search+DeepMind&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: xAI Grok马斯克",    "weight": 7,  "tags": ["xAI","Grok","Tesla"],
     "url": "https://news.google.com/rss/search?q=when:24h+xAI+Grok+Elon+Musk+Tesla+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI编程开发工具",     "weight": 8,  "tags": ["AI-coding","developer","tools"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+coding+developer+tools+Cursor+GitHub+Copilot&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI能源电力",         "weight": 7,  "tags": ["AI","energy","power"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+energy+electricity+power+nuclear+data+center&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 多模态视觉模型",     "weight": 8,  "tags": ["multimodal","vision","AI"],
     "url": "https://news.google.com/rss/search?q=when:24h+multimodal+vision+language+model+image+video+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "LessWrong AI安全思考",      "weight": 7,  "tags": ["AI-safety","AGI","alignment"],
     "url": "https://www.lesswrong.com/feed.xml"},
    {"name": "Papers With Code",          "weight": 8,  "tags": ["AI","papers","SOTA"],
     "url": "https://paperswithcode.com/rss"},
    {"name": "Wired AI",                  "weight": 7,  "tags": ["AI","society","deep-dive"],
     "url": "https://www.wired.com/feed/tag/ai/latest/rss"},
    {"name": "Ars Technica Technology",   "weight": 7,  "tags": ["tech","AI","analysis"],
     "url": "https://feeds.arstechnica.com/arstechnica/technology-lab"},
    {"name": "The Verge AI",              "weight": 7,  "tags": ["AI","consumer","products"],
     "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"},
    {"name": "MarkTechPost",              "weight": 7,  "tags": ["AI","research","papers-summary"],
     "url": "https://www.marktechpost.com/feed/"},
]

# ══════════════════════════════════════════════════════
# 汇总 + 工具
# ══════════════════════════════════════════════════════
ALL_SOURCES = (
    TIER1_FINANCIAL_MEDIA
    + TIER2_AI_SOURCES
    + TIER3_SEMICONDUCTOR
    + TIER4_INVESTMENT
    + TIER5_CHINESE_MEDIA
    + TIER6_FRONTIER_TOPICS
)

KEYWORDS_EN = [
    "AI", "artificial intelligence", "LLM", "large language model",
    "GPU", "semiconductor", "chip", "NVIDIA", "TSMC", "Intel", "AMD",
    "investment", "venture capital", "VC", "funding", "IPO", "valuation",
    "compute", "datacenter", "inference", "training", "fine-tuning",
    "agent", "autonomous", "agentic", "reasoning", "multimodal",
    "OpenAI", "Anthropic", "DeepSeek", "Gemini", "Claude", "GPT",
    "transformer", "foundation model", "open source", "open-source",
    "startup", "unicorn", "acquisition", "M&A", "series",
    "robotics", "automation", "AGI", "alignment", "safety",
    "model", "benchmark", "parameter", "token", "context window",
    "Hugging Face", "xAI", "Grok", "Cursor", "Copilot",
]

KEYWORDS_CN = [
    "人工智能", "大模型", "半导体", "芯片", "算力", "投资",
    "融资", "IPO", "估值", "智能体", "数据中心", "推理",
    "训练", "开源", "大厂", "创业", "并购", "机器人",
    "GPU", "英伟达", "英特尔", "台积电", "多模态",
    "DeepSeek", "通义", "Kimi", "豆包", "文心",
]

KEYWORDS = KEYWORDS_EN + KEYWORDS_CN

if __name__ == "__main__":
    tiers = [
        ("Tier1 顶级财经",   TIER1_FINANCIAL_MEDIA),
        ("Tier2 AI专属",     TIER2_AI_SOURCES),
        ("Tier3 半导体算力", TIER3_SEMICONDUCTOR),
        ("Tier4 投资创业",   TIER4_INVESTMENT),
        ("Tier5 中文媒体",   TIER5_CHINESE_MEDIA),
        ("Tier6 前沿专题",   TIER6_FRONTIER_TOPICS),
    ]
    total = 0
    for name, lst in tiers:
        print(f"  {name}: {len(lst)} 个")
        total += len(lst)
    print(f"  {'─'*25}")
    print(f"  总计: {total} 个")