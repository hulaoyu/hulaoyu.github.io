#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 content/ 里的片段编译成可以直接发布的静态站点。

    python tools/build.py

没有第三方依赖，只用标准库。输出写在站点根目录（index.html、posts/…）。
日常改文章：改 content/posts/*.html 开头那段 meta 和正文，然后重跑一次。
"""

from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import quote

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

SITE = {
    "name": "胡天宇的小站",
    "tagline": "把不好解释的东西，拆成能动手的部分。",
    "tagline_html": "把不好解释的东西，<br>拆成能动手的部分。",
    "desc": "胡天宇的个人站：交互式解释器、前端，和一些没被裁掉的中间过程。",
    "author": "胡天宇",
    "github": "https://github.com/hulaoyu",
    "url": "https://hulaoyu.github.io/hulaoyu-",
    "year": 2026,
}

NAV = [
    ("index.html", "首页", "home"),
    ("projects.html", "作品", "grid"),
    ("categories.html", "分类", "folder"),
    ("tags.html", "标签", "hash"),
    ("archives.html", "归档", "archive"),
    ("about.html", "关于", "user"),
]

ICONS = {
    "home": '<path d="M4 11.2 12 4l8 7.2V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="1.2"/><rect x="13" y="4" width="7" height="7" rx="1.2"/><rect x="4" y="13" width="7" height="7" rx="1.2"/><rect x="13" y="13" width="7" height="7" rx="1.2"/>',
    "folder": '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6h4l2 2.2h7A1.5 1.5 0 0 1 19 9.7v8.8a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 3 18.5z"/>',
    "hash": '<path d="M9.5 4 7.5 20M16.5 4l-2 16M4 9h16M3 15h16"/>',
    "archive": '<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8M10 12h4"/>',
    "user": '<circle cx="12" cy="8" r="3.6"/><path d="M4.5 20.5c.8-3.6 3.9-5.3 7.5-5.3s6.7 1.7 7.5 5.3"/>',
    "search": '<circle cx="11" cy="11" r="6.2"/><path d="m15.8 15.8 4.2 4.2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "up": '<path d="M12 19V6M6 12l6-6 6 6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 3v1.8M12 19.2V21M4.6 4.6l1.3 1.3M18.1 18.1l1.3 1.3M3 12h1.8M19.2 12H21M4.6 19.4l1.3-1.3M18.1 5.9l1.3-1.3"/>',
    "moon": '<path d="M20 14.4A8.4 8.4 0 1 1 9.6 4a6.7 6.7 0 0 0 10.4 10.4z"/>',
    "system": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.6 7 8.4 6 8.4-6"/>',
    "rss": '<path d="M5 19a1.2 1.2 0 1 1 0-2.4A1.2 1.2 0 0 1 5 19zM4 11a9 9 0 0 1 9 9M4 5a15 15 0 0 1 15 15"/>',
    "github": None,  # 用实心图标，单独处理
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v4.5A1.5 1.5 0 0 1 16.5 20h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10"/>',
}

GITHUB_PATH = (
    '<path fill="currentColor" stroke="none" d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 '
    '6.84 9.73.5.1.68-.22.68-.49 0-.24-.01-1.04-.01-1.89-2.78.62-3.37-1.2-3.37-1.2-.45-1.18-'
    '1.11-1.49-1.11-1.49-.9-.63.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-'
    '1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.28 '
    '2.75 1.05a9.36 9.36 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 '
    '2.75 0 3.93-2.34 4.8-4.57 5.05.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.81 0 .27.18.6.69.49A10.02 10.02 '
    '0 0 0 22 12.25C22 6.58 17.52 2 12 2z"/>'
)


def icon(name: str, cls: str = "icon") -> str:
    if name == "github":
        body = GITHUB_PATH
        return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{body}</svg>'
    body = ICONS[name]
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def plain(fragment: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def read_minutes(text: str) -> int:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z0-9_]+", text))
    return max(1, math.ceil(cjk / 380 + words / 220))


def strip_tags(markup: str) -> str:
    return re.sub(r"<[^>]+>", "", markup).strip()


def title_html(title: str) -> str:
    """标题里像 2–6–1 这样的记号不允许在连字符处折行。"""
    return esc(title).replace("2–6–1", '<span class="nowrap">2–6–1</span>')


def load_posts():
    posts = []
    for path in sorted((CONTENT / "posts").glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta([\s\S]*?)-->", raw)
        if not m:
            raise SystemExit(f"{path.name}: 缺少开头的 <!--meta {...} --> 段")
        meta = json.loads(m.group(1).strip())
        body = raw[m.end():].lstrip("\n")
        meta.setdefault("pinned", False)
        meta.setdefault("tags", [])
        meta.setdefault("categories", [meta.get("category", "随笔")])
        meta["body"] = body
        meta["text"] = plain(body)
        meta["minutes"] = read_minutes(meta["text"])
        meta["url"] = f"posts/{meta['slug']}.html"
        meta["iso"] = meta["date"]
        meta["display"] = meta["date"].replace("-", "/")
        posts.append(meta)

    posts.sort(key=lambda p: p["date"], reverse=True)
    posts.sort(key=lambda p: not p["pinned"])
    return posts


POSTS = load_posts()


def taxonomies():
    cats, tags = {}, {}
    for p in POSTS:
        for c in p["categories"]:
            cats.setdefault(c, []).append(p)
        for t in p["tags"]:
            tags.setdefault(t, []).append(p)
    ordered_tags = dict(sorted(tags.items(), key=lambda kv: (-len(kv[1]), kv[0])))
    ordered_cats = dict(sorted(cats.items(), key=lambda kv: (-len(kv[1]), kv[0])))
    return ordered_cats, ordered_tags


CATS, TAGS = taxonomies()


def top_tags(n=7):
    return list(TAGS.items())[:n]


# --------------------------------------------------------------------------- #
# 片段
# --------------------------------------------------------------------------- #
def theme_boot() -> str:
    return """<script>
  (function () {
    var p = 'system';
    try { p = localStorage.getItem('theme-pref') || 'system'; } catch (e) {}
    var dark = p === 'dark' || (p === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    var r = document.documentElement;
    r.dataset.theme = dark ? 'dark' : 'light';
    r.dataset.themePref = p;
  })();
</script>"""


def page_head(title, desc, rel, canonical, extra=""):
    full_title = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(SITE['author'])}">
<meta name="theme-color" content="#fbf9f4">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE['name'])}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(SITE['url'])}/assets/img/preview.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel}assets/img/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE['name'])}" href="{rel}feed.xml">
<link rel="stylesheet" href="{rel}assets/css/site.css">
{theme_boot()}{extra}"""


def sidebar(active, rel):
    items = []
    for href, label, ic in NAV:
        current = ' aria-current="page"' if label == active else ""
        items.append(
            f'<li><a href="{rel}{href}"{current}>{icon(ic, "icon")}{label}</a></li>'
        )
    nav = "\n        ".join(items)
    return f"""<aside class="sidebar" id="sidebar">
  <div class="brand">
    <a class="avatar" href="{rel}index.html" aria-label="{esc(SITE['name'])} 首页">
      <img src="{rel}assets/img/avatar.svg" alt="{esc(SITE['author'])}的头像" width="104" height="104">
    </a>
    <div>
      <p class="site-name"><a href="{rel}index.html">{esc(SITE['name'])}</a></p>
      <p class="site-tagline">{SITE['tagline_html']}</p>
      <p class="site-meta">PORTFOLIO / NOTES / {SITE['year']}</p>
    </div>
  </div>

  <nav class="nav" aria-label="站点导航">
    <ul>
        {nav}
    </ul>
  </nav>

  <div class="sidebar-foot">
    <div class="theme-switch" role="group" aria-label="配色">
      <button type="button" data-theme-set="light" aria-pressed="false" aria-label="浅色" title="浅色">{icon("sun")}</button>
      <button type="button" data-theme-set="dark" aria-pressed="false" aria-label="深色" title="深色">{icon("moon")}</button>
      <button type="button" data-theme-set="system" aria-pressed="true" aria-label="跟随系统" title="跟随系统">{icon("system")}</button>
    </div>
    <p class="theme-label">浅色 / 深色 / 跟随系统</p>

    <div class="socials">
      <a class="icon-btn" href="{SITE['github']}" target="_blank" rel="noopener noreferrer" aria-label="GitHub">{icon("github")}</a>
      <a class="icon-btn" href="{rel}feed.xml" aria-label="RSS 订阅">{icon("rss")}</a>
      <a class="icon-btn" href="{rel}about.html" aria-label="关于">{icon("user")}</a>
    </div>

    <p class="colophon">
      © {SITE['year']} {esc(SITE['author'])} · 保留部分权利<br>
      无追踪 · 无外部依赖<br>
      <a href="{rel}about.html">关于这个站</a>
    </p>
  </div>
</aside>"""


def topbar(rel, crumb_parts, current=""):
    crumbs = [f'<a href="{rel}index.html">首页</a>']
    for label, href in crumb_parts:
        if href:
            cls = ' class="cat"' if "categories.html" in href else ""
            crumbs.append(f'<a href="{href}"{cls}>{esc(label)}</a>')
        else:
            crumbs.append(f'<span class="here" aria-current="page">{esc(label)}</span>')
    sep = '<span class="sep">/</span>'
    return f"""<header class="topbar">
  <button class="icon-btn menu-btn" id="menuBtn" type="button" aria-label="打开导航" aria-controls="sidebar" aria-expanded="false">
    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
  </button>
  <div class="crumbs">{sep.join(crumbs)}</div>
  <div class="topbar-actions">
    <button class="search-hint" type="button" data-search-open aria-label="搜索（快捷键 /）">
      {icon("search", "icon")}<span>搜索</span><kbd>/</kbd>
    </button>
    <a class="icon-btn" href="{SITE['github']}" target="_blank" rel="noopener noreferrer" aria-label="GitHub">{icon("github")}</a>
    <a class="icon-btn" href="{rel}feed.xml" aria-label="RSS">{icon("rss")}</a>
  </div>
</header>"""


def recent_items(rel, limit=3):
    lines = []
    for p in POSTS[:limit]:
        lines.append(
            f'<li><a href="{rel}{p["url"]}"><span class="when">{p["display"]}</span>{esc(p["title"])}</a></li>'
        )
    return "\n        ".join(lines)


def tag_links(rel, limit=7):
    links = []
    for name, items in top_tags(limit):
        links.append(
            f'<a href="{rel}tags.html#tag={quote(name)}">{esc(name)}<span class="n">{len(items)}</span></a>'
        )
    return "\n        ".join(links)


def sidebar_footer(rel):
    return f"""<footer class="site-foot">
  <div class="foot-widgets">
    <section>
      <h2>最近更新</h2>
      <ul class="foot-list">
        {recent_items(rel)}
      </ul>
    </section>
    <section>
      <h2>热门标签</h2>
      <div class="foot-tags">
        {tag_links(rel)}
      </div>
      <div class="foot-list" style="margin-top:1rem">
        <a href="{rel}feed.xml">RSS 订阅 {icon("rss", "icon")}</a>
      </div>
    </section>
  </div>

  <div class="foot-base">
    <span>© {SITE['year']} {esc(SITE['author'])} · 保留部分权利</span>
    <span>本站无追踪、无外部请求 · 基于 <a href="{rel}about.html#colophon">Chirpy 的版式</a></span>
  </div>
</footer>"""


def search_dialog(rel):
    return f"""<dialog class="search-dialog" id="searchDialog" aria-label="站内搜索">
  <div class="search-field">
    {icon("search", "icon")}
    <input id="searchInput" type="search" placeholder="搜索文章、标签…" autocomplete="off" spellcheck="false" aria-label="搜索关键词">
    <kbd>Esc</kbd>
  </div>
  <ul class="search-results" id="searchResults"></ul>
  <div class="search-foot">
    <span>↑↓ 选择</span><span>Enter 打开</span><span>/ 唤起 · Esc 关闭</span>
  </div>
</dialog>"""


def page(title, desc, body, rel="", active="", crumb=(), body_class="", path=""):
    canonical = f"{SITE['url']}/{path}".rstrip("/")
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light" data-root="{rel}">
<head>
{page_head(title, desc, rel, canonical)}
</head>
<body{f' class="{body_class}"' if body_class else ''}>
<a class="skip-link" href="#main">跳到正文</a>
<div class="progress" id="progress" aria-hidden="true"></div>

{sidebar(active, rel)}

<div class="main">
{topbar(rel, crumb)}
  <main class="content" id="main">
{body}
{sidebar_footer(rel)}
  </main>
</div>

<div class="backdrop" id="backdrop"></div>
<button class="to-top" id="toTop" type="button" aria-label="回到顶部">{icon("up")}</button>

{search_dialog(rel)}

<script src="{rel}assets/data/posts.js"></script>
<script src="{rel}assets/js/site.js" defer></script>
</body>
</html>
"""


def chip(name, kind, rel):
    if kind == "tag":
        href = f'{rel}tags.html#tag={quote(name)}'
        prefix = '<span class="hash">#</span>'
    else:
        href = f'{rel}categories.html#cat={quote(name)}'
        prefix = ""
    return f'<a class="chip" href="{href}">{prefix}{esc(name)}</a>'


def post_item(p, rel, heading="h2"):
    cats = " / ".join(esc(c) for c in p["categories"])
    pin = '<span class="pin">置顶</span>' if p.get("pinned") else ""
    return f"""<article class="post-item">
  <{heading}>{pin}<a href="{rel}{p['url']}">{title_html(p['title'])}</a></{heading}>
  <p class="meta">
    <time datetime="{p['iso']}">{p['display']}</time>
    <span class="dot">·</span>
    <span>{cats}</span>
    <span class="dot">·</span>
    <span>约 {p['minutes']} 分钟</span>
  </p>
  <p class="excerpt">{esc(p['excerpt'])}</p>
  <a class="read-more" href="{rel}{p['url']}">继续阅读 {icon("arrow", "icon")}</a>
</article>"""


# --------------------------------------------------------------------------- #
# 页面
# --------------------------------------------------------------------------- #
def build_index():
    body = f"""<div class="page-head">
  <p class="eyebrow">POSTS · {SITE['year']}</p>
  <h1>{esc(SITE['name'])}</h1>
  <p class="lede">{esc(SITE['desc'])}</p>
</div>

<div class="post-list">
  {chr(10).join(post_item(p, '') for p in POSTS)}
</div>"""
    out = page(SITE["name"], SITE["desc"], body, rel="", active="首页", crumb=(), path="")
    (ROOT / "index.html").write_text(out, encoding="utf-8")


def build_toc(body):
    heads = re.findall(r'<h([23])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', body, flags=re.S)
    if not heads:
        return ""
    lis = []
    for level, hid, raw in heads:
        title = strip_tags(raw)
        title = re.sub(r"^§\s*", "", title)
        lis.append(
            f'<li class="lvl-{level}"><a href="#{hid}">{esc(title)}</a></li>'
        )
    return f"""<aside class="toc" aria-label="文章目录">
  <p class="toc-title">目录</p>
  <ol>
    {''.join(lis)}
  </ol>
</aside>"""


def build_posts():
    out_dir = ROOT / "posts"
    out_dir.mkdir(exist_ok=True)
    for i, p in enumerate(POSTS):
        rel = "../"
        newer = POSTS[i - 1] if i > 0 else None
        older = POSTS[i + 1] if i + 1 < len(POSTS) else None

        pager = ""
        if newer or older:
            left = ""
            right = ""
            if newer:
                left = f'<a class="prev" href="{rel}{newer["url"]}"><span class="dir">← 更新一篇</span><span class="ttl">{esc(newer["title"])}</span></a>'
            else:
                left = '<span class="placeholder"></span>'
            if older:
                right = f'<a class="next" href="{rel}{older["url"]}"><span class="dir">更早一篇 →</span><span class="ttl">{esc(older["title"])}</span></a>'
            pager = f'<nav class="pager" aria-label="上下篇">{left}{right}</nav>'

        cats = "".join(chip(c, "cat", rel) for c in p["categories"])
        tags = "".join(chip(t, "tag", rel) for t in p["tags"])
        toc = build_toc(p["body"])
        article = f"""<div class="post-layout">
  <article class="article">
    <header class="article-head">
      <div class="cats">{cats}</div>
      <h1>{title_html(p['title'])}</h1>
      <p class="meta">
        <time datetime="{p['iso']}">{p['display']}</time>
        <span class="dot">·</span>
        <span>约 {p['minutes']} 分钟</span>
      </p>
    </header>

    <div class="prose">
{p['body']}
    </div>

    <footer class="article-foot">
      <span class="label">标签</span>
      <div class="tags">{tags}</div>
      {pager}
    </footer>
  </article>

  {toc}
</div>"""
        body = article.replace("%rel%", rel)
        html_page = page(
            p["title"],
            p["excerpt"],
            body,
            rel=rel,
            active="",
            crumb=[(p["categories"][0], f"{rel}categories.html#cat={quote(p['categories'][0])}"), (p["title"], None)],
            path=p["url"],
        )
        (out_dir / f"{p['slug']}.html").write_text(html_page, encoding="utf-8")


def build_categories():
    if not CATS:
        return
    first = next(iter(CATS))
    body = [f"""<div class="page-head">
  <p class="eyebrow">分类 · {len(CATS)} 个</p>
  <h1>按分类翻</h1>
  <p class="lede">文章不多，分类就设得粗一点。点一个分类，只看这一类的篇目。</p>
</div>

<div id="filterBar" class="filter-bar" hidden>
  <span data-filter-label>分类</span>
  <span class="muted" data-filter-count></span>
  <a href="categories.html">显示全部</a>
</div>

<div class="cloud">
  {''.join(f'<a href="#cat={quote(c)}">{esc(c)}<span class="n">{len(items)}</span></a>' for c, items in CATS.items())}
</div>"""]

    for c, items in CATS.items():
        rows = "".join(
            f'<a href="{p["url"]}"><time datetime="{p["iso"]}">{p["date"][5:].replace("-", "/")}</time><span class="ttl">{esc(p["title"])}</span></a>'
            for p in items
        )
        body.append(
            f"""<section class="tax-section" data-filter-group="cat" data-filter-value="{esc(c)}">
  <h2>{esc(c)} <span class="count">{len(items)} 篇</span></h2>
  <div class="tax-list">
    {rows}
  </div>
</section>"""
        )

    body.append('<p id="filterEmpty" hidden class="muted" style="margin-top:2rem">没有这个分类。</p>')
    out = page("分类", "按分类浏览小站里的文章。", "\n".join(body), active="分类", crumb=[("分类", None)], path="categories.html")
    (ROOT / "categories.html").write_text(out, encoding="utf-8")


def build_tags():
    if not TAGS:
        return
    top = max(len(items) for items in TAGS.values())
    cloud = []
    for name, items in TAGS.items():
        size = min(4, max(1, round(len(items) / top * 4)))
        cloud.append(f'<a href="#tag={quote(name)}" data-size="{size}">{esc(name)}<span class="n">{len(items)}</span></a>')

    body = [f"""<div class="page-head">
  <p class="eyebrow">标签 · {len(TAGS)} 个</p>
  <h1>按标签找</h1>
  <p class="lede">标签比分类细，也更容易交叉。字越大，写得越多。</p>
</div>

<div id="filterBar" class="filter-bar" hidden>
  <span data-filter-label>标签</span>
  <span class="muted" data-filter-count></span>
  <a href="tags.html">显示全部</a>
</div>

<div class="cloud">
  {''.join(cloud)}
</div>"""]

    for name, items in TAGS.items():
        rows = "".join(
            f'<a href="{p["url"]}"><time datetime="{p["iso"]}">{p["display"]}</time><span class="ttl">{esc(p["title"])}</span></a>'
            for p in items
        )
        body.append(
            f"""<section class="tax-section" data-filter-group="tag" data-filter-value="{esc(name)}">
  <h2><span class="hash" style="color:var(--faint)">#</span>{esc(name)} <span class="count">{len(items)} 篇</span></h2>
  <div class="tax-list">
    {rows}
  </div>
</section>"""
        )

    body.append('<p id="filterEmpty" hidden class="muted" style="margin-top:2rem">没有这个标签。</p>')
    out = page("标签", "按标签浏览小站里的文章。", "\n".join(body), active="标签", crumb=[("标签", None)], path="tags.html")
    (ROOT / "tags.html").write_text(out, encoding="utf-8")


def build_archives():
    by_year = {}
    for p in POSTS:
        by_year.setdefault(p["date"][:4], []).append(p)

    chunks = [f"""<div class="page-head">
  <p class="eyebrow">归档 · {len(POSTS)} 篇</p>
  <h1>全部文章</h1>
  <p class="lede">从最近的一篇往前翻。目前一共 {len(POSTS)} 篇，都是自己写的。</p>
</div>"""]

    total = len(POSTS)
    for year in sorted(by_year, reverse=True):
        items = by_year[year]
        rows = "".join(
            f'<a href="{p["url"]}"><time datetime="{p["iso"]}">{p["date"][5:].replace("-", "/")}</time><span class="ttl">{esc(p["title"])}</span></a>'
            for p in items
        )
        chunks.append(
            f"""<p class="year">{year}</p>
<div class="group-head">{len(items)} 篇</div>
<div class="tax-list">
  {rows}
</div>"""
        )

    out = page("归档", f"按时间排列的全部文章，共 {total} 篇。", "\n".join(chunks), active="归档", crumb=[("归档", None)], path="archives.html")
    (ROOT / "archives.html").write_text(out, encoding="utf-8")


def build_simple(name, title, desc, active, file_name, rel=""):
    raw = (CONTENT / file_name).read_text(encoding="utf-8")
    body = raw.replace("%rel%", rel)
    out = page(title, desc, body, rel=rel, active=active, crumb=[(title, None)], path=name)
    (ROOT / name).write_text(out, encoding="utf-8")


def build_404():
    body = f"""<div class="notfound">
  <p class="code">404</p>
  <h1>这一页不存在。</h1>
  <p>链接可能写错了，或者这篇文章被挪走了。站里目前有 {len(POSTS)} 篇，去首页或者归档里翻翻看。</p>
  <div class="links">
    <a href="index.html">回首页</a>
    <a href="archives.html">看归档</a>
    <a href="tags.html">按标签找</a>
  </div>
</div>"""
    out = page("页面不存在", "抱歉，这个地址没有对应的页面。", body, active="", crumb=[("404", None)], path="404.html")
    (ROOT / "404.html").write_text(out, encoding="utf-8")


def build_data():
    data_dir = ROOT / "assets" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "title": p["title"],
            "url": p["url"],
            "date": p["display"],
            "categories": p["categories"],
            "tags": p["tags"],
            "excerpt": p["excerpt"],
            "body": p["text"],
        }
        for p in POSTS
    ]
    js = "window.SITE_POSTS = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    (data_dir / "posts.js").write_text(js, encoding="utf-8")


def build_feed():
    import email.utils
    from datetime import datetime, timezone

    items = []
    for p in POSTS:
        dt = datetime.strptime(p["date"], "%Y-%m-%d").replace(hour=9, tzinfo=timezone.utc)
        link = f"{SITE['url']}/{p['url']}"
        items.append(
            f"""  <item>
    <title>{esc(p['title'])}</title>
    <link>{esc(link)}</link>
    <guid isPermaLink="true">{esc(link)}</guid>
    <pubDate>{email.utils.format_datetime(dt)}</pubDate>
    <category>{esc(p['categories'][0])}</category>
    <description>{esc(p['excerpt'])}</description>
  </item>"""
        )

    now = email.utils.format_datetime(datetime.now(timezone.utc))
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{esc(SITE['name'])}</title>
  <link>{esc(SITE['url'])}/</link>
  <description>{esc(SITE['desc'])}</description>
  <language>zh-CN</language>
  <lastBuildDate>{now}</lastBuildDate>
  <atom:link href="{esc(SITE['url'])}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
</channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")


def build_sitemap():
    urls = ["", "projects.html", "categories.html", "tags.html", "archives.html", "about.html"] + [p["url"] for p in POSTS]
    rows = "\n".join(
        f"  <url><loc>{esc(SITE['url'])}/{u}</loc></url>" for u in urls
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{rows}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")


def main():
    build_index()
    build_posts()
    build_categories()
    build_tags()
    build_archives()
    build_simple("projects.html", "作品", "两件作品：一台会学习的机器，和一个由对话搭起来的站。", "作品", "projects.html")
    build_simple("about.html", "关于", "关于胡天宇：交互式解释器、前端，和这个站为什么长这样。", "关于", "about.html")
    build_404()
    build_data()
    build_feed()
    build_sitemap()
    print(f"built {len(POSTS)} posts, {len(CATS)} categories, {len(TAGS)} tags -> {ROOT}")


if __name__ == "__main__":
    main()
