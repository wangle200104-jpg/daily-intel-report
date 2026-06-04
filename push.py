"""
push.py v9 — 微信推送
2条消息：① 深度长文  ② 今日导读+快讯（合并）
"""
import os, re, requests, time

WXP_LIMIT  = 40000
SC_LIMIT   = 32768
WXP_API    = "https://wxpusher.zjiecode.com/api/send/message"
SC_API_TPL = "https://sctapi.ftqq.com/{key}.send"

AUTHOR_TITLE   = "材料工程师 / 投资人"
AUTHOR_BIO     = "深圳 · 韶音"
AUTHOR_TAGS    = "工厂/制造 · 材料创新 · 价值投资"
AUTHOR_TWITTER = "@wangsir1w"
AUTHOR_TWURL   = "https://x.com/wangsir1w"
AUTHOR_WECHAT  = "13973780026"
AUTHOR_WXNOTE  = "备注已关注X账号"

# ── 图片 base64（从原push.py读取）───────────────
_IMG_FULL = "data:image/jpeg;base64,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"
_IMG_CROP = "data:image/jpeg;base64,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"

# ── 白底财经配色 ──────────────────────────────────
C_BG      = "#ffffff"
C_SURFACE = "#f8f9fa"
C_SURF2   = "#f1f3f5"
C_BORDER  = "#e9ecef"
C_BORDER2 = "#ced4da"
C_INK     = "#0d1117"
C_INK2    = "#343a40"
C_MUTED   = "#6c757d"
C_LIGHT   = "#adb5bd"
C_RED     = "#c0392b"
C_RED_BG  = "#fdf3f2"
C_BLUE    = "#1a6fc4"
C_GREEN   = "#1a7340"
C_GRN_BG  = "#f0faf4"

_DP = {
    "大模型": ("#1a6fc4","#e8f0fb"), "LLM":("#1a6fc4","#e8f0fb"),
    "AI":("#1a6fc4","#e8f0fb"), "云计算":("#1a6fc4","#e8f0fb"),
    "半导体":("#6f42c1","#f0ebff"), "芯片":("#6f42c1","#f0ebff"),
    "GPU":("#6f42c1","#f0ebff"), "算力":("#6f42c1","#f0ebff"),
    "投资":("#c0392b","#fdf2f2"), "融资":("#c0392b","#fdf2f2"),
    "VC":("#c0392b","#fdf2f2"),
    "机器人":("#1a7340","#f0faf4"), "智能体":("#1a7340","#f0faf4"),
    "Agent":("#1a7340","#f0faf4"),
    "开源":("#d9730d","#fff4e6"),
    "政策":("#6c757d","#f1f3f5"), "监管":("#6c757d","#f1f3f5"),
}

def _ds(domain):
    for k,(fg,bg) in _DP.items():
        if k in domain: return fg, bg
    return C_MUTED, C_SURF2

def _tag(text, fg, bg):
    s  = 'background:' + bg + ';color:' + fg + ';font-size:10px;font-weight:600;'
    s += 'padding:1px 6px;border-radius:3px;margin:1px 3px 1px 0;display:inline-block'
    return '<span style="' + s + '">' + text + '</span>'

def _div():
    return '<div style="border-top:1px solid ' + C_BORDER + ';margin:8px 0"></div>'

def _wrap(body, full_footer=False):
    s  = 'background:' + C_BG + ';padding:15px 13px;'
    s += 'font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",sans-serif'
    return '<div style="' + s + '">' + body + (_footer_full() if full_footer else _footer_mini()) + '</div>'

def _footer_mini():
    out  = '<div style="margin-top:12px;border-top:1px solid ' + C_BORDER + '">'
    out += '<div style="display:flex;align-items:stretch;overflow:hidden">'
    if _IMG_CROP:
        out += '<img src="' + _IMG_CROP + '" style="width:56px;flex-shrink:0;object-fit:cover;object-position:top center">'
    out += '<div style="flex:1;padding:8px 10px;background:' + C_SURFACE + ';display:flex;flex-direction:column;justify-content:center;gap:3px">'
    out += '<div style="font-size:11px;font-weight:700;color:' + C_INK + '">' + AUTHOR_TITLE + '</div>'
    out += '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">'
    out += '<a href="' + AUTHOR_TWURL + '" style="font-size:11px;font-weight:700;color:' + C_BLUE + ';text-decoration:none">𝕏 ' + AUTHOR_TWITTER + '</a>'
    out += '<span style="font-size:11px;color:' + C_MUTED + '">微信 <strong style="color:' + C_INK + '">' + AUTHOR_WECHAT + '</strong></span>'
    out += '</div></div></div></div>'
    return out

def _footer_full():
    out  = '<div style="margin-top:18px;border-top:2px solid ' + C_INK + ';padding-top:14px">'
    if _IMG_FULL:
        out += '<div style="border-radius:10px;overflow:hidden;margin-bottom:10px;border:1px solid ' + C_BORDER2 + '">'
        out += '<img src="' + _IMG_FULL + '" style="width:100%;display:block">'
        out += '<div style="padding:9px 12px;background:' + C_INK + '">'
        out += '<div style="font-size:13px;font-weight:800;color:#fff">' + AUTHOR_TITLE + '</div>'
        out += '<div style="font-size:11px;color:#999;margin-top:2px">' + AUTHOR_BIO + ' · ' + AUTHOR_TAGS + '</div>'
        out += '</div></div>'
    out += '<a href="' + AUTHOR_TWURL + '" style="display:flex;align-items:center;gap:10px;padding:11px 13px;background:' + C_INK + ';border-radius:8px;text-decoration:none;margin-bottom:7px">'
    out += '<div style="width:30px;height:30px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0"><span style="color:' + C_INK + ';font-size:13px;font-weight:900">𝕏</span></div>'
    out += '<div style="flex:1"><div style="font-size:10px;color:#888;margin-bottom:1px">我的推特</div>'
    out += '<div style="font-size:15px;font-weight:800;color:#fff">' + AUTHOR_TWITTER + '</div></div>'
    out += '<span style="color:#444;font-size:12px">▶</span></a>'
    out += '<div style="display:flex;align-items:center;gap:10px;padding:11px 13px;background:' + C_SURFACE + ';border:1px solid ' + C_BORDER2 + ';border-radius:8px">'
    out += '<div style="width:30px;height:30px;border-radius:50%;background:' + C_INK + ';display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:15px">💬</div>'
    out += '<div style="flex:1"><div style="font-size:10px;color:' + C_MUTED + ';margin-bottom:2px">欢迎加我微信</div>'
    out += '<div style="font-size:16px;font-weight:800;color:' + C_INK + ';letter-spacing:.5px">' + AUTHOR_WECHAT + '</div>'
    out += '<div style="font-size:11px;color:' + C_MUTED + ';margin-top:2px">' + AUTHOR_WXNOTE + '</div>'
    out += '</div></div></div>'
    return out

def _masthead(date_str, label, subtitle):
    out  = '<div style="padding-left:11px;border-left:3px solid ' + C_RED + ';margin-bottom:14px">'
    out += '<div style="font-size:9px;font-weight:700;color:' + C_RED + ';letter-spacing:2px;text-transform:uppercase;margin-bottom:3px">Daily Intel · ' + AUTHOR_TWITTER + '</div>'
    out += '<div style="font-size:18px;font-weight:900;color:' + C_INK + ';line-height:1.15;letter-spacing:-.4px">每日科技投资简报</div>'
    out += '<div style="margin-top:5px;display:flex;align-items:center;gap:7px;flex-wrap:wrap">'
    out += '<span style="font-size:11px;color:' + C_MUTED + '">' + date_str + '</span>'
    out += '<span style="font-size:10px;background:' + C_RED + ';color:#fff;padding:1px 8px;border-radius:3px;font-weight:700">' + label + '</span>'
    out += '<span style="font-size:11px;color:' + C_INK2 + ';font-weight:500">' + subtitle + '</span>'
    out += '</div></div>'
    return out

def _md(text, accent=None):
    if accent is None: accent = C_RED
    h = text.strip()
    h = re.sub(r'^##\s+深度[文章]*\d*[：:．.]\s*(.+)$',
               lambda m: '<div style="font-size:14px;font-weight:700;color:' + C_INK + ';line-height:1.4;margin:10px 0 4px">' + m.group(1).strip() + '</div>',
               h, flags=re.M)
    h = re.sub(r'^##\s+(.+)$',
               lambda m: '<div style="font-size:13px;font-weight:700;color:' + C_INK2 + ';margin:8px 0 3px">' + m.group(1) + '</div>',
               h, flags=re.M)
    h = re.sub(r'\*\*今日启示\*\*[：:．.]?\s*(.+)',
               '<div style="background:' + C_RED_BG + ';border-left:3px solid ' + C_RED + ';border-radius:0 4px 4px 0;padding:8px 10px;margin:10px 0 4px;color:' + C_RED + ';font-size:12px;font-weight:600;line-height:1.65">💡 \\1</div>',
               h)
    h = re.sub(r'\*\*来源\*\*[：:](.+?)\s*[|｜]\s*\*\*领域\*\*[：:](.+)',
               lambda m: '<div style="margin:2px 0 6px">' + _tag(m.group(1).strip(), C_MUTED, C_SURF2) + _tag(m.group(2).strip(), *_ds(m.group(2).strip())) + '</div>',
               h)
    h = re.sub(r'\*\*(.+?)\*\*',
               '<strong style="color:' + accent + ';font-weight:700">\\1</strong>', h)
    h = re.sub(r'^>\s+(.+)$',
               '<div style="border-left:2px solid ' + C_BORDER2 + ';padding:4px 9px;color:' + C_MUTED + ';font-size:12px;margin:4px 0">\\1</div>',
               h, flags=re.M)
    h = re.sub(r'\n-{3,}\n', _div(), h)
    out = []
    for ln in h.split('\n'):
        ln = ln.strip()
        if not ln:
            out.append('<div style="height:4px"></div>')
        elif ln.startswith('<'):
            out.append(ln)
        else:
            out.append('<p style="font-size:13px;color:' + C_INK2 + ';line-height:1.82;margin:2px 0">' + ln + '</p>')
    return '\n'.join(out)


# ══════════════════════════════════════════════════
# 消息① 深度长文
# ══════════════════════════════════════════════════
def build_msg1_deep(deep_text, date_str):
    arts = [a.strip() for a in re.split(r'\n-{3,}\n', deep_text)
            if a.strip() and len(a.strip()) > 50]
    cards = []
    for i, art in enumerate(arts[:10], 1):
        tm = (re.search(r'##\s+深度[文章]*\d*[：:．.]\s*(.+)', art)
              or re.search(r'##\s+(.+)', art))
        title  = tm.group(1).strip() if tm else ("文章 " + str(i))
        dm     = re.search(r'\*\*领域\*\*[：:](.+)', art)
        domain = dm.group(1).strip() if dm else ""
        dg, db = _ds(domain) if domain else (C_MUTED, C_SURF2)
        body   = re.sub(r'^##[^\n]+\n', '', art, count=1).strip()
        if len(body) > 950: body = body[:950] + '…'

        card  = '<div style="padding:11px 0;border-bottom:1px solid ' + C_BORDER + '">'
        card += '<div style="display:flex;gap:6px;align-items:flex-start;margin-bottom:5px">'
        card += '<span style="font-size:10px;font-weight:800;color:#fff;background:' + C_RED + ';padding:1px 5px;border-radius:3px;flex-shrink:0;margin-top:2px">' + str(i).zfill(2) + '</span>'
        if domain:
            card += '<span style="font-size:10px;font-weight:600;color:' + dg + ';background:' + db + ';padding:1px 5px;border-radius:3px;flex-shrink:0;margin-top:2px">' + domain + '</span>'
        card += '<span style="font-size:13px;font-weight:700;color:' + C_INK + ';line-height:1.4">' + title + '</span>'
        card += '</div>'
        card += '<div style="font-size:13px;color:' + C_INK2 + ';line-height:1.82">' + _md(body, C_RED) + '</div>'
        card += '</div>'
        cards.append(card)

    meta = '<div style="font-size:11px;color:' + C_MUTED + ';margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid ' + C_BORDER + '">' + str(len(cards)) + ' 篇深度分析 · 每篇约500字</div>'
    body = (_masthead(date_str, "① 深度长文", "10篇分析")
            + meta + ''.join(cards)
            + '<div style="margin-top:9px;text-align:right;font-size:11px;color:' + C_LIGHT + '">导读+快讯见下一条 →</div>')
    return _wrap(body, full_footer=False)


# ══════════════════════════════════════════════════
# 快讯解析（支持新旧两种格式）
# ══════════════════════════════════════════════════
def _parse_briefs(brief_text):
    """解析快讯文本，支持 ===第N条=== 新格式和 **[01] 旧格式"""
    items = []

    # 新格式：===第N条===
    blocks = re.split(r'===第\d+条===', brief_text)
    blocks = [b.strip() for b in blocks if b.strip()]

    if len(blocks) >= 3:
        for block in blocks[:20]:
            dm = re.search(r'领域[：:]\s*(.+)', block)
            tm = re.search(r'标题[：:]\s*(.+)', block)
            bm = re.search(r'正文[：:]\s*([\s\S]+?)(?=启示[：:]|$)', block)
            im = re.search(r'启示[：:]\s*(.+)', block)
            items.append({
                "domain":  dm.group(1).strip() if dm else "",
                "title":   tm.group(1).strip() if tm else "",
                "body":    bm.group(1).strip() if bm else "",
                "insight": im.group(1).strip() if im else "",
            })
    else:
        # 旧格式兼容：按行解析
        lines  = [l.strip() for l in brief_text.split('\n') if l.strip()]
        cur    = []
        raw_blocks = []
        for ln in lines:
            if re.match(r'^\*\*\[?\d+', ln) or re.match(r'^\d{2}\s', ln):
                if cur: raw_blocks.append('\n'.join(cur))
                cur = [ln]
            else:
                cur.append(ln)
        if cur: raw_blocks.append('\n'.join(cur))

        for block in raw_blocks[:20]:
            ins_m   = re.search(r'📌\s*(.+)', block)
            insight = ins_m.group(1).strip() if ins_m else ""
            if ins_m: block = block[:ins_m.start()].strip()
            title_m = re.match(r'\*\*(.+?)\*\*', block)
            title   = title_m.group(1) if title_m else ""
            body    = block[title_m.end():].strip() if title_m else block
            tags    = re.findall(r'\[([^\]]+)\]', title)
            domain  = tags[1] if len(tags) >= 2 else (tags[0] if tags else "")
            clean   = re.sub(r'\[\d+\]\s*|\[[^\]]+\]\s*', '', title).strip()
            items.append({"domain": domain, "title": clean, "body": body, "insight": insight})

    return items


# ══════════════════════════════════════════════════
# 消息② 今日导读 + 快讯简报（合并）
# ══════════════════════════════════════════════════
def build_msg2_combined(header, brief_text, date_str):
    # ── 导读 ──
    kw_m = re.search(r'今日关键词[：:]\s*(.+)', header)
    kw_html = ""
    if kw_m:
        kws    = [k.strip() for k in re.split(r'[·\s·]+', kw_m.group(1)) if k.strip()]
        colors = [C_RED, C_BLUE, C_GREEN, "#6f42c1", "#d9730d"]
        kw_html = '<div style="margin-top:10px;padding-top:9px;border-top:1px solid ' + C_BORDER + '">'
        for i, k in enumerate(kws):
            c = colors[i % len(colors)]
            kw_html += '<span style="display:inline-block;background:' + c + '18;color:' + c + ';font-size:10px;padding:1px 7px;border-radius:8px;margin:1px 3px 1px 0;border:1px solid ' + c + '33;font-weight:600">' + k + '</span>'
        kw_html += '</div>'
        header = header[:kw_m.start()].strip()

    header_rows = []
    for ln in header.split('\n'):
        ln = ln.strip()
        if not ln: continue
        is_b = ln.startswith('•') or ln.startswith('-')
        text = ln.lstrip('•- ').strip()
        text = re.sub(r'\*\*(.+?)\*\*', '<strong style="color:' + C_RED + ';font-weight:700">\\1</strong>', text)
        if is_b:
            row  = '<div style="display:flex;gap:7px;padding:7px 0;border-bottom:1px solid ' + C_BORDER + ';align-items:flex-start">'
            row += '<span style="color:' + C_RED + ';font-size:9px;margin-top:5px;flex-shrink:0;font-weight:700">▶</span>'
            row += '<span style="font-size:13px;color:' + C_INK2 + ';line-height:1.75">' + text + '</span>'
            row += '</div>'
        else:
            row = '<p style="font-size:13px;color:' + C_INK2 + ';line-height:1.82;margin:0 0 7px">' + text + '</p>'
        header_rows.append(row)

    header_block  = _masthead(date_str, "② 今日导读", "要点速览")
    header_block += '<div style="background:' + C_SURFACE + ';border:1px solid ' + C_BORDER + ';border-radius:8px;padding:12px 13px;margin-bottom:14px">'
    header_block += ''.join(header_rows) + kw_html + '</div>'

    # ── 快讯 ──
    items = _parse_briefs(brief_text)
    brief_cards = []
    for i, it in enumerate(items, 1):
        domain = it["domain"]
        dg, db = _ds(domain) if domain else (C_MUTED, C_SURF2)
        title  = re.sub(r'\*\*(.+?)\*\*', '<strong style="color:' + C_INK + '">\\1</strong>', it["title"])
        body   = re.sub(r'\*\*(.+?)\*\*', '<strong style="color:' + C_INK + '">\\1</strong>', it["body"])

        ins_html = ""
        if it["insight"]:
            ins_html  = '<div style="margin-top:4px;padding:4px 8px;background:' + C_GRN_BG + ';'
            ins_html += 'border-radius:4px;color:' + C_GREEN + ';font-size:11px;font-weight:600">'
            ins_html += '📌 ' + it["insight"] + '</div>'

        card  = '<div style="padding:9px 0;border-bottom:1px solid ' + C_BORDER + '">'
        card += '<div style="display:flex;gap:5px;align-items:flex-start;margin-bottom:4px">'
        card += '<span style="font-size:10px;color:' + C_LIGHT + ';font-weight:700;min-width:20px;margin-top:2px;flex-shrink:0;text-align:right">' + str(i).zfill(2) + '</span>'
        if domain:
            card += '<span style="font-size:10px;font-weight:600;color:' + dg + ';background:' + db + ';padding:1px 5px;border-radius:3px;flex-shrink:0;margin-top:2px">' + domain + '</span>'
        card += '<span style="font-size:13px;font-weight:700;color:' + C_INK + ';line-height:1.4">' + title + '</span>'
        card += '</div>'
        card += '<div style="font-size:12px;color:' + C_MUTED + ';line-height:1.78;padding-left:24px">' + body + ins_html + '</div>'
        card += '</div>'
        brief_cards.append(card)

    brief_block  = '<div style="margin-top:4px">'
    brief_block += _masthead(date_str, "② 快讯", str(len(brief_cards)) + "条速览")
    brief_block += '<div style="font-size:11px;color:' + C_MUTED + ';margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid ' + C_BORDER + '">' + str(len(brief_cards)) + ' 条快讯 · 每条约80字</div>'
    brief_block += ''.join(brief_cards) + '</div>'

    return _wrap(header_block + brief_block, full_footer=True)


# ══════════════════════════════════════════════════
# 推送执行
# ══════════════════════════════════════════════════
def _wxp_send(token, uid_list, html, summary):
    r    = requests.post(WXP_API, json={
        "appToken": token, "content": html[:WXP_LIMIT],
        "summary": summary[:100], "contentType": 2, "uids": uid_list,
    }, timeout=20)
    data = r.json()
    ok   = data.get("success") or data.get("code") == 1000
    if not ok: print("    ⚠️  WxPusher: " + str(data.get('msg', data)))
    return ok


def push_wxpusher(header, deep_text, brief_text, date_str, repo_url=""):
    token = os.environ.get("WXPUSHER_APP_TOKEN","")
    uids  = os.environ.get("WXPUSHER_UIDS","")
    if not token or not uids:
        print("  ⏭  WxPusher 未配置"); return False
    uid_list = [u.strip() for u in uids.split(",") if u.strip()]

    msgs = [
        (build_msg1_deep(deep_text, date_str),       "📰 [" + date_str + "] 深度长文 10篇"),
        (build_msg2_combined(header, brief_text, date_str), "📋⚡ [" + date_str + "] 今日导读+快讯"),
    ]
    ok = 0
    for i, (html, summary) in enumerate(msgs):
        try:
            r   = _wxp_send(token, uid_list, html, summary)
            lbl = ["①深度长文", "②导读+快讯"][i]
            print("  " + ("✅" if r else "❌") + " WxPusher " + lbl + " → " + str(len(uid_list)) + " 人")
            if r: ok += 1
        except Exception as e:
            print("  ❌ 消息" + str(i+1) + " 异常: " + str(e))
        if i < 1: time.sleep(1.5)
    return ok > 0


def push_serverchan(header, deep_text, brief_text, date_str):
    key = os.environ.get("SERVERCHAN_KEY","")
    if not key:
        print("  ⏭  Server酱 未配置"); return False
    desp = ("## 今日导读\n" + header + "\n\n"
            "## 深度文章（节选）\n" + deep_text[:2500] + "\n\n"
            "## 快讯（节选）\n" + brief_text[:2000] + "\n\n"
            "---\n*" + date_str + " · " + AUTHOR_TWITTER + " · 微信" + AUTHOR_WECHAT + "*")
    try:
        r    = requests.post(SC_API_TPL.format(key=key),
                             data={"title": "🧠 每日科技简报 · " + date_str,
                                   "desp": desp[:SC_LIMIT]}, timeout=15)
        data = r.json()
        ok   = data.get("data",{}).get("errno")==0 or data.get("code")==0
        print("  " + ("✅" if ok else "❌") + " Server酱 " + ("成功" if ok else str(data)))
        return ok
    except Exception as e:
        print("  ❌ Server酱 异常: " + str(e)); return False


def push_all(header, deep_text, brief_text, date_str, repo_url=""):
    print("\n📤 推送到微信（2条）…")
    wx_ok = push_wxpusher(header, deep_text, brief_text, date_str, repo_url)
    if not wx_ok:
        print("  ⚠️  WxPusher 失败，Server酱 备援…")
    push_serverchan(header, deep_text, brief_text, date_str)
    print("✅ 推送完成\n")