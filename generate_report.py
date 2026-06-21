"""
sources.py  v2  —  精选新闻源库
聚焦：半导体 · 设备 · 晶圆 · 材料 · 算力 · AI · 机器人
共 150 个源，7层分级，权重 7-10
参考：FeedSpot Top50半导体源 + Substack最佳科技通讯 + 行业权威媒体
"""

# ══════════════════════════════════════════════════════
# Tier 1 · 顶级财经 + 科技媒体（12个）权重 9-10
# ══════════════════════════════════════════════════════
TIER1 = [
    {"name": "Bloomberg Tech",
     "weight": 10, "tags": ["macro","finance","AI","semiconductor"],
     "url": "https://feeds.bloomberg.com/technology/news.rss"},
    {"name": "Reuters Technology",
     "weight": 10, "tags": ["macro","geopolitics","semiconductor","AI"],
     "url": "https://feeds.reuters.com/reuters/technologyNews"},
    {"name": "Financial Times Tech",
     "weight": 10, "tags": ["finance","tech","semiconductor"],
     "url": "https://www.ft.com/technology?format=rss"},
    {"name": "Wall Street Journal Tech",
     "weight": 9, "tags": ["finance","tech","semiconductor"],
     "url": "https://feeds.a.dj.com/rss/RSSWSJD.xml"},
    {"name": "Stratechery (Ben Thompson)",
     "weight": 10, "tags": ["tech","strategy","AI","semiconductor"],
     "url": "https://stratechery.com/feed/"},
    {"name": "MIT Technology Review",
     "weight": 9, "tags": ["AI","materials","semiconductor","deep-dive"],
     "url": "https://www.technologyreview.com/feed/"},
    {"name": "The Economist Tech",
     "weight": 9, "tags": ["macro","analysis","AI","semiconductor"],
     "url": "https://www.economist.com/science-and-technology/rss.xml"},
    {"name": "Nikkei Asia Tech",
     "weight": 9, "tags": ["Japan","semiconductor","Toyota","Sony","supply-chain"],
     "url": "https://asia.nikkei.com/rss/feed/section/tech-science"},
    {"name": "South China Morning Post Tech",
     "weight": 9, "tags": ["China","tech","semiconductor","policy"],
     "url": "https://www.scmp.com/rss/5/feed"},
    {"name": "Axios Tech",
     "weight": 9, "tags": ["tech","AI","policy","semiconductor"],
     "url": "https://www.axios.com/feeds/feed.rss"},
    {"name": "The Information (GNews)",
     "weight": 9, "tags": ["AI","semiconductor","insider","analysis"],
     "url": "https://news.google.com/rss/search?q=when:48h+site:theinformation.com+AI+chip+semiconductor&ceid=US:en"},
    {"name": "Wired Tech",
     "weight": 8, "tags": ["AI","tech","chip"],
     "url": "https://www.wired.com/feed/rss"},
]

# ══════════════════════════════════════════════════════
# Tier 2A · 半导体行业专业媒体（18个）权重 9-10
# 核心：行业分析 + 供应链 + 技术深度
# ══════════════════════════════════════════════════════
TIER2A_SEMI_MEDIA = [
    # 顶级分析机构
    {"name": "SemiAnalysis (Dylan Patel)",
     "weight": 10, "tags": ["semiconductor","AI","HBM","supply-chain","compute"],
     "url": "https://semianalysis.substack.com/feed"},
    {"name": "Fabricated Knowledge (Doug O'Laughlin)",
     "weight": 10, "tags": ["semiconductor","investment","foundry","memory"],
     "url": "https://www.fabricatedknowledge.com/feed"},
    {"name": "Asianometry",
     "weight": 10, "tags": ["semiconductor","history","China","TSMC","supply-chain"],
     "url": "https://newsletter.asianometry.com/feed"},
    {"name": "Semiconductor Engineering",
     "weight": 10, "tags": ["semiconductor","EDA","process","packaging","equipment"],
     "url": "https://semiengineering.com/feed/"},
    # 行业权威媒体
    {"name": "IEEE Spectrum 半导体",
     "weight": 10, "tags": ["semiconductor","research","engineering"],
     "url": "https://spectrum.ieee.org/feeds/topic/semiconductors.rss"},
    {"name": "EE Times 半导体",
     "weight": 10, "tags": ["semiconductor","chip","design","EDA"],
     "url": "https://www.eetimes.com/tag/semiconductors/feed/"},
    {"name": "EEJournal 半导体",
     "weight": 9, "tags": ["semiconductor","engineering","chip-design"],
     "url": "https://www.eejournal.com/category/semiconductor/feed/"},
    {"name": "DIGITIMES 半导体",
     "weight": 10, "tags": ["Taiwan","TSMC","semiconductor","supply-chain","Asia"],
     "url": "https://www.digitimes.com/rss/daily.xml"},
    {"name": "THE ELEC 韩国芯片",
     "weight": 10, "tags": ["Korea","Samsung","SKHynix","semiconductor","HBM"],
     "url": "https://thelec.net/rss/S1N3.xml"},
    {"name": "SemiWiki",
     "weight": 9, "tags": ["semiconductor","EDA","IP","design","process"],
     "url": "https://semiwiki.com/feed/"},
    {"name": "AnySilicon",
     "weight": 9, "tags": ["semiconductor","ASIC","IP","foundry","service"],
     "url": "https://anysilicon.com/feed/"},
    {"name": "Semiconductor Today",
     "weight": 9, "tags": ["semiconductor","compound","GaN","SiC","power"],
     "url": "https://www.semiconductor-today.com/rss/news.rss"},
    {"name": "Tech Xplore 半导体",
     "weight": 9, "tags": ["semiconductor","research","electronics","nanotechnology"],
     "url": "https://techxplore.com/rss-feed/semiconductors-news/"},
    {"name": "Planet Analog",
     "weight": 8, "tags": ["analog","chip","power","sensor"],
     "url": "https://www.planetanalog.com/feed/"},
    {"name": "Evertiq 电子制造",
     "weight": 8, "tags": ["electronics","manufacturing","supply-chain","EMS"],
     "url": "https://feeds2.feedburner.com/Evertiq"},
    {"name": "Semiconductor Industry Association (SIA)",
     "weight": 9, "tags": ["semiconductor","industry","sales","policy","CHIPS-Act"],
     "url": "https://www.semiconductors.org/rss/"},
    {"name": "SEMI Blog",
     "weight": 9, "tags": ["semiconductor","equipment","materials","manufacturing"],
     "url": "https://blog.semi.org/feed"},
    {"name": "The Memory Guy",
     "weight": 9, "tags": ["DRAM","NAND","HBM","memory","storage"],
     "url": "https://thememoryguy.com/feed/"},
]

# ══════════════════════════════════════════════════════
# Tier 2B · 半导体设备 / 晶圆制造 专项（18个）权重 9-10
# 聚焦：ASML/Lam/AMAT/KLA/TEL + 晶圆厂动态（全部国际英文源）
# ══════════════════════════════════════════════════════
TIER2B_EQUIPMENT_FAB = [
    {"name": "GNews: ASML EUV光刻",
     "weight": 10, "tags": ["ASML","EUV","High-NA","lithography"],
     "url": "https://news.google.com/rss/search?q=when:48h+ASML+EUV+lithography+High-NA+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AMAT Lam KLA设备",
     "weight": 10, "tags": ["WFE","AMAT","Lam","KLA","equipment"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+equipment+Applied+Materials+OR+Lam+Research+OR+KLA+revenue&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 东京电子日本设备",
     "weight": 9, "tags": ["Tokyo-Electron","Japan","Screen","equipment"],
     "url": "https://news.google.com/rss/search?q=when:48h+Tokyo+Electron+OR+Screen+Holdings+semiconductor+equipment+Japan&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: TSMC台积电代工",
     "weight": 10, "tags": ["TSMC","foundry","2nm","CoWoS","wafer"],
     "url": "https://news.google.com/rss/search?q=when:48h+TSMC+foundry+wafer+fab+2nm+CoWoS+advanced+packaging+revenue&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: Samsung三星代工",
     "weight": 9, "tags": ["Samsung","foundry","GAA","memory","HBM"],
     "url": "https://news.google.com/rss/search?q=when:48h+Samsung+foundry+GAA+semiconductor+fab+HBM+memory&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: Intel晶圆代工IFS",
     "weight": 9, "tags": ["Intel","IFS","foundry","18A","process"],
     "url": "https://news.google.com/rss/search?q=when:48h+Intel+foundry+IFS+18A+process+node+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: HBM高带宽内存",
     "weight": 10, "tags": ["HBM","HBM4","memory","SKHynix","Micron"],
     "url": "https://news.google.com/rss/search?q=when:48h+HBM+HBM4+HBM3E+high+bandwidth+memory+SK+Hynix+Micron+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 先进封装CoWoS Chiplet",
     "weight": 10, "tags": ["CoWoS","chiplet","3D-IC","SoIC","EMIB","packaging"],
     "url": "https://news.google.com/rss/search?q=when:48h+advanced+packaging+CoWoS+chiplet+3D+IC+EMIB+hybrid+bonding&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: DRAM NAND存储价格",
     "weight": 9, "tags": ["DRAM","NAND","memory","price","supply"],
     "url": "https://news.google.com/rss/search?q=when:48h+DRAM+NAND+memory+price+supply+demand+Samsung+Micron+Kioxia&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: Synopsys Cadence EDA",
     "weight": 9, "tags": ["EDA","Synopsys","Cadence","chip-design"],
     "url": "https://news.google.com/rss/search?q=when:48h+Synopsys+OR+Cadence+EDA+semiconductor+chip+design+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 出口管制芯片禁令",
     "weight": 10, "tags": ["export-control","ban","BIS","Entity-List"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+chip+export+control+ban+BIS+entity+list+China&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: CHIPS法案补贴",
     "weight": 9, "tags": ["CHIPS-Act","subsidy","fab","policy"],
     "url": "https://news.google.com/rss/search?q=when:48h+CHIPS+Act+semiconductor+subsidy+fab+Intel+TSMC+Samsung+billion&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: SMIC中芯国际",
     "weight": 9, "tags": ["SMIC","China","foundry","domestic"],
     "url": "https://news.google.com/rss/search?q=when:48h+SMIC+China+semiconductor+foundry+7nm+domestic+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 晶圆产能扩张",
     "weight": 9, "tags": ["fab","capacity","capex","expansion"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+fab+capacity+expansion+capex+wafer+billion&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 光子芯片CPO",
     "weight": 8, "tags": ["photonics","CPO","optical","interconnect"],
     "url": "https://news.google.com/rss/search?q=when:48h+photonic+chip+co-packaged+optics+CPO+silicon+photonics&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 半导体WFE市场",
     "weight": 9, "tags": ["WFE","market","revenue","SEMI","forecast"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+equipment+WFE+market+revenue+SEMI+forecast+billion&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 汽车芯片功率器件",
     "weight": 8, "tags": ["automotive","chip","SiC","IGBT","power"],
     "url": "https://news.google.com/rss/search?q=when:48h+automotive+chip+semiconductor+SiC+IGBT+power+device+EV&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 半导体并购投资",
     "weight": 9, "tags": ["M&A","acquisition","semiconductor","funding"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+chip+acquisition+merger+funding+billion+investment&ceid=US:en&hl=en-US&gl=US"},
]

# ══════════════════════════════════════════════════════
# Tier 3 · 材料科学 / 先进材料（16个）权重 8-10
# 你的专业背景，学术 + 产业双覆盖
# ══════════════════════════════════════════════════════
TIER3_MATERIALS = [
    # 学术权威期刊
    {"name": "Nature Materials",
     "weight": 10, "tags": ["materials","research","nano","polymer","Nature"],
     "url": "https://www.nature.com/nmat.rss"},
    {"name": "Nature Electronics",
     "weight": 10, "tags": ["materials","electronics","semiconductor","research"],
     "url": "https://www.nature.com/natelectron.rss"},
    {"name": "Advanced Materials (Wiley)",
     "weight": 10, "tags": ["materials","polymer","nanotech","advanced","Wiley"],
     "url": "https://onlinelibrary.wiley.com/feed/15214095/most-recent"},
    {"name": "ACS Nano",
     "weight": 9, "tags": ["nanomaterials","2D","graphene","semiconductor"],
     "url": "https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc=ancac3"},
    {"name": "C&EN 化学工程新闻",
     "weight": 9, "tags": ["chemistry","materials","semiconductor","battery","polymer"],
     "url": "https://cen.acs.org/rss/latest.xml"},
    {"name": "Materials Today",
     "weight": 9, "tags": ["materials","research","industry","advanced"],
     "url": "https://www.materialstoday.com/rss/news/"},
    # 产业新闻
    {"name": "GNews: 固态电池材料",
     "weight": 10, "tags": ["solid-state","battery","lithium","electrolyte","materials"],
     "url": "https://news.google.com/rss/search?q=when:48h+solid+state+battery+lithium+electrolyte+materials+energy+density+Toyota+CATL&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 碳化硅SiC功率器件",
     "weight": 10, "tags": ["SiC","silicon-carbide","power","EV","wafer","materials"],
     "url": "https://news.google.com/rss/search?q=when:48h+silicon+carbide+SiC+power+semiconductor+EV+wafer+device+China&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 氮化镓GaN半导体",
     "weight": 9, "tags": ["GaN","gallium-nitride","power","RF","semiconductor","5G"],
     "url": "https://news.google.com/rss/search?q=when:48h+gallium+nitride+GaN+power+semiconductor+RF+5G+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 稀土关键矿产",
     "weight": 9, "tags": ["rare-earth","critical-minerals","China","supply-chain","magnet"],
     "url": "https://news.google.com/rss/search?q=when:48h+rare+earth+critical+minerals+China+magnet+supply+chain+export&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 钙钛矿太阳能",
     "weight": 8, "tags": ["perovskite","solar","materials","efficiency","photovoltaic"],
     "url": "https://news.google.com/rss/search?q=when:48h+perovskite+solar+cell+materials+efficiency+photovoltaic+breakthrough&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 新材料中国",
     "weight": 9, "tags": ["materials","China","carbon-fiber","innovation","新材料"],
     "url": "https://news.google.com/rss/search?q=when:48h+新材料+OR+碳纤维+OR+超导+OR+石墨烯+OR+先进材料+中国+产业&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: AI材料发现",
     "weight": 9, "tags": ["AI","materials-discovery","simulation","DFT","research"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+materials+discovery+simulation+machine+learning+new+compound&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 3D打印先进制造",
     "weight": 8, "tags": ["3Dprint","additive","manufacturing","metal","aerospace"],
     "url": "https://news.google.com/rss/search?q=when:48h+3D+printing+additive+manufacturing+metal+aerospace+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 氢能燃料电池",
     "weight": 8, "tags": ["hydrogen","fuel-cell","energy","materials","green"],
     "url": "https://news.google.com/rss/search?q=when:48h+hydrogen+fuel+cell+green+energy+materials+electrolyzer&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Compound Semiconductor",
     "weight": 9, "tags": ["compound","GaN","SiC","InP","GaAs","photonics"],
     "url": "https://compoundsemiconductor.net/rss/news"},
]

# ══════════════════════════════════════════════════════
# Tier 4 · 算力 / AI基础设施（14个）权重 9-10
# 聚焦：数据中心 + GPU + 能源 + 推理
# ══════════════════════════════════════════════════════
TIER4_COMPUTE = [
    {"name": "GNews: 英伟达GPU算力",
     "weight": 10, "tags": ["NVIDIA","GPU","Blackwell","Rubin","B200","compute","AI"],
     "url": "https://news.google.com/rss/search?q=when:48h+NVIDIA+GPU+Blackwell+B200+Rubin+GB200+AI+compute+inference&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI数据中心建设",
     "weight": 10, "tags": ["datacenter","AI","infrastructure","gigawatt","power","capex"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+data+center+gigawatt+billion+infrastructure+power+compute+build&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI能源电力核电",
     "weight": 9, "tags": ["AI","energy","nuclear","electricity","power-grid","sustainability"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+data+center+energy+power+nuclear+SMR+electricity+grid&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 液冷散热技术",
     "weight": 9, "tags": ["liquid-cooling","thermal","GPU","datacenter","immersion"],
     "url": "https://news.google.com/rss/search?q=when:48h+liquid+cooling+immersion+data+center+GPU+thermal+management+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI推理效率",
     "weight": 9, "tags": ["inference","efficiency","quantization","distillation","edge-AI"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+inference+efficiency+quantization+distillation+latency+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: Huawei Ascend China GPU",
     "weight": 10, "tags": ["Huawei","Ascend","China","compute","GPU"],
     "url": "https://news.google.com/rss/search?q=when:48h+Huawei+Ascend+910C+China+domestic+GPU+AI+chip+compute&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: China AI compute infra",
     "weight": 9, "tags": ["China","compute","datacenter","AI-infra"],
     "url": "https://news.google.com/rss/search?q=when:48h+China+AI+compute+datacenter+infrastructure+domestic+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Data Center Dynamics",
     "weight": 9, "tags": ["datacenter","AI","power","cooling","infrastructure"],
     "url": "https://www.datacenterdynamics.com/en/rss/"},
    {"name": "Data Center Knowledge",
     "weight": 8, "tags": ["datacenter","cloud","AI","power","cooling"],
     "url": "https://www.datacenterknowledge.com/feed"},
    {"name": "Blocks & Files 存储",
     "weight": 9, "tags": ["storage","HBM","DRAM","flash","AI","NVMe"],
     "url": "https://blocksandfiles.com/feed/"},
    {"name": "GNews: 边缘AI芯片Qualcomm",
     "weight": 8, "tags": ["edge-AI","Qualcomm","Apple-Silicon","NPU","inference","mobile"],
     "url": "https://news.google.com/rss/search?q=when:48h+edge+AI+chip+Qualcomm+Apple+NPU+neural+inference+mobile+embedded&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 互联网络InfiniBand/RoCE",
     "weight": 8, "tags": ["InfiniBand","RoCE","network","GPU-cluster","AI-networking"],
     "url": "https://news.google.com/rss/search?q=when:48h+InfiniBand+RoCE+GPU+cluster+networking+AI+training+bandwidth&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: RISC-V开放架构",
     "weight": 8, "tags": ["RISC-V","open","ISA","chip","China","embedded"],
     "url": "https://news.google.com/rss/search?q=when:48h+RISC-V+chip+processor+open+source+China+embedded+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "HPCwire 超算",
     "weight": 8, "tags": ["HPC","supercomputer","AI","GPU","compute"],
     "url": "https://www.hpcwire.com/feed/"},
]

# ══════════════════════════════════════════════════════
# Tier 5 · 人工智能（22个）权重 8-10
# ══════════════════════════════════════════════════════
TIER5_AI = [
    # 大厂官方
    {"name": "OpenAI Blog",
     "weight": 10, "tags": ["AI","LLM","GPT","AGI","reasoning"],
     "url": "https://openai.com/news/rss.xml"},
    {"name": "Anthropic Blog",
     "weight": 10, "tags": ["AI","Claude","safety","alignment"],
     "url": "https://www.anthropic.com/news/rss"},
    {"name": "Google DeepMind",
     "weight": 9, "tags": ["AI","Gemini","research","AGI"],
     "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Meta AI Blog",
     "weight": 9, "tags": ["AI","Llama","open-source","research"],
     "url": "https://ai.meta.com/blog/rss/"},
    {"name": "NVIDIA AI Blog",
     "weight": 9, "tags": ["GPU","AI","CUDA","inference","compute"],
     "url": "https://blogs.nvidia.com/feed/"},
    {"name": "Hugging Face Blog",
     "weight": 9, "tags": ["AI","open-source","models","community"],
     "url": "https://huggingface.co/blog/feed.xml"},
    # 顶级独立分析
    {"name": "Import AI (Jack Clark)",
     "weight": 9, "tags": ["AI","policy","safety","research"],
     "url": "https://importai.substack.com/feed"},
    {"name": "Interconnects (Nathan Lambert)",
     "weight": 9, "tags": ["AI","LLM","RLHF","training","fine-tuning"],
     "url": "https://www.interconnects.ai/feed"},
    {"name": "Epoch AI",
     "weight": 9, "tags": ["AI","compute","scaling","trends","benchmarks"],
     "url": "https://epochai.org/feed.xml"},
    {"name": "AI Snake Oil",
     "weight": 8, "tags": ["AI","critical","analysis","policy"],
     "url": "https://www.aisnakeoil.com/feed"},
    # 中国大模型
    {"name": "GNews: DeepSeek国产大模型",
     "weight": 10, "tags": ["DeepSeek","China","LLM","open-source","efficient"],
     "url": "https://news.google.com/rss/search?q=when:48h+DeepSeek+OR+Qwen+OR+Kimi+OR+豆包+OR+通义+OR+文心+AI+model+China&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 大模型发布训练",
     "weight": 10, "tags": ["LLM","release","training","benchmark","SOTA"],
     "url": "https://news.google.com/rss/search?q=when:48h+large+language+model+LLM+release+training+benchmark+SOTA+reasoning&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI Agent智能体",
     "weight": 9, "tags": ["AI-agent","autonomous","agentic","workflow","tool-use"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+agent+autonomous+agentic+workflow+tool-use+coding&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI开源模型",
     "weight": 9, "tags": ["open-source","LLM","weights","community","Llama"],
     "url": "https://news.google.com/rss/search?q=when:48h+open+source+AI+model+weights+release+Llama+Mistral+community&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 多模态视觉AI",
     "weight": 8, "tags": ["multimodal","vision","video","image","generation"],
     "url": "https://news.google.com/rss/search?q=when:48h+multimodal+vision+video+AI+model+image+generation+Sora&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: AI监管政策",
     "weight": 8, "tags": ["AI","regulation","policy","EU","safety","governance"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+regulation+policy+government+EU+AI+Act+executive+order+safety&ceid=US:en&hl=en-US&gl=US"},
    {"name": "arXiv cs.AI",
     "weight": 8, "tags": ["AI","papers","research","SOTA"],
     "url": "https://rss.arxiv.org/rss/cs.AI"},
    {"name": "arXiv cs.LG",
     "weight": 8, "tags": ["ML","papers","research","training"],
     "url": "https://rss.arxiv.org/rss/cs.LG"},
    {"name": "VentureBeat AI",
     "weight": 8, "tags": ["AI","enterprise","industry","product"],
     "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "The Decoder AI",
     "weight": 8, "tags": ["AI","news","analysis","LLM"],
     "url": "https://the-decoder.com/feed/"},
    {"name": "机器之心",
     "weight": 9, "tags": ["AI","LLM","research","China"],
     "url": "https://www.jiqizhixin.com/rss"},
    {"name": "量子位",
     "weight": 8, "tags": ["AI","LLM","industry","China"],
     "url": "https://www.qbitai.com/feed"},
]

# ══════════════════════════════════════════════════════
# Tier 6 · 机器人 / 具身智能（精简到3个，权重降低）
# 半导体为主，机器人只作点缀，避免淹没半导体内容
# ══════════════════════════════════════════════════════
TIER6_ROBOTICS = [
    {"name": "GNews: 人形机器人产业",
     "weight": 7, "tags": ["humanoid","robot","Optimus","Figure"],
     "url": "https://news.google.com/rss/search?q=when:48h+humanoid+robot+Optimus+Figure+Boston+Dynamics+embodied+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 机器人芯片传感器",
     "weight": 7, "tags": ["robot","chip","sensor","semiconductor"],
     "url": "https://news.google.com/rss/search?q=when:48h+robot+humanoid+chip+sensor+semiconductor+actuator+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "The Robot Report",
     "weight": 6, "tags": ["robotics","humanoid","industrial"],
     "url": "https://www.therobotreport.com/feed/"},
]

# ══════════════════════════════════════════════════════
# Tier 6B · 半导体补充源（替换原机器人源位置，增强半导体覆盖）
# ══════════════════════════════════════════════════════
TIER6B_SEMI_EXTRA = [
    {"name": "GNews: 半导体财报营收",
     "weight": 10, "tags": ["earnings","revenue","semiconductor","guidance"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+earnings+revenue+guidance+NVIDIA+TSMC+ASML+AMD+results&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 晶圆厂扩产投资",
     "weight": 10, "tags": ["fab","capex","expansion","wafer"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+fab+capacity+expansion+capex+wafer+billion+construction&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 半导体供应链",
     "weight": 9, "tags": ["supply-chain","semiconductor","shortage"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+supply+chain+shortage+disruption+chip+inventory&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 模拟芯片功率器件",
     "weight": 9, "tags": ["analog","power","TI","Infineon","STMicro"],
     "url": "https://news.google.com/rss/search?q=when:48h+analog+chip+power+semiconductor+Texas+Instruments+Infineon+STMicro&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 中国芯片设备国产化",
     "weight": 10, "tags": ["China","equipment","domestic","NAURA","AMEC"],
     "url": "https://news.google.com/rss/search?q=when:48h+China+semiconductor+equipment+domestic+NAURA+AMEC+lithography+localization&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 芯片设计创业",
     "weight": 8, "tags": ["chip-design","startup","fabless","IP"],
     "url": "https://news.google.com/rss/search?q=when:48h+chip+design+startup+fabless+semiconductor+funding+AI+accelerator&ceid=US:en&hl=en-US&gl=US"},
]

# ══════════════════════════════════════════════════════
# Tier 7 · 投资 / 产业链 / 热点追踪（22个）权重 7-10
# 国际投资源 + X/Twitter热点 + 精选中文（大幅增加国际比例）
# ══════════════════════════════════════════════════════
TIER7_INVESTMENT_CN = [
    # 国际 VC & 投资
    {"name": "a16z Blog",
     "weight": 10, "tags": ["VC","AI","semiconductor","investment-thesis"],
     "url": "https://a16z.com/feed/"},
    {"name": "TechCrunch Venture",
     "weight": 9, "tags": ["VC","funding","startups","AI"],
     "url": "https://techcrunch.com/category/venture/feed/"},
    {"name": "Crunchbase News",
     "weight": 9, "tags": ["VC","M&A","funding","deals"],
     "url": "https://news.crunchbase.com/feed/"},
    {"name": "The Diff (Byrne Hobart)",
     "weight": 9, "tags": ["finance","analysis","semiconductor","macro"],
     "url": "https://www.thediff.co/feed/"},
    {"name": "Hacker News",
     "weight": 8, "tags": ["tech","AI","startups","developer"],
     "url": "https://news.ycombinator.com/rss"},
    # 国际GNews热点追踪
    {"name": "GNews: AI funding unicorn",
     "weight": 10, "tags": ["VC","AI","unicorn","funding","billion"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+startup+funding+series+billion+valuation+raise+venture&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: US-China tech compete",
     "weight": 9, "tags": ["US-China","tech","geopolitics","semiconductor"],
     "url": "https://news.google.com/rss/search?q=when:48h+US+China+tech+competition+AI+semiconductor+decoupling&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: semiconductor earnings",
     "weight": 9, "tags": ["earnings","revenue","semiconductor","quarterly"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+earnings+revenue+quarterly+results+guidance+NVIDIA+TSMC&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: Huawei supply chain",
     "weight": 10, "tags": ["Huawei","supply-chain","AI","semiconductor"],
     "url": "https://news.google.com/rss/search?q=when:48h+Huawei+supply+chain+semiconductor+AI+chip+Ascend&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: China chip self-sufficiency",
     "weight": 9, "tags": ["China","semiconductor","domestic","self-sufficiency"],
     "url": "https://news.google.com/rss/search?q=when:48h+China+semiconductor+chip+domestic+self+sufficiency+supply+chain&ceid=US:en&hl=en-US&gl=US"},
    # X/Twitter 半导体热点追踪（24h内最热新闻，模拟推特热搜效果）
    {"name": "GNews: X热点 semiconductor breaking",
     "weight": 10, "tags": ["trending","X","semiconductor","breaking"],
     "url": "https://news.google.com/rss/search?q=when:24h+semiconductor+chip+breaking+major+announcement&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 NVIDIA TSMC earnings",
     "weight": 10, "tags": ["trending","NVIDIA","TSMC","earnings"],
     "url": "https://news.google.com/rss/search?q=when:24h+NVIDIA+OR+TSMC+breaking+OR+announcement+OR+earnings+OR+launch&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 ASML EUV order",
     "weight": 10, "tags": ["trending","ASML","EUV","order"],
     "url": "https://news.google.com/rss/search?q=when:24h+ASML+OR+EUV+OR+lithography+breaking+OR+order+OR+revenue&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 HBM packaging",
     "weight": 10, "tags": ["trending","HBM","CoWoS","packaging"],
     "url": "https://news.google.com/rss/search?q=when:24h+HBM+OR+CoWoS+OR+advanced+packaging+breaking+OR+capacity+OR+shortage&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 chip export ban",
     "weight": 10, "tags": ["trending","export","ban","China"],
     "url": "https://news.google.com/rss/search?q=when:24h+chip+export+control+ban+OR+restriction+OR+sanction+China+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 Samsung Intel foundry",
     "weight": 9, "tags": ["trending","Samsung","Intel","foundry"],
     "url": "https://news.google.com/rss/search?q=when:24h+Samsung+OR+Intel+foundry+OR+fab+breaking+OR+announcement+OR+restructure&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 chip AI compute",
     "weight": 9, "tags": ["trending","AI","compute","chip"],
     "url": "https://news.google.com/rss/search?q=when:24h+AI+chip+compute+datacenter+breaking+OR+major+OR+billion+investment&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: X热点 semiconductor stock",
     "weight": 9, "tags": ["trending","stock","semiconductor","market"],
     "url": "https://news.google.com/rss/search?q=when:24h+semiconductor+stock+surge+OR+crash+OR+earnings+beat+OR+miss+NVIDIA+ASML&ceid=US:en&hl=en-US&gl=US"},
    # McKinsey/Gartner行业报告
    {"name": "GNews: semiconductor industry report",
     "weight": 8, "tags": ["report","industry","McKinsey","Gartner"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+AI+industry+report+McKinsey+OR+Gartner+OR+BCG+forecast&ceid=US:en&hl=en-US&gl=US"},
    # 精选中文（保留最核心的4个）
    {"name": "半导体行业观察",
     "weight": 9, "tags": ["semiconductor","China","chip","industry"],
     "url": "https://news.google.com/rss/search?q=when:48h+半导体+芯片+OR+晶圆+OR+封装+OR+设备+产业&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "虎嗅科技",
     "weight": 8, "tags": ["tech","business","AI","China"],
     "url": "https://www.huxiu.com/rss/0.xml"},
    {"name": "36氪",
     "weight": 8, "tags": ["AI","startups","investment","China"],
     "url": "https://36kr.com/feed"},
    {"name": "South China Morning Post",
     "weight": 9, "tags": ["China","tech","semiconductor","policy"],
     "url": "https://www.scmp.com/rss/5/feed"},
    # 中文GNews（精简到3个最核心）
    {"name": "GNews: 国产大模型",
     "weight": 9, "tags": ["China","LLM","AI","DeepSeek"],
     "url": "https://news.google.com/rss/search?q=when:48h+DeepSeek+OR+Kimi+OR+Qwen+大模型&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: A股半导体",
     "weight": 8, "tags": ["A-share","semiconductor","China"],
     "url": "https://news.google.com/rss/search?q=when:48h+A股+半导体+OR+芯片+产业链&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 中国机器人",
     "weight": 8, "tags": ["China","robot","humanoid"],
     "url": "https://news.google.com/rss/search?q=when:48h+中国+人形机器人+OR+具身智能+产业链&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "Pandaily 中国科技英文",
     "weight": 7, "tags": ["China-tech","AI","semiconductor"],
     "url": "https://pandaily.com/feed/"},
]

# ══════════════════════════════════════════════════════
# 汇总
# ══════════════════════════════════════════════════════
ALL_SOURCES = (
    TIER1
    + TIER2A_SEMI_MEDIA
    + TIER2B_EQUIPMENT_FAB
    + TIER3_MATERIALS
    + TIER4_COMPUTE
    + TIER5_AI
    + TIER6_ROBOTICS
    + TIER6B_SEMI_EXTRA
    + TIER7_INVESTMENT_CN
)

# ══════════════════════════════════════════════════════
# 关键词（中英双语）
# ══════════════════════════════════════════════════════
KEYWORDS_EN = [
    # 半导体核心
    "semiconductor","chip","GPU","CPU","ASIC","FPGA",
    "NVIDIA","TSMC","Intel","AMD","ASML","Qualcomm","ARM",
    "HBM","CoWoS","chiplet","EUV","DUV","lithography","foundry",
    "wafer","fab","etch","deposition","CMP","metrology","EDA",
    "packaging","SoIC","EMIB","3D-IC","advanced packaging",
    "Applied Materials","Lam Research","KLA","Tokyo Electron",
    # 材料
    "SiC","GaN","silicon carbide","gallium nitride","compound semiconductor",
    "materials","battery","solid-state","rare earth","lithium",
    "perovskite","graphene","carbon fiber","substrate",
    # AI & 算力
    "AI","LLM","large language model","GPT","inference","training",
    "agent","autonomous","multimodal","reasoning","benchmark",
    "datacentre","datacenter","compute","gigawatt","liquid cooling",
    "DeepSeek","Gemini","Claude","Llama","Qwen",
    # 机器人
    "humanoid","robot","embodied","robotics","automation",
    "reducer","actuator","manipulation","dexterous",
    # 投资 & 地缘
    "funding","IPO","acquisition","venture capital","valuation",
    "export control","sanction","ban","supply chain","CHIPS Act",
    "geopolitics","US-China","decoupling",
]
KEYWORDS_CN = [
    "半导体","芯片","算力","存储","封装","光刻","刻蚀","晶圆",
    "HBM","先进封装","国产替代","制程","设备",
    "人工智能","大模型","推理","智能体","具身智能",
    "机器人","人形机器人","减速器","谐波","产业链",
    "新材料","碳化硅","氮化镓","固态电池","稀土","碳纤维",
    "华为","昇腾","中芯国际","台积电","英伟达",
    "投资","融资","并购","A股","出口管制",
    "数据中心","智算中心","液冷","能源",
]
KEYWORDS = KEYWORDS_EN + KEYWORDS_CN

if __name__ == "__main__":
    tiers = [
        ("Tier1  顶级财经媒体",       TIER1),
        ("Tier2A 半导体行业媒体",     TIER2A_SEMI_MEDIA),
        ("Tier2B 设备/晶圆制造",      TIER2B_EQUIPMENT_FAB),
        ("Tier3  材料科学",           TIER3_MATERIALS),
        ("Tier4  算力/AI基础设施",    TIER4_COMPUTE),
        ("Tier5  人工智能",           TIER5_AI),
        ("Tier6  机器人/具身智能",    TIER6_ROBOTICS),
        ("Tier6B 半导体补充",        TIER6B_SEMI_EXTRA),
        ("Tier7  投资/产业链/中文",   TIER7_INVESTMENT_CN),
    ]
    total = 0
    print("=" * 55)
    print("新闻源统计")
    print("=" * 55)
    for name, lst in tiers:
        w10 = sum(1 for s in lst if s["weight"] == 10)
        print(f"  {name}: {len(lst):3d} 个  (权重10: {w10}个)")
        total += len(lst)
    print(f"  {'─'*45}")
    print(f"  总计: {total} 个")
    # 重复检查
    names = [s["name"] for s in ALL_SOURCES]
    dups  = [n for n in set(names) if names.count(n) > 1]
    print()
    print("  ✅ 无重复" if not dups else f"  ⚠️  重复: {dups}")
