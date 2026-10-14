#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建《量化投资100讲》电子书 —— 单文件网页版阅读器。

用法：
    python3 电子书/build_ebook.py

产物：
    电子书/量化投资100讲.html   自包含的单文件书籍阅读器（封面 / 目录 / 逐章阅读）
"""

import json
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

MD_EXTENSIONS = ["extra", "sane_lists"]

# 每讲的元数据行，移出正文改由章节页眉呈现
META_LINE_RE = re.compile(r"^>\s*(所属模块|建议时长|内容状态)[：:].*$", re.M)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
TIME_HEAD_RE = re.compile(r"^(#{2,4})\s*\d+\s*[–\-—~－至]\s*\d+\s*分钟\s*[：:]\s*", re.M)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
LECTURE_NO_RE = re.compile(r"第\s*(\d+)\s*讲")
MODULE_DIR_RE = re.compile(r"^模块\s*(\d+)\s*[-—－]\s*(.+)$")

md = markdown.Markdown(extensions=MD_EXTENSIONS)


def read_module_descriptions():
    """从总目录中提取每个模块的一句话说明。"""
    toc = ROOT / "量化投资100讲目录.md"
    desc = {}
    if not toc.exists():
        return desc
    lines = toc.read_text(encoding="utf-8").splitlines()
    current = None
    for line in lines:
        m = re.match(r"^#\s*模块\s*(\d+)[：:]\s*(.+?)(?:（.*）)?\s*$", line)
        if m:
            current = int(m.group(1))
            continue
        if current is not None:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#") or s.startswith("---"):
                current = None
                continue
            if s.startswith("[") or s.startswith(">"):
                continue
            desc[current] = s
            current = None
    return desc


def clean_body(text):
    text = COMMENT_RE.sub("", text)
    text = re.sub(r"^\s*<title>.*?</title>\s*$", "", text, flags=re.M)
    text = META_LINE_RE.sub("", text)
    text = TIME_HEAD_RE.sub(r"\1 ", text)
    return text


def md_to_html(text):
    md.reset()
    html = md.convert(text)
    # GFM 任务清单 -> 复选框
    html = re.sub(
        r"<li>\s*\[ \]\s*",
        '<li class="task"><span class="tick"></span>',
        html,
    )
    html = re.sub(
        r"<li>\s*\[[xX]\]\s*",
        '<li class="task done"><span class="tick"></span>',
        html,
    )
    # 站外链接新窗口打开
    html = html.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')
    return html


def fix_links(html, stem_to_no):
    """把指向其它讲次的 .md 链接改为讲次锚点，其余内部 .md 链接改为纯文本。"""
    from urllib.parse import unquote

    def repl(m):
        href, label = m.group("href"), m.group("label")
        if href.startswith(("http", "#", "mailto")):
            return m.group(0)
        stem = unquote(href.split("#")[0].split("/")[-1])
        if stem.endswith(".md"):
            stem = stem[:-3]
        if stem in stem_to_no:
            return '<a class="xref" href="#ch-%d">%s</a>' % (stem_to_no[stem], label)
        if ".md" in href:
            return '<span class="xref-plain">%s</span>' % label
        return m.group(0)

    return re.sub(
        r'<a\b[^>]*?href="(?P<href>[^"]+)"[^>]*?>(?P<label>.*?)</a>', repl, html
    )


def discover():
    descriptions = read_module_descriptions()
    modules = []
    for mod_dir in sorted(ROOT.glob("模块*"), key=lambda p: p.name):
        m = MODULE_DIR_RE.match(mod_dir.name)
        if not m or not mod_dir.is_dir():
            continue
        mod_no = int(m.group(1))
        mod_name = m.group(2).strip()
        chapters = []
        for f in sorted(mod_dir.glob("第*讲-*.md")):
            hit = LECTURE_NO_RE.search(f.name)
            if not hit:
                continue
            chapters.append((int(hit.group(1)), f))
        modules.append(
            {
                "no": mod_no,
                "name": mod_name,
                "desc": descriptions.get(mod_no, ""),
                "files": sorted(chapters, key=lambda x: x[0]),
            }
        )

    stem_to_no = {}
    for mod in modules:
        for n, f in mod["files"]:
            stem_to_no[f.stem] = n

    book = []
    for mod in modules:
        chapters = []
        for n, f in mod["files"]:
            raw = f.read_text(encoding="utf-8")
            body = clean_body(raw)
            h1 = H1_RE.search(raw)
            title = h1.group(1) if h1 else f.stem
            title = LECTURE_NO_RE.sub("", title).strip(" ：:—-")
            chapters.append(
                {
                    "n": n,
                    "title": title,
                    "html": fix_links(md_to_html(body), stem_to_no),
                }
            )
        book.append(
            {
                "no": mod["no"],
                "name": mod["name"],
                "desc": mod["desc"],
                "chapters": chapters,
            }
        )
    return book


CSS = r"""
:root{
  --paper:#f7f3ea; --paper-2:#efe8d9; --paper-3:#e7ddc9;
  --ink:#232019; --ink-soft:#5d564a; --ink-faint:#8b8375;
  --accent:#0e6b5e; --accent-soft:rgba(14,107,94,.12);
  --rule:rgba(35,32,25,.14); --serif:"Songti SC","STSong","Source Han Serif SC","Noto Serif SC",Georgia,serif;
  --sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  --mono:"SF Mono",Menlo,Consolas,"Courier New",monospace;
  --measure:38rem;
}
html[data-theme="night"]{
  --paper:#15171b; --paper-2:#1c1f24; --paper-3:#242830;
  --ink:#e7e4db; --ink-soft:#a8a294; --ink-faint:#767061;
  --accent:#5fd0bd; --accent-soft:rgba(95,208,189,.14);
  --rule:rgba(231,228,219,.14);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--paper); color:var(--ink);
  font-family:var(--serif);
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
}
button{font-family:var(--sans); cursor:pointer}
.view{display:none}
.view.active{display:block}
#view-cover.active{display:flex}
#view-reader.active{display:flex;flex-direction:column;height:100vh;height:100dvh}

/* ---------- 封面 ---------- */
.view-cover{
  min-height:100vh; min-height:100dvh;
  background:
    radial-gradient(circle at 82% 12%,var(--accent-soft),transparent 42%),
    radial-gradient(circle at 12% 88%,var(--accent-soft),transparent 40%),
    var(--paper);
  align-items:center; justify-content:center; padding:6vh 6vw;
}
.cover-inner{width:min(100%,44rem); text-align:center}
.cover-frame{
  border:1px solid var(--rule); border-radius:6px;
  padding:clamp(2.2rem,6vw,4.4rem) clamp(1.4rem,5vw,3.6rem);
  position:relative; background:linear-gradient(180deg,rgba(255,255,255,.35),transparent);
}
.cover-frame::before,.cover-frame::after{
  content:""; position:absolute; width:26px; height:26px; border:1px solid var(--accent); opacity:.55;
}
.cover-frame::before{top:14px;left:14px;border-right:0;border-bottom:0}
.cover-frame::after{bottom:14px;right:14px;border-left:0;border-top:0}
.cover-kicker{
  font-family:var(--sans); font-size:.72rem; letter-spacing:.34em;
  color:var(--accent); text-transform:uppercase; margin-bottom:1.6rem;
}
.cover-title{
  font-size:clamp(2.4rem,7.5vw,4.1rem); line-height:1.12; margin:0;
  font-weight:700; letter-spacing:.02em;
}
.cover-100{color:var(--accent); font-family:var(--sans); font-weight:800}
.cover-rule{width:64px;height:2px;background:var(--accent);margin:1.7rem auto;border-radius:2px}
.cover-sub{font-size:clamp(1.05rem,2.6vw,1.35rem); color:var(--ink-soft); margin:0 0 1.1rem; letter-spacing:.04em}
.cover-desc{
  font-size:.95rem; line-height:2; color:var(--ink-faint); margin:0 auto 2rem; max-width:32rem;
}
.cover-by{font-family:var(--sans);font-size:.86rem;letter-spacing:.16em;color:var(--ink-soft);margin:0 0 1.7rem}
.cover-meta{
  display:flex; flex-wrap:wrap; gap:.5rem 1.4rem; justify-content:center;
  font-family:var(--sans); font-size:.82rem; color:var(--ink-soft); margin-bottom:2.2rem;
}
.cover-meta span{position:relative; padding-left:1rem}
.cover-meta span::before{content:"";position:absolute;left:0;top:50%;width:4px;height:4px;border-radius:50%;background:var(--accent);transform:translateY(-50%)}
.cover-actions{display:flex;gap:.8rem;justify-content:center;flex-wrap:wrap}
.btn{
  font-size:.92rem; padding:.72rem 1.7rem; border-radius:999px;
  border:1px solid var(--rule); background:transparent; color:var(--ink);
  transition:.18s; letter-spacing:.03em;
}
.btn:hover{border-color:var(--accent); color:var(--accent)}
.btn-primary{background:var(--accent); border-color:var(--accent); color:#fff}
.btn-primary:hover{opacity:.9; color:#fff}
.btn-ghost{border-color:transparent;color:var(--ink-soft)}

/* ---------- 目录 ---------- */
.view-toc{min-height:100vh;min-height:100dvh;padding:clamp(2.4rem,6vw,4.5rem) clamp(1.2rem,5vw,2rem) 5rem}
.toc-head{text-align:center;margin-bottom:clamp(2rem,5vw,3.4rem);position:relative}
.toc-head .btn-ghost{position:absolute;left:0;top:0}
.toc-head h2{font-size:clamp(1.7rem,4.5vw,2.5rem);margin:.2rem 0 .5rem;letter-spacing:.16em}
.toc-head-meta{font-family:var(--sans);font-size:.82rem;color:var(--ink-faint);letter-spacing:.1em}
.toc-list{max-width:var(--measure);margin:0 auto}
.toc-mod{margin-bottom:2.6rem;padding-bottom:1.4rem;border-bottom:1px solid var(--rule)}
.toc-mod-head{display:flex;align-items:baseline;gap:.9rem;margin-bottom:.4rem}
.toc-mod-no{
  font-family:var(--sans);font-size:.74rem;font-weight:700;color:var(--accent);
  border:1px solid var(--accent);border-radius:4px;padding:.12rem .5rem;letter-spacing:.08em;white-space:nowrap;
}
.toc-mod-name{font-size:1.25rem;font-weight:700;letter-spacing:.04em}
.toc-mod-desc{font-size:.86rem;color:var(--ink-faint);line-height:1.9;margin:.5rem 0 1rem}
.toc-ch{
  display:flex;gap:.9rem;align-items:baseline;padding:.5rem .6rem;border-radius:6px;
  text-decoration:none;color:var(--ink);transition:.14s;
}
.toc-ch:hover{background:var(--accent-soft)}
.toc-ch .cno{font-family:var(--sans);font-size:.78rem;color:var(--ink-faint);min-width:3.6rem;letter-spacing:.04em}
.toc-ch .ctt{font-size:.98rem;line-height:1.7}

/* ---------- 阅读器 ---------- */
.topbar{
  display:flex;align-items:center;gap:1rem;padding:.7rem clamp(1rem,4vw,1.6rem);
  border-bottom:1px solid var(--rule);background:var(--paper);position:relative;z-index:5;
}
.icon-btn{
  font-family:var(--sans);font-size:.84rem;color:var(--ink-soft);background:transparent;
  border:1px solid transparent;border-radius:6px;padding:.4rem .7rem;transition:.15s;white-space:nowrap;
}
.icon-btn:hover{color:var(--accent);border-color:var(--rule)}
.topbar-title{flex:1;text-align:center;font-family:var(--sans);font-size:.84rem;color:var(--ink-faint);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.topbar-right{display:flex;align-items:center;gap:.4rem}
#read-percent{font-family:var(--sans);font-size:.78rem;color:var(--ink-faint);min-width:2.6rem;text-align:right}
.read-progress{height:2px;background:var(--paper-3);flex:0 0 auto}
.read-progress div{height:100%;width:0;background:var(--accent);transition:width .12s linear}
.reader-scroll{flex:1;overflow-y:auto;overflow-x:hidden}
.page{max-width:var(--measure);margin:0 auto;padding:clamp(2.4rem,6vw,4rem) clamp(1.3rem,5vw,1.6rem) 2rem}

.chapter-opener{text-align:center;padding-bottom:2rem;margin-bottom:2.4rem;border-bottom:1px solid var(--rule)}
.op-module{font-family:var(--sans);font-size:.76rem;letter-spacing:.22em;color:var(--accent);margin-bottom:1.5rem}
.op-no{font-family:var(--sans);font-size:.9rem;color:var(--ink-faint);letter-spacing:.3em;margin-bottom:.6rem}
.op-no b{font-size:1.6rem;color:var(--ink);letter-spacing:0;vertical-align:-.12em}
.op-title{font-size:clamp(1.5rem,4.4vw,2.1rem);line-height:1.45;margin:0;letter-spacing:.02em;font-weight:700}

.chapter-body{font-size:1.06rem;line-height:2.05;letter-spacing:.01em}
.chapter-body h2{
  font-size:1.32rem;margin:2.8rem 0 1rem;padding-left:.85rem;border-left:3px solid var(--accent);
  line-height:1.5;letter-spacing:.03em;
}
.chapter-body h3{font-size:1.1rem;margin:1.9rem 0 .8rem;color:var(--ink-soft);letter-spacing:.02em}
.chapter-body p{margin:1.05rem 0}
.chapter-body strong{font-weight:700;color:var(--ink)}
.chapter-body em{font-style:normal;color:var(--accent)}
.chapter-body a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--accent-soft)}
.chapter-body a:hover{border-bottom-color:var(--accent)}
.xref-plain{color:var(--ink-soft);border-bottom:1px dashed var(--rule)}
.chapter-body ul,.chapter-body ol{padding-left:1.5rem;margin:1rem 0}
.chapter-body li{margin:.45rem 0;line-height:1.95}
.chapter-body li.task{list-style:none;position:relative;padding-left:1.7rem}
.chapter-body li.task .tick{
  position:absolute;left:0;top:.62em;width:1rem;height:1rem;border:1.5px solid var(--ink-faint);
  border-radius:4px;
}
.chapter-body li.task.done .tick{background:var(--accent);border-color:var(--accent)}
.chapter-body blockquote{
  margin:1.5rem 0;padding:1rem 1.3rem;background:var(--paper-2);
  border-left:3px solid var(--accent);border-radius:0 6px 6px 0;color:var(--ink-soft);
}
.chapter-body blockquote p{margin:.35rem 0}
.chapter-body code{
  font-family:var(--mono);font-size:.86em;background:var(--paper-2);
  padding:.14em .42em;border-radius:4px;color:var(--ink);
}
.chapter-body pre{
  background:var(--paper-2);border:1px solid var(--rule);border-radius:8px;
  padding:1.1rem 1.2rem;overflow-x:auto;margin:1.4rem 0;line-height:1.75;
}
.chapter-body pre code{background:transparent;padding:0;font-size:.84rem}
.chapter-body table{
  border-collapse:collapse;width:100%;margin:1.5rem 0;font-size:.92rem;
  font-family:var(--sans);display:block;overflow-x:auto;
}
.chapter-body th,.chapter-body td{border:1px solid var(--rule);padding:.6rem .8rem;text-align:left;line-height:1.7}
.chapter-body th{background:var(--paper-2);font-weight:600}
.chapter-body hr{border:0;border-top:1px solid var(--rule);margin:2.4rem 0}
.chapter-body img{max-width:100%;border-radius:6px}

.chapnav{
  max-width:var(--measure);margin:1.5rem auto 4rem;padding:1.6rem 1.4rem 0;
  border-top:1px solid var(--rule);display:flex;gap:.8rem;
}
.chapnav .btn{flex:1;text-align:center;font-size:.86rem;padding:.7rem .6rem}
.chapnav .btn[disabled]{opacity:.35;cursor:default}
.chapnav .btn[disabled]:hover{border-color:var(--rule);color:var(--ink)}
.chapnav .nav-label{display:block;font-size:.68rem;color:var(--ink-faint);letter-spacing:.12em;margin-bottom:.3rem}
.chapnav .nav-title{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ---------- 侧栏目录 ---------- */
.drawer{
  position:fixed;top:0;left:0;height:100%;width:min(84vw,22rem);z-index:30;
  background:var(--paper);border-right:1px solid var(--rule);
  transform:translateX(-102%);transition:transform .28s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;
}
.drawer.open{transform:none;box-shadow:0 0 40px rgba(0,0,0,.18)}
.drawer-head{
  display:flex;align-items:center;justify-content:space-between;padding:.9rem 1.1rem;
  border-bottom:1px solid var(--rule);font-family:var(--sans);letter-spacing:.14em;color:var(--ink-soft);
}
.drawer-list{overflow-y:auto;padding:1rem 1rem 3rem;flex:1}
.drawer-mod{font-family:var(--sans);font-size:.76rem;color:var(--accent);letter-spacing:.1em;margin:1.2rem .4rem .5rem;font-weight:700}
.drawer-ch{
  display:flex;gap:.6rem;padding:.42rem .5rem;border-radius:6px;text-decoration:none;color:var(--ink-soft);
  font-size:.9rem;line-height:1.6;font-family:var(--sans);
}
.drawer-ch:hover{background:var(--accent-soft);color:var(--ink)}
.drawer-ch.active{background:var(--accent-soft);color:var(--accent)}
.drawer-ch .cno{color:var(--ink-faint);min-width:2.4rem;font-size:.8rem}
.drawer-ch .ctt{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.scrim{
  position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:20;opacity:0;visibility:hidden;transition:.25s;
}
.scrim.open{opacity:1;visibility:visible}

@media(max-width:560px){
  .chapter-body{font-size:1.02rem}
  .topbar-title{font-size:.78rem}
  .toc-head .btn-ghost{position:static;display:block;margin:0 auto 1rem}
}
"""

JS = r"""
const BOOK = JSON.parse(document.getElementById('book-data').textContent);
const flat = [];
const byNo = {};
BOOK.forEach(m => m.chapters.forEach(c => {
  c.moduleNo = m.no; c.moduleName = m.name;
  flat.push(c); byNo[c.n] = c;
}));

const $ = s => document.querySelector(s);
const views = { cover: $('#view-cover'), toc: $('#view-toc'), reader: $('#view-reader') };
const readerScroll = $('#reader-scroll');
let current = null;

/* ---- 主题 ---- */
const THEME_KEY = 'q100:theme';
function applyTheme(t){
  document.documentElement.setAttribute('data-theme', t);
  $('#theme-toggle').textContent = t === 'night' ? '日间' : '夜间';
}
applyTheme(localStorage.getItem(THEME_KEY) || 'day');
$('#theme-toggle').onclick = () => {
  const t = document.documentElement.getAttribute('data-theme') === 'night' ? 'day' : 'night';
  localStorage.setItem(THEME_KEY, t); applyTheme(t);
};

/* ---- 目录渲染 ---- */
function renderTOC(){
  const el = $('#toc-list'); let h = '';
  BOOK.forEach(m => {
    h += '<div class="toc-mod"><div class="toc-mod-head">'
      + '<span class="toc-mod-no">模块 ' + String(m.no).padStart(2,'0') + '</span>'
      + '<span class="toc-mod-name">' + esc(m.name) + '</span></div>';
    if (m.desc) h += '<div class="toc-mod-desc">' + esc(m.desc) + '</div>';
    m.chapters.forEach(c => {
      h += '<a class="toc-ch" href="#ch-' + c.n + '"><span class="cno">第'
        + String(c.n).padStart(3,'0') + '讲</span><span class="ctt">' + esc(c.title) + '</span></a>';
    });
    h += '</div>';
  });
  el.innerHTML = h;

  const d = $('#drawer-list'); let dh = '';
  BOOK.forEach(m => {
    dh += '<div class="drawer-mod">模块 ' + String(m.no).padStart(2,'0') + ' · ' + esc(m.name) + '</div>';
    m.chapters.forEach(c => {
      dh += '<a class="drawer-ch" data-n="' + c.n + '" href="#ch-' + c.n + '"><span class="cno">'
        + String(c.n).padStart(3,'0') + '</span><span class="ctt">' + esc(c.title) + '</span></a>';
    });
  });
  d.innerHTML = dh;
}
function esc(s){ return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

/* ---- 章节渲染 ---- */
function renderChapter(n){
  const c = byNo[n]; if (!c) return;
  current = c;
  const open = '<header class="chapter-opener">'
    + '<div class="op-module">模块 ' + String(c.moduleNo).padStart(2,'0') + ' · ' + esc(c.moduleName) + '</div>'
    + '<div class="op-no">第 <b>' + String(c.n).padStart(3,'0') + '</b> 讲</div>'
    + '<h1 class="op-title">' + esc(c.title) + '</h1>'
    + '</header>';
  $('#page').innerHTML = open + '<div class="chapter-body">' + c.html + '</div>';
  $('#topbar-title').textContent = '第 ' + String(c.n).padStart(3,'0') + ' 讲 · ' + c.title;

  const i = flat.indexOf(c), prev = flat[i-1], next = flat[i+1];
  $('#chapnav').innerHTML =
    '<button class="btn" id="nav-prev" ' + (prev?'':'disabled') + '><span class="nav-label">上一讲</span>'
      + '<span class="nav-title">' + (prev ? esc(prev.title) : '已是第一讲') + '</span></button>'
    + '<button class="btn" id="nav-toc"><span class="nav-label">返回</span><span class="nav-title">目录</span></button>'
    + '<button class="btn" id="nav-next" ' + (next?'':'disabled') + '><span class="nav-label">下一讲</span>'
      + '<span class="nav-title">' + (next ? esc(next.title) : '已是最后一讲') + '</span></button>';
  if (prev) $('#nav-prev').onclick = () => go(prev.n);
  if (next) $('#nav-next').onclick = () => go(next.n);
  $('#nav-toc').onclick = () => location.hash = '#toc';

  document.querySelectorAll('.drawer-ch').forEach(a =>
    a.classList.toggle('active', +a.dataset.n === n));

  readerScroll.scrollTop = 0;
  updateProgress();
  localStorage.setItem('q100:last', n);
}

function updateProgress(){
  const max = readerScroll.scrollHeight - readerScroll.clientHeight;
  const p = max > 0 ? Math.min(100, Math.round(readerScroll.scrollTop / max * 100)) : 0;
  $('#read-progress-bar').style.width = p + '%';
  $('#read-percent').textContent = p + '%';
}
readerScroll.addEventListener('scroll', updateProgress, { passive: true });
window.addEventListener('resize', updateProgress);

/* ---- 视图切换 / 路由 ---- */
function show(name){
  Object.values(views).forEach(v => v.classList.remove('active'));
  views[name].classList.add('active');
}
function go(n){ location.hash = '#ch-' + n; }
function route(){
  const h = location.hash;
  if (h.indexOf('#ch-') === 0){
    const n = parseInt(h.slice(4), 10);
    if (byNo[n]) { show('reader'); renderChapter(n); closeDrawer(); return; }
  }
  if (h === '#toc'){ show('toc'); window.scrollTo(0,0); return; }
  show('cover'); window.scrollTo(0,0);
}
window.addEventListener('hashchange', route);

/* ---- 顶部/封面按钮 ---- */
$('#start-read').onclick = () => {
  const last = +localStorage.getItem('q100:last');
  go(byNo[last] ? last : flat[0].n);
};
$('#goto-toc').onclick = () => location.hash = '#toc';
$('#toc-back').onclick = () => location.hash = '#cover';

/* ---- 侧栏 ---- */
function openDrawer(){ $('#drawer').classList.add('open'); $('#scrim').classList.add('open'); }
function closeDrawer(){ $('#drawer').classList.remove('open'); $('#scrim').classList.remove('open'); }
$('#open-drawer').onclick = openDrawer;
$('#close-drawer').onclick = closeDrawer;
$('#scrim').onclick = closeDrawer;

/* ---- 键盘翻页 ---- */
document.addEventListener('keydown', e => {
  if (!views.reader.classList.contains('active')) return;
  if (e.key === 'Escape') closeDrawer();
  if (e.target.tagName === 'INPUT') return;
  const i = flat.indexOf(current);
  if (e.key === 'ArrowRight' && flat[i+1]) go(flat[i+1].n);
  if (e.key === 'ArrowLeft' && flat[i-1]) go(flat[i-1].n);
});

/* ---- 启动 ---- */
renderTOC();
const last = +localStorage.getItem('q100:last');
if (byNo[last]){
  $('#start-read').textContent = '继续阅读 · 第' + String(last).padStart(3,'0') + '讲';
}
route();
"""

TEMPLATE = r"""<!doctype html>
<html lang="zh-CN" data-theme="day">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="author" content="揖光尘@XQuant-Shop">
<title>量化投资100讲 · 揖光尘@XQuant-Shop</title>
<style>__CSS__</style>
</head>
<body>

<!-- 封面 -->
<section id="view-cover" class="view view-cover active">
  <div class="cover-inner">
    <div class="cover-frame">
      <div class="cover-kicker">Quantitative Investing</div>
      <h1 class="cover-title">量化投资<span class="cover-100">100</span>讲</h1>
      <div class="cover-rule"></div>
      <p class="cover-sub">用代码代替直觉的决策系统</p>
      <p class="cover-desc">从量化世界观、必备数学、数据工程、经典策略、因子投资，到回测评估、风控与组合优化、机器学习与实战落地——一条完整的量化学习路径。</p>
      <p class="cover-by">揖光尘@XQuant-Shop</p>
      <div class="cover-meta">
        <span>11 个模块</span><span>106 讲</span><span>课程讲义 v1.0</span>
      </div>
      <div class="cover-actions">
        <button class="btn btn-primary" id="start-read">开始阅读</button>
        <button class="btn" id="goto-toc">查看目录</button>
      </div>
    </div>
  </div>
</section>

<!-- 目录 -->
<section id="view-toc" class="view view-toc">
  <header class="toc-head">
    <button class="btn btn-ghost" id="toc-back">← 返回封面</button>
    <h2>目录</h2>
    <div class="toc-head-meta">共 11 个模块 · 106 讲</div>
  </header>
  <nav id="toc-list" class="toc-list"></nav>
</section>

<!-- 阅读器 -->
<section id="view-reader" class="view view-reader">
  <div class="topbar">
    <button class="icon-btn" id="open-drawer">☰ 目录</button>
    <div class="topbar-title" id="topbar-title"></div>
    <div class="topbar-right">
      <span id="read-percent">0%</span>
      <button class="icon-btn" id="theme-toggle">夜间</button>
    </div>
  </div>
  <div class="read-progress"><div id="read-progress-bar"></div></div>
  <div class="reader-scroll" id="reader-scroll">
    <article class="page" id="page"></article>
    <nav class="chapnav" id="chapnav"></nav>
  </div>
</section>

<aside id="drawer" class="drawer">
  <div class="drawer-head"><span>目录</span><button class="icon-btn" id="close-drawer">✕</button></div>
  <nav id="drawer-list" class="drawer-list"></nav>
</aside>
<div id="scrim" class="scrim"></div>

<script id="book-data" type="application/json">__BOOK_DATA__</script>
<script>__JS__</script>
</body>
</html>
"""


def main():
    book = discover()
    total = sum(len(m["chapters"]) for m in book)
    data = json.dumps(book, ensure_ascii=False).replace("</", "<\\/")
    html = (
        TEMPLATE.replace("__CSS__", CSS)
        .replace("__BOOK_DATA__", data)
        .replace("__JS__", JS)
    )
    out = HERE / "量化投资100讲.html"
    out.write_text(html, encoding="utf-8")

    # 供 GitHub Pages 发布（仓库 Settings → Pages 的 Source 选 main / docs）
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "index.html").write_text(html, encoding="utf-8")
    (docs / ".nojekyll").write_text("", encoding="utf-8")

    print("模块数：%d，讲数：%d" % (len(book), total))
    print("已生成：%s（%.2f MB）" % (out, out.stat().st_size / 1024 / 1024))
    print("已生成 Pages 版本：%s" % (docs / "index.html"))


if __name__ == "__main__":
    main()
