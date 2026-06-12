"""
page_generator.py — 生成 GitHub Pages 静态页面
参考：masiqi/ai-digest 的设计风格
每次运行后生成/更新：
  docs/daily/YYYY-MM-DD_SESSION.html  — 当日详情页
  docs/index.html                      — 首页列表（追加最新条目）
  docs/feed.xml                        — RSS 订阅源
"""
import os, re, datetime

DATE_STR = datetime.date.today().strftime("%Y-%m-%d")
TODAY    = datetime.date.today().strftime("%Y年%m月%d日")

NOW_HOUR = (datetime.datetime.utcnow().hour + 8) % 24
SESSION  = "午班" if NOW_HOUR >= 14 else "早班"
SESSION_EN = "PM" if SESSION == "午班" else "AM"

SITE_BASE = "https://wangle200104-jpg.github.io/daily-intel-report"

DOMAIN_COLORS = {
    "半导体": ("#6f42c1", "#6f42c110"),
    "算力":   ("#6f42c1", "#6f42c110"),
    "HBM":    ("#6f42c1", "#6f42c110"),
    "AI":     ("#1a6fc4", "#1a6fc410"),
    "大模型": ("#1a6fc4", "#1a6fc410"),
    "机器人": ("#d9730d", "#d9730d10"),
    "材料":   ("#1a7340", "#1a734010"),
    "投资":   ("#c0392b", "#c0392b10"),
    "政策":   ("#6c757d", "#6c757d10"),
}

def domain_color(domain: str) -> tuple:
    for k, v in DOMAIN_COLORS.items():
        if k in domain:
            return v
    return ("#6c757d", "#6c757d10")


def md_to_html(text: str) -> str:
    """极简 Markdown → HTML"""
    # 加粗
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # 标题
    text = re.sub(r'^#{2,3}\s+(.+)$',
                  r'<h3 class="article-sub">\1</h3>', text, flags=re.M)
    # 段落
    paras = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('<'):
            paras.append(line)
        elif line.startswith('【今日启示】'):
            paras.append(
                f'<div class="insight">💡 {line.replace("【今日启示】","").strip()}</div>'
            )
        elif re.match(r'^\d+\.', line) or line.startswith('·') or line.startswith('•'):
            paras.append(f'<li>{line.lstrip("0123456789.·• ")}</li>')
        else:
            paras.append(f'<p>{line}</p>')
    return '\n'.join(paras)


def parse_brief_text(brief_text: str) -> list[dict]:
    """解析 ===第N条=== 格式的快讯"""
    items = []
    blocks = re.split(r'===第\d+条===', brief_text)
    for block in [b.strip() for b in blocks if b.strip()]:
        dm = re.search(r'领域[：:]\s*(.+)', block)
        tm = re.search(r'标题[：:]\s*(.+)', block)
        bm = re.search(r'正文[：:]\s*([\s\S]+?)(?=启示[：:]|$)', block)
        im = re.search(r'启示[：:]\s*(.+)', block)
        items.append({
            "domain":  dm.group(1).strip() if dm else "",
            "title":   tm.group(1).strip() if tm else "",
            "body":    bm.group(1).strip() if bm else block[:200],
            "insight": im.group(1).strip() if im else "",
        })
    return items


    """生成当日详情页 HTML"""
def generate_daily_html(header: str, deep_text: str, brief_text: str,
                        deep_list: list = None) -> str:
    """生成当日详情页 HTML，支持文章配图"""
    if deep_list is None:
        deep_list = []

    # 解析深度文章
    articles = [a.strip() for a in re.split(r'\n---\n', deep_text)
                if a.strip() and len(a.strip()) > 50]

    # 深度文章卡片
    art_cards = []
    for i, art in enumerate(articles[:10], 1):
        tm = (re.search(r'##\s+深度[文章]*\d*[：:]\s*(.+)', art)
              or re.search(r'##\s+(.+)', art))
        title = tm.group(1).strip() if tm else f"文章 {i}"
        dm    = re.search(r'\*\*领域\*\*[：:]\s*(.+)', art)
        domain= dm.group(1).strip() if dm else ""
        body  = re.sub(r'^##[^\n]+\n', '', art, count=1).strip()
        body  = re.sub(r'\*\*来源\*\*[^\n]+\n?', '', body).strip()
        fg, bg = domain_color(domain)

        domain_badge = (
            f'<span class="domain-badge" style="color:{fg};background:{bg};'
            f'border:1px solid {fg}40">{domain}</span>'
            if domain else ""
        )

        # 从 deep_list 取图片 URL 和 原文链接
        img_url  = ""
        link_url = ""
        src_name = ""
        if i <= len(deep_list):
            img_url  = deep_list[i-1].get("image", "") or ""
            link_url = deep_list[i-1].get("link", "") or ""
            src_name = deep_list[i-1].get("source", "") or ""
        img_html = (
            f'<img class="article-img" src="{img_url}" alt="{title}" '
            f'loading="lazy" onerror="this.style.display=\'none\'">'
            if img_url else ""
        )
        link_html = ""
        if link_url:
            link_html = (
                f'<div class="article-source">'
                f'<a href="{link_url}" target="_blank" rel="noopener">'
                f'🔗 查看原文</a>'
                f'<span>{src_name}</span>'
                f'</div>'
            )

        art_cards.append(f"""
<div class="article-card">
  <div class="article-header">
    <span class="article-num">{i:02d}</span>
    {domain_badge}
    <h2 class="article-title">{title}</h2>
  </div>
  {img_html}
  <div class="article-body">{md_to_html(body[:1200])}</div>
  {link_html}
</div>""")

    # 快讯卡片
    briefs = parse_brief_text(brief_text)
    brief_cards = []
    for i, b in enumerate(briefs, 1):
        fg, bg = domain_color(b["domain"])
        insight_html = (
            f'<div class="brief-insight">📌 {b["insight"]}</div>'
            if b["insight"] else ""
        )
        brief_cards.append(f"""
<div class="brief-item">
  <div class="brief-header">
    <span class="brief-num">{i:02d}</span>
    <span class="domain-badge sm" style="color:{fg};background:{bg};border:1px solid {fg}40">
      {b["domain"]}
    </span>
    <span class="brief-title">{b["title"]}</span>
  </div>
  <div class="brief-body">{b["body"]}</div>
  {insight_html}
</div>""")

    # 导读处理
    kw_m = re.search(r'今日关键词[：:]\s*(.+)', header)
    kw_html = ""
    if kw_m:
        kws = [k.strip() for k in re.split(r'[·\s]+', kw_m.group(1)) if k.strip()]
        colors = ["#c0392b","#1a6fc4","#1a7340","#6f42c1","#d9730d"]
        kw_html = '<div class="kw-row">' + ''.join(
            f'<span class="kw-tag" style="color:{colors[i%5]};'
            f'background:{colors[i%5]}15;border:1px solid {colors[i%5]}40">{k}</span>'
            for i, k in enumerate(kws)
        ) + '</div>'
        header_text = header[:kw_m.start()].strip()
    else:
        header_text = header.strip()

    header_html = re.sub(r'\*\*(.+?)\*\*',
                         r'<strong style="color:#c0392b">\1</strong>',
                         header_text)

    page_url = f"{SITE_BASE}/daily/{DATE_STR}_{SESSION}.html"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta property="og:title" content="每日科技投资简报 {TODAY} {SESSION}">
<meta property="og:description" content="{header_text[:120]}">
<meta property="og:url" content="{page_url}">
<title>🧠 每日科技投资简报 · {TODAY} · {SESSION}</title>
<style>
:root {{
  --bg:#0d1117; --card:#161b22; --border:#30363d;
  --text:#e6edf3; --text2:#8b949e; --light:#adb5bd;
  --red:#c0392b; --blue:#1a6fc4; --green:#1a7340;
  --red-bg:#c0392b15; --surface:#1c2128;
}}
@media (prefers-color-scheme: light) {{
  :root {{
    --bg:#f8f9fa; --card:#ffffff; --border:#e9ecef;
    --text:#0d1117; --text2:#6c757d; --light:#adb5bd;
    --surface:#f1f3f5;
  }}
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system,BlinkMacSystemFont,"PingFang SC",
               "Helvetica Neue",sans-serif;
  background:var(--bg); color:var(--text);
  font-size:15px; line-height:1.8;
  max-width:860px; margin:0 auto; padding:20px 16px 60px;
}}
a {{ color:var(--blue); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}

/* 导航 */
.nav {{
  display:flex; align-items:center; justify-content:space-between;
  padding:12px 0; border-bottom:1px solid var(--border); margin-bottom:24px;
}}
.nav-brand {{ font-weight:800; font-size:16px; color:var(--text); }}
.nav-links {{ display:flex; gap:16px; font-size:13px; }}

/* 顶部 */
.header {{
  padding:28px 0 24px; border-bottom:1px solid var(--border); margin-bottom:28px;
}}
.header-top {{ display:flex; align-items:center; gap:10px; margin-bottom:14px; }}
.session-label {{
  font-size:11px; font-weight:700; padding:3px 10px; border-radius:4px;
  background:var(--red); color:#fff;
}}
.header-date {{ font-size:14px; color:var(--text2); }}
.header-title {{ font-size:28px; font-weight:900; line-height:1.3; }}

/* 导读卡片 */
.intro-card {{
  background:var(--surface); border:1px solid var(--border);
  border-left:3px solid var(--red); border-radius:0 8px 8px 0;
  padding:16px 18px; margin-top:16px;
}}
.intro-card p {{ color:var(--text); font-size:15px; line-height:1.85; }}
.kw-row {{ margin-top:12px; display:flex; flex-wrap:wrap; gap:6px; }}
.kw-tag {{
  font-size:11px; font-weight:600; padding:2px 9px;
  border-radius:20px; cursor:default;
}}

/* 深度文章 */
.section-label {{
  font-size:12px; font-weight:700; text-transform:uppercase;
  letter-spacing:1px; color:var(--text2);
  margin:32px 0 14px; padding-bottom:8px;
  border-bottom:1px solid var(--border);
  display:flex; align-items:center; gap:6px;
}}
.article-card {{
  background:var(--card); border:1px solid var(--border);
  border-radius:12px; padding:20px 22px; margin-bottom:16px;
}}
.article-header {{
  display:flex; align-items:flex-start; gap:8px; margin-bottom:12px;
  flex-wrap:wrap;
}}
.article-num {{
  font-size:10px; font-weight:800; color:#fff;
  background:var(--red); padding:2px 6px; border-radius:3px;
  flex-shrink:0; margin-top:3px;
}}
.domain-badge {{
  font-size:11px; font-weight:600; padding:2px 8px;
  border-radius:4px; flex-shrink:0; margin-top:2px;
}}
.domain-badge.sm {{ font-size:10px; padding:1px 6px; }}
.article-title {{
  font-size:18px; font-weight:700; line-height:1.4; flex:1;
}}
.article-body p {{
  font-size:15px; color:var(--text); line-height:1.85; margin-bottom:10px;
}}
.article-img {{
  width:100%; max-height:240px; object-fit:cover;
  border-radius:8px; margin-bottom:14px;
  border:1px solid var(--border); display:block;
}}
.article-body h3.article-sub {{
  font-size:14px; font-weight:700; color:var(--text2);
  margin:12px 0 6px;
}}
.insight {{
  margin-top:12px; padding:10px 14px;
  background:var(--red-bg); border-left:3px solid var(--red);
  border-radius:0 6px 6px 0;
  font-size:13px; font-weight:600; color:var(--red);
}}
.article-source {{
  margin-top:10px; padding-top:8px; border-top:1px dashed var(--border);
  display:flex; align-items:center; gap:10px; font-size:12px;
}}
.article-source a {{
  color:var(--blue); font-weight:600; text-decoration:none;
}}
.article-source a:hover {{ text-decoration:underline; }}
.article-source span {{ color:var(--text2); }}

/* 快讯 */
.brief-item {{
  border-bottom:1px solid var(--border); padding:12px 0;
}}
.brief-item:last-child {{ border-bottom:none; }}
.brief-header {{
  display:flex; align-items:flex-start; gap:6px; margin-bottom:6px;
}}
.brief-num {{
  font-size:11px; font-weight:700; color:var(--light);
  min-width:22px; text-align:right; flex-shrink:0; margin-top:2px;
}}
.brief-title {{ font-size:15px; font-weight:700; line-height:1.4; }}
.brief-body {{ font-size:13px; color:var(--text2); line-height:1.75; padding-left:28px; }}
.brief-insight {{
  margin-top:5px; padding:4px 10px; margin-left:28px;
  background:var(--surface); border-radius:4px;
  font-size:12px; font-weight:600; color:var(--green);
}}

/* 作者卡片 */
.author-card {{
  background:var(--card); border:1px solid var(--border);
  border-radius:12px; padding:18px 20px; margin-top:32px;
  display:flex; align-items:center; gap:16px;
}}
.author-avatar {{
  width:52px; height:52px; border-radius:50%; flex-shrink:0;
  background:var(--surface); border:2px solid var(--red);
  display:flex; align-items:center; justify-content:center;
  font-size:22px;
}}
.author-name {{ font-size:15px; font-weight:700; }}
.author-meta {{ font-size:13px; color:var(--text2); margin-top:3px; }}
.author-links {{ display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }}
.author-link {{
  font-size:12px; padding:3px 10px; border-radius:6px;
  border:1px solid var(--border); color:var(--text); background:var(--surface);
}}
.author-link:hover {{ border-color:var(--blue); text-decoration:none; }}

.footer {{
  margin-top:40px; text-align:center; font-size:12px; color:var(--text2); line-height:2;
  border-top:1px solid var(--border); padding-top:20px;
}}
</style>
</head>
<body>

<div class="nav">
  <a class="nav-brand" href="../index.html">🧠 每日科技投资简报</a>
  <div class="nav-links">
    <a href="https://x.com/wangsir1w" target="_blank">𝕏 @wangsir1w</a>
    <a href="../feed.xml">📡 RSS</a>
  </div>
</div>

<div class="header">
  <div class="header-top">
    <span class="session-label">{SESSION} · {SESSION_EN}</span>
    <span class="header-date">{TODAY}</span>
  </div>
  <div class="header-title">每日科技投资简报</div>
  <div class="intro-card">
    <p>{header_html}</p>
    {kw_html}
    <p style="margin-top:10px;font-size:12px;color:var(--text2)">
      深度长文见下方 · 精选快讯见底部
    </p>
  </div>
</div>

<div class="section-label">📰 深度长文 · {len(art_cards)} 篇</div>
{''.join(art_cards)}

<div class="section-label">⚡ 精选快讯 · {len(brief_cards)} 条</div>
<div class="brief-list">
{''.join(brief_cards)}
</div>

<div class="author-card">
  <div class="author-avatar">👤</div>
  <div>
    <div class="author-name">王sir · 材料工程师 / 投资人</div>
    <div class="author-meta">深圳 · 韶音 · 工厂/制造 · 材料创新 · 价值投资</div>
    <div class="author-links">
      <a class="author-link" href="https://x.com/wangsir1w" target="_blank">𝕏 @wangsir1w</a>
      <a class="author-link" href="https://github.com/wangle200104-jpg/daily-intel-report" target="_blank">📦 GitHub</a>
      <span class="author-link">💬 微信 13973780026</span>
    </div>
  </div>
</div>

<div class="footer">
  由 GitHub Actions + DeepSeek V4 Pro 自动生成<br>
  {TODAY} · {SESSION} · 聚焦半导体·算力·材料·AI·机器人
</div>

</body>
</html>"""


def update_index(page_url_rel: str, date_str: str, session: str, header_snippet: str):
    """在首页列表顶部插入新条目"""
    index_path = "docs/index.html"
    if not os.path.exists(index_path):
        return

    with open(index_path, encoding="utf-8") as f:
        html = f.read()

    session_badge_cls = "pm" if session == "午班" else ""
    snippet = header_snippet[:60].replace('<', '&lt;').replace('>', '&gt;')

    new_item = f"""  <li class="day-item" onclick="location.href='{page_url_rel}'">
    <div style="flex:1">
      <a href="{page_url_rel}">{date_str} · {session}</a>
      <div class="day-meta">
        <span>{snippet}…</span>
      </div>
    </div>
    <span class="session-badge {session_badge_cls}">{session}</span>
  </li>
"""
    # 在 <!-- 由 GitHub Actions 自动更新 --> 后插入
    marker = "  <!-- 由 GitHub Actions 自动更新 -->\n"
    if marker in html and new_item not in html:
        html = html.replace(marker, marker + new_item)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ 首页列表已更新：{date_str} {session}")


def generate_rss(entries: list[dict]):
    """生成/更新 RSS feed.xml"""
    items_xml = ""
    for e in entries[:20]:
        items_xml += f"""
  <item>
    <title>{e['title']}</title>
    <link>{e['link']}</link>
    <pubDate>{e['date']}</pubDate>
    <description><![CDATA[{e['desc'][:300]}]]></description>
  </item>"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>每日科技投资简报 | 王sir</title>
  <link>{SITE_BASE}</link>
  <description>聚焦半导体·算力·材料·AI·机器人 每天09:00+16:00推送</description>
  <language>zh-CN</language>
  {items_xml}
</channel>
</rss>"""

    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)
    print("✅ feed.xml 已更新")


def publish_page(header: str, deep_text: str, brief_text: str,
                deep_list: list = None):
    """主入口：生成详情页 + 更新首页 + 更新RSS"""
    os.makedirs("docs/daily", exist_ok=True)

    # 生成详情页（传入deep_list用于图片显示）
    filename  = f"{DATE_STR}_{SESSION}.html"
    filepath  = f"docs/daily/{filename}"
    page_url  = f"{SITE_BASE}/daily/{filename}"
    page_html = generate_daily_html(header, deep_text, brief_text,
                                    deep_list=deep_list or [])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"✅ 详情页生成：{filepath}")
    print(f"   访问地址：{page_url}")

    # 更新首页列表
    update_index(
        page_url_rel=f"daily/{filename}",
        date_str=DATE_STR,
        session=SESSION,
        header_snippet=re.sub(r'<[^>]+>', '', header)[:60],
    )

    # 更新 RSS（读取最近条目）
    try:
        existing_rss = []
        if os.path.exists("docs/feed.xml"):
            with open("docs/feed.xml") as f:
                rss_src = f.read()
            for m in re.finditer(r'<item>(.*?)</item>', rss_src, re.S):
                t  = re.search(r'<title>(.*?)</title>', m.group(1))
                lk = re.search(r'<link>(.*?)</link>', m.group(1))
                dt = re.search(r'<pubDate>(.*?)</pubDate>', m.group(1))
                ds = re.search(r'<!\[CDATA\[(.*?)\]\]>', m.group(1), re.S)
                existing_rss.append({
                    "title": t.group(1) if t else "",
                    "link":  lk.group(1) if lk else "",
                    "date":  dt.group(1) if dt else "",
                    "desc":  ds.group(1) if ds else "",
                })
        new_entry = {
            "title": f"每日科技投资简报 {DATE_STR} {SESSION}",
            "link":  page_url,
            "date":  datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "desc":  re.sub(r'<[^>]+>', '', header)[:300],
        }
        generate_rss([new_entry] + existing_rss)
    except Exception as e:
        print(f"  ⚠️ RSS更新失败: {e}")

    return page_url
