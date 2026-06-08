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
# Tier 2B · 半导体设备 / 晶圆制造 专项（16个）权重 9-10
# 聚焦：ASML/Lam/AMAT/KLA/TEL + 晶圆厂动态
# ══════════════════════════════════════════════════════
TIER2B_EQUIPMENT_FAB = [
    # Google News 设备专项
    {"name": "GNews: ASML EUV光刻机",
     "weight": 10, "tags": ["ASML","EUV","DUV","lithography","High-NA"],
     "url": "https://news.google.com/rss/search?q=when:48h+ASML+EUV+lithography+High-NA+semiconductor+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 半导体设备 AMAT/Lam/KLA",
     "weight": 10, "tags": ["WFE","Applied-Materials","Lam-Research","KLA","equipment"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+equipment+Applied+Materials+Lam+Research+KLA+wafer+fab&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 东京电子TEL日本设备",
     "weight": 9, "tags": ["Tokyo-Electron","Japan","equipment","etch","deposition"],
     "url": "https://news.google.com/rss/search?q=when:48h+Tokyo+Electron+semiconductor+equipment+Japan+chip+fab&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 台积电晶圆厂",
     "weight": 10, "tags": ["TSMC","foundry","3nm","2nm","N2","CoWoS","packaging"],
     "url": "https://news.google.com/rss/search?q=when:48h+TSMC+台积电+foundry+wafer+fab+N2+3nm+CoWoS+advanced&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 三星晶圆代工",
     "weight": 9, "tags": ["Samsung","foundry","GAA","SF3","memory","wafer"],
     "url": "https://news.google.com/rss/search?q=when:48h+Samsung+foundry+GAA+SF3+wafer+semiconductor+fab+Korea&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 英特尔晶圆厂IFS",
     "weight": 9, "tags": ["Intel","IFS","foundry","18A","process","fab"],
     "url": "https://news.google.com/rss/search?q=when:48h+Intel+foundry+IFS+18A+process+node+fab+wafer&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: HBM高带宽内存",
     "weight": 10, "tags": ["HBM","HBM4","memory","SKHynix","Samsung","Micron"],
     "url": "https://news.google.com/rss/search?q=when:48h+HBM+high+bandwidth+memory+HBM4+HBM3+SK+Hynix+Micron+AI+chip&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 先进封装CoWoS/Chiplet",
     "weight": 10, "tags": ["CoWoS","chiplet","3D-IC","SoIC","EMIB","HPC","packaging"],
     "url": "https://news.google.com/rss/search?q=when:48h+advanced+packaging+CoWoS+chiplet+3D+IC+EMIB+SoIC+HBM&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 晶圆代工产能扩张",
     "weight": 9, "tags": ["fab","capacity","capex","wafer","expansion","CHIPS-Act"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+fab+capacity+expansion+capex+wafer+CHIPS+Act+Arizona+Japan&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 出口管制设备禁令",
     "weight": 10, "tags": ["export-control","ban","equipment","China","BIS","Entity-List"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+equipment+export+control+ban+China+BIS+Entity+List+restriction&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 国产设备替代",
     "weight": 10, "tags": ["China","equipment","domestic","光刻机","刻蚀机"],
     "url": "https://news.google.com/rss/search?q=when:48h+国产+光刻机+OR+刻蚀机+OR+薄膜设备+OR+中微+OR+北方华创+OR+华海清科+半导体设备&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 中芯国际SMIC",
     "weight": 9, "tags": ["SMIC","China","foundry","domestic","7nm"],
     "url": "https://news.google.com/rss/search?q=when:48h+SMIC+中芯国际+foundry+China+semiconductor+fab+7nm&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 晶圆级衬底材料",
     "weight": 9, "tags": ["wafer","substrate","silicon","SiC","GaN","substrate-materials"],
     "url": "https://news.google.com/rss/search?q=when:48h+wafer+substrate+silicon+carbide+SiC+GaN+semiconductor+materials&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: DRAM NAND价格供应链",
     "weight": 9, "tags": ["DRAM","NAND","memory","price","supply-chain","shortage"],
     "url": "https://news.google.com/rss/search?q=when:48h+DRAM+NAND+memory+price+supply+shortage+Samsung+Micron+Kioxia&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 光子芯片互联CPO",
     "weight": 9, "tags": ["photonics","optical","CPO","interconnect","silicon-photonics"],
     "url": "https://news.google.com/rss/search?q=when:48h+photonic+chip+optical+co-packaged+CPO+silicon+photonics+interconnect&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 量子计算芯片",
     "weight": 8, "tags": ["quantum","computing","chip","qubit","error-correction"],
     "url": "https://news.google.com/rss/search?q=when:48h+quantum+computing+chip+qubit+error+correction+IBM+Google+Microsoft&ceid=US:en&hl=en-US&gl=US"},
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
    {"name": "GNews: 国产算力华为昇腾",
     "weight": 10, "tags": ["Huawei","Ascend","China","compute","GPU","算力"],
     "url": "https://news.google.com/rss/search?q=when:48h+华为昇腾+OR+910C+OR+国产GPU+OR+寒武纪+OR+海光+OR+算力+国产替代&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 中国算力基建",
     "weight": 9, "tags": ["China","compute","datacenter","AI-infra","智算中心"],
     "url": "https://news.google.com/rss/search?q=when:48h+中国+智算中心+OR+算力+OR+数据中心+AI+基础设施+建设&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
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
# Tier 6 · 机器人 / 具身智能（14个）权重 8-10
# ══════════════════════════════════════════════════════
TIER6_ROBOTICS = [
    {"name": "GNews: 人形机器人产业",
     "weight": 10, "tags": ["humanoid","robot","Optimus","Figure","Boston-Dynamics"],
     "url": "https://news.google.com/rss/search?q=when:48h+humanoid+robot+Optimus+Figure+01+Boston+Dynamics+embodied+AI&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 具身智能AI",
     "weight": 10, "tags": ["embodied-AI","physical-AI","manipulation","dexterous"],
     "url": "https://news.google.com/rss/search?q=when:48h+embodied+AI+physical+intelligence+robot+manipulation+dexterous+learning&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 中国机器人产业链",
     "weight": 10, "tags": ["China","humanoid","robot","reducer","motor","supply-chain"],
     "url": "https://news.google.com/rss/search?q=when:48h+中国+人形机器人+OR+减速器+OR+谐波+OR+绿的谐波+OR+具身智能+OR+宇树&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 工业机器人自动化",
     "weight": 9, "tags": ["industrial","robot","automation","factory","AI","manufacturing"],
     "url": "https://news.google.com/rss/search?q=when:48h+industrial+robot+automation+factory+AI+manufacturing+arm&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 机器人零部件",
     "weight": 9, "tags": ["reducer","motor","sensor","actuator","robot-parts"],
     "url": "https://news.google.com/rss/search?q=when:48h+robot+harmonic+reducer+motor+torque+sensor+actuator+supply+chain&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 自动驾驶AI",
     "weight": 8, "tags": ["autonomous","self-driving","EV","AI","Tesla","Waymo"],
     "url": "https://news.google.com/rss/search?q=when:48h+autonomous+driving+AI+chip+Tesla+FSD+Waymo+robotaxi+semiconductor&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Robohub",
     "weight": 9, "tags": ["robotics","research","AI","embodied"],
     "url": "https://robohub.org/feed/"},
    {"name": "IEEE Robotics 机器人",
     "weight": 9, "tags": ["robotics","research","AI","control","manipulation"],
     "url": "https://news.google.com/rss/search?q=when:48h+IEEE+robotics+automation+AI+manipulation+control+humanoid&ceid=US:en&hl=en-US&gl=US"},
    {"name": "Robotics & Automation News",
     "weight": 8, "tags": ["robotics","automation","AI","manufacturing"],
     "url": "https://roboticsandautomationnews.com/feed/"},
    {"name": "BAIR Blog 机器人AI",
     "weight": 8, "tags": ["AI","robotics","research","Berkeley"],
     "url": "https://bair.berkeley.edu/blog/feed.xml"},
    {"name": "GNews: 特斯拉Optimus人形",
     "weight": 9, "tags": ["Tesla","Optimus","humanoid","robot","Musk","production"],
     "url": "https://news.google.com/rss/search?q=when:48h+Tesla+Optimus+humanoid+robot+production+update+Musk&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 智能制造工业AI",
     "weight": 8, "tags": ["smart-manufacturing","Industry4.0","AI","factory","China"],
     "url": "https://news.google.com/rss/search?q=when:48h+智能制造+OR+工业AI+OR+数字工厂+OR+智能工厂+机器人&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "The Robot Report",
     "weight": 8, "tags": ["robotics","humanoid","industrial","AI"],
     "url": "https://www.therobotreport.com/feed/"},
    {"name": "GNews: 波士顿动力机器狗",
     "weight": 7, "tags": ["Boston-Dynamics","Spot","Atlas","robot","commercial"],
     "url": "https://news.google.com/rss/search?q=when:48h+Boston+Dynamics+Atlas+Spot+robot+commercial+AI+deployment&ceid=US:en&hl=en-US&gl=US"},
]

# ══════════════════════════════════════════════════════
# Tier 7 · 投资 / 产业链 / 中文媒体（22个）权重 7-10
# ══════════════════════════════════════════════════════
TIER7_INVESTMENT_CN = [
    # VC & 投资
    {"name": "a16z Blog",
     "weight": 10, "tags": ["VC","AI","semiconductor","investment-thesis"],
     "url": "https://a16z.com/feed/"},
    {"name": "TechCrunch 融资",
     "weight": 9, "tags": ["VC","funding","startups","AI","semiconductor"],
     "url": "https://techcrunch.com/category/venture/feed/"},
    {"name": "GNews: AI融资独角兽",
     "weight": 10, "tags": ["VC","AI","unicorn","funding","billion","valuation"],
     "url": "https://news.google.com/rss/search?q=when:48h+AI+startup+funding+series+billion+valuation+raise+venture&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 芯片半导体投资",
     "weight": 10, "tags": ["semiconductor","investment","funding","PE","M&A"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+chip+investment+funding+billion+venture+acquisition&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: 中美科技竞争",
     "weight": 9, "tags": ["US-China","tech","geopolitics","semiconductor","decoupling"],
     "url": "https://news.google.com/rss/search?q=when:48h+US+China+tech+competition+AI+semiconductor+decoupling+supply+chain&ceid=US:en&hl=en-US&gl=US"},
    {"name": "GNews: CHIPS法案补贴",
     "weight": 9, "tags": ["CHIPS-Act","subsidy","fab","US","semiconductor","policy"],
     "url": "https://news.google.com/rss/search?q=when:48h+CHIPS+Act+semiconductor+subsidy+fab+Intel+TSMC+Samsung+grant&ceid=US:en&hl=en-US&gl=US"},
    # A股 + 中国产业
    {"name": "GNews: A股半导体产业链",
     "weight": 9, "tags": ["A-share","semiconductor","China","supply-chain","stocks"],
     "url": "https://news.google.com/rss/search?q=when:48h+A股+半导体+OR+芯片+OR+AI+产业链+OR+国产替代+设备&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 华为产业链",
     "weight": 10, "tags": ["Huawei","supply-chain","AI","semiconductor","5G"],
     "url": "https://news.google.com/rss/search?q=when:48h+华为+昇腾+OR+供应链+OR+鸿蒙+AI+产业&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 中国AI政策",
     "weight": 9, "tags": ["China","AI","policy","government","regulation"],
     "url": "https://news.google.com/rss/search?q=when:48h+中国+AI+人工智能+政策+OR+工信部+OR+科技部+OR+规划&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 新能源锂电产业链",
     "weight": 8, "tags": ["battery","CATL","BYD","lithium","EV","supply-chain"],
     "url": "https://news.google.com/rss/search?q=when:48h+宁德时代+OR+比亚迪+OR+锂电池+OR+新能源+产业链+材料&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    # 中文科技媒体
    {"name": "虎嗅科技",
     "weight": 8, "tags": ["tech","business","AI","China"],
     "url": "https://www.huxiu.com/rss/0.xml"},
    {"name": "36氪",
     "weight": 8, "tags": ["AI","startups","investment","China"],
     "url": "https://36kr.com/feed"},
    {"name": "钛媒体",
     "weight": 7, "tags": ["AI","tech","investment","China"],
     "url": "https://www.tmtpost.com/rss"},
    {"name": "Pandaily 中国科技英文",
     "weight": 7, "tags": ["China-tech","AI","startups","semiconductor"],
     "url": "https://pandaily.com/feed/"},
    {"name": "Technode",
     "weight": 7, "tags": ["China-tech","AI","policy","semiconductor"],
     "url": "https://technode.com/feed/"},
    {"name": "华尔街见闻",
     "weight": 8, "tags": ["finance","macro","investment","China","AI"],
     "url": "https://wallstreetcn.com/rss"},
    {"name": "GNews: 国产大模型中文",
     "weight": 9, "tags": ["China","LLM","AI","DeepSeek","Kimi","Qwen"],
     "url": "https://news.google.com/rss/search?q=when:48h+DeepSeek+OR+通义+OR+Kimi+OR+豆包+OR+文心+大模型+发布&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 中国机器人政策",
     "weight": 8, "tags": ["China","robot","humanoid","policy","industry"],
     "url": "https://news.google.com/rss/search?q=when:48h+中国+机器人+政策+OR+人形机器人+OR+工业机器人+规划+产业&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "GNews: 中国材料能源",
     "weight": 8, "tags": ["China","materials","energy","battery","solar"],
     "url": "https://news.google.com/rss/search?q=when:48h+中国+新材料+OR+固态电池+OR+光伏+OR+碳化硅+OR+稀土+产业&ceid=CN:zh-Hans&hl=zh-CN&gl=CN"},
    {"name": "Hacker News",
     "weight": 8, "tags": ["tech","AI","startups","developer"],
     "url": "https://news.ycombinator.com/rss"},
    {"name": "GNews: 科技股Q&A财报",
     "weight": 7, "tags": ["earnings","semiconductor","AI","stocks","results"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+AI+earnings+results+revenue+guidance+quarterly&ceid=US:en&hl=en-US&gl=US"},
    {"name": "McKinsey 半导体",
     "weight": 8, "tags": ["semiconductor","industry","analysis","strategy"],
     "url": "https://news.google.com/rss/search?q=when:48h+semiconductor+AI+materials+robot+supply+chain+McKinsey+BCG+Gartner+report&ceid=US:en&hl=en-US&gl=US"},
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
