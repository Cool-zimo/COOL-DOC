#!/usr/bin/env python3
"""
COOL-DOC 站点生成器。

设计要点
--------
1. 目录式 URL：al/getting-started/index.html → /COOL-DOC/zh/al/getting-started/
   用户要「COOL-DOC/al/文档名」这种好跳转的链接，所以不用 .html 后缀。

2. 双语：zh/ 与 en/ 两套完整结构，页面顶部可切换。
   另外为 /COOL-DOC/al/xxx/ 生成自动跳转页，让不带语言段的链接也能用。

3. 正文是 Markdown，在这里用 mistune 转成真 HTML 再写文件。
   绝不能把 Markdown 原样塞进 .html —— 引擎不会转换，用户看到的是带井号的源码。

4. 侧边栏目录、上下页、锚点 id 全部自动生成。

路径说明
--------
三个层级的 depth 不同，相对前缀必须分别算，不能共用一个 up：

    zh/index.html                    depth=1  root='../'
    zh/al/index.html                 depth=2  root='../../'
    zh/al/getting-started/index.html depth=3  root='../../../'

此外：
    文档页回应用首页/同级页要用 '../'，不能用 root
    语言切换 = root + 另一语言 + 子路径
"""
import os, re, json, shutil, html as H

try:
    import mistune
except ImportError:
    raise SystemExit('需要 mistune：pip install mistune')

ROOT = '/data/workspace/cooldoc'
OUT = os.environ.get('CD_OUT') or os.path.join(ROOT, 'dist')
CSS = open(os.path.join(ROOT, 'css.tpl'), encoding='utf-8').read()

LANGS = ('zh', 'en')
LANG_NAME = {'zh': '中文', 'en': 'English'}
OTHER = {'zh': 'en', 'en': 'zh'}

SITE = {
    'zh': {
        'tagline': 'Cool-zimo 全部项目的文档',
        'home': '首页', 'allProjects': '全部项目', 'onThisPage': '本页目录',
        'prev': '上一页', 'next': '下一页',
        'updated': '最后更新', 'backHome': '返回文档首页',
        'readMore': '阅读', 'allDocs': '全部文档',
    },
    'en': {
        'tagline': 'Docs for every Cool-zimo project',
        'home': 'Home', 'allProjects': 'All projects', 'onThisPage': 'On this page',
        'prev': 'Previous', 'next': 'Next',
        'updated': 'Last updated', 'backHome': 'Back to docs home',
        'readMore': 'Read', 'allDocs': 'All docs',
    },
}

# 代码块走 pygments 高亮：API 参考、格式规范里有大段代码，不着色很难读。
# 深色底配浅色高亮主题（monokai）。
try:
    from pygments import highlight as _hl
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import HtmlFormatter

    class _HL(mistune.HTMLRenderer):
        def block_code(self, code, info=None):
            lang = (info or '').strip().split()[0] if info else ''
            try:
                lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
            except Exception:
                lexer = TextLexer()
            try:
                body = _hl(code, lexer, HtmlFormatter(nowrap=True))
            except Exception:
                body = H.escape(code)
            return f'<pre><code class="language-{H.escape(lang or "text")}">{body}</code></pre>\n'

    md = mistune.create_markdown(renderer=_HL(escape=False), plugins=['table'])
    PYG_CSS = HtmlFormatter(style='monokai').get_style_defs('.doc pre code')
except ImportError:
    md = mistune.create_markdown(escape=False, plugins=['table'])
    PYG_CSS = ''
    print('提示：未装 pygments，代码块不高亮（pip install pygments）')


def slugify(text):
    s = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', text.strip())
    return (s.replace(' ', '-').lower() or 'sec')


def add_ids(mdhtml):
    out = []
    for line in mdhtml.split('\n'):
        m = re.match(r'^<h([23])>(.*?)</h\1>$', line.strip())
        if m:
            lvl, inner = m.group(1), m.group(2)
            text = H.unescape(re.sub(r'<[^>]+>', '', inner))
            out.append(f'<h{lvl} id="{slugify(text)}">{inner}</h{lvl}>')
        else:
            out.append(line)
    return '\n'.join(out)


def toc_of(mdhtml):
    """提取 h2/h3 做本页目录。

    必须兼容 <h2 id="..."> —— 调用点在 add_ids 之后，标题上已经带 id 了。
    只匹配裸 <h2> 的话目录永远为空，而且不报错，很难发现。
    """
    items = []
    for line in mdhtml.split('\n'):
        m = re.match(r'^<h([23])(?:\s+id="[^"]*")?>(.*?)</h\1>$', line.strip())
        if m:
            lvl = int(m.group(1))
            text = H.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
            items.append((lvl, text, slugify(text)))
    return items


def esc(s):
    return H.escape(str(s), quote=True)


def _sidebar(lang, app, app_list, toc, root_up, level_up):
    """侧边栏：项目列表 + 可选的本页目录"""
    L = SITE[lang]
    nav = ''.join(
        f'<a class="{"on" if a["slug"] == app else ""}" href="{root_up}{a["slug"]}/">'
        f'{esc(a["title"][lang])}</a>' for a in app_list)
    toc_html = ''
    if len(toc) > 1:
        lis = ''.join(
            f'<a href="#{sid}" style="padding-left:{10 if lvl == 2 else 24}px;'
            f'font-size:{13 if lvl == 2 else 12.5}px">{esc(t)}</a>'
            for lvl, t, sid in toc)
        toc_html = f'<div class="app-t">{esc(L["onThisPage"])}</div>{lis}'
    return (f'<a class="home" href="{root_up}">🏠 {esc(L["backHome"])}</a>'
            f'<div class="app-t">{esc(L["allProjects"])}</div>{nav}{toc_html}')


def _langbar(lang, root_up, sub):
    """语言切换。sub 是语言之后的子路径，如 'al/getting-started/'"""
    o = OTHER[lang]
    return ('<div class="lang">'
            f'<a class="{"on" if lang == "zh" else ""}" href="{root_up}zh/{sub}">中</a>'
            f'<a class="{"on" if lang == "en" else ""}" href="{root_up}en/{sub}">EN</a>'
            '</div>')


SHELL = """<!DOCTYPE html>
<html lang="{htmllang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>📚</text></svg>">
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="top">
  <button class="menu-btn" id="mbtn" aria-label="menu">☰</button>
  <a class="brand" href="{brand}"><span class="lg">📚</span>COOL-DOC<small>{tagline}</small></a>
  <div class="top-sp"></div>
  {langbar}
</header>
<div class="scrim" id="scrim"></div>
<div class="wrap">
  <nav class="side" id="side">{sidebar}</nav>
  <main class="main">
{body}
  </main>
</div>
<footer>
  COOL-DOC · <a href="https://github.com/Cool-zimo/COOL-DOC">GitHub</a> ·
  <a href="https://cool-zimo.github.io/">作者主页</a>
</footer>
<script>
(function(){{
  var b=document.getElementById('mbtn'),s=document.getElementById('side'),
      c=document.getElementById('scrim');
  function close(){{s.classList.remove('on');c.classList.remove('on');}}
  b.onclick=function(){{var on=s.classList.toggle('on');c.classList.toggle('on',on);}};
  c.onclick=close;
  s.addEventListener('click',function(e){{
    if(e.target.tagName==='A'&&innerWidth<900) close(); }});
}})();
</script>
</body>
</html>
"""


def _render(lang, title, desc, css, brand, langbar, sidebar, body):
    return SHELL.format(
        htmllang='zh-CN' if lang == 'zh' else 'en',
        title=esc(title), desc=esc(desc), css=css, brand=brand,
        tagline=esc(SITE[lang]['tagline']), langbar=langbar,
        sidebar=sidebar, body=body)


def page_html(lang, app, appname, page, body_html, prevp, nextp, app_list):
    """文档页。位于 zh/al/<slug>/index.html，depth=3"""
    L = SITE[lang]
    root = '../../../'
    toc = toc_of(body_html)
    sidebar = _sidebar(lang, app, app_list, toc, root, '../')
    langbar = _langbar(lang, root, f'{app}/{page["slug"]}/')

    pager = ''
    if prevp or nextp:
        a = (f'<a href="../{prevp["slug"]}/"><small>← {esc(L["prev"])}</small>'
             f'<b>{esc(prevp["title"][lang])}</b></a>') if prevp else \
            '<a style="visibility:hidden"></a>'
        b = (f'<a class="next" href="../{nextp["slug"]}/"><small>{esc(L["next"])} →</small>'
             f'<b>{esc(nextp["title"][lang])}</b></a>') if nextp else ''
        if b:
            pager = f'<div class="pager">{a}{b}</div>'
        elif prevp:
            pager = f'<div class="pager">{a}<a style="visibility:hidden"></a></div>'

    body = f"""    <div class="crumb"><a href="{root}">COOL-DOC</a><span>/</span>
      <a href="../">{esc(appname[lang])}</a><span>/</span>{esc(page['title'][lang])}</div>
    <article class="doc">
      <h1>{esc(page['title'][lang])}</h1>
      <p class="lead">{esc(page.get('desc', {}).get(lang, ''))}</p>
      {body_html}
      {pager}
    </article>"""

    return _render(lang,
                   f'{page["title"][lang]} · {appname[lang]} · COOL-DOC',
                   page.get('desc', {}).get(lang, ''),
                   root + 'assets/style.css', root, langbar, sidebar, body)


def app_index_html(lang, app, appname, pages, app_list, app_desc):
    """应用首页。位于 zh/al/index.html，depth=2"""
    L = SITE[lang]
    root = '../../'
    sidebar = _sidebar(lang, app, app_list, [], root, './')
    langbar = _langbar(lang, root, f'{app}/')
    cards = ''.join(
        f'<a class="card" href="{p["slug"]}/"><b>{esc(p["title"][lang])}</b>'
        f'<span>{esc(p.get("desc", {}).get(lang, ""))}</span>'
        f'<span class="go">{esc(L["readMore"])} →</span></a>' for p in pages)
    body = f"""    <div class="crumb"><a href="{root}">COOL-DOC</a><span>/</span>{esc(appname[lang])}</div>
    <article class="doc">
      <h1>{esc(appname[lang])}</h1>
      <p class="lead">{esc(app_desc.get(lang, ''))}</p>
      <div class="cards">{cards}</div>
    </article>"""
    return _render(lang, f'{appname[lang]} · COOL-DOC', app_desc.get(lang, ''),
                   root + 'assets/style.css', root, langbar, sidebar, body)


def home_html(lang, app_list):
    """语言首页。位于 zh/index.html，depth=1"""
    L = SITE[lang]
    root = '../'
    sidebar = _sidebar(lang, None, app_list, [], root, './')
    langbar = _langbar(lang, root, '')
    cards = ''.join(
        f'<a class="card" href="{a["slug"]}/"><b>{esc(a["title"][lang])}</b>'
        f'<span>{esc(a["desc"][lang])}</span>'
        f'<span class="go">{esc(L["readMore"])} →</span></a>' for a in app_list)
    body = f"""    <article class="doc">
      <h1>COOL-DOC</h1>
      <p class="lead">{esc(L['tagline'])} · {'中英双语' if lang == 'zh' else 'Bilingual'}</p>
      <div class="cards">{cards}</div>
    </article>"""
    return _render(lang, f'COOL-DOC · {L["tagline"]}', L['tagline'],
                   root + 'assets/style.css', root, langbar, sidebar, body)


def redirect_html(target):
    """无语言前缀的跳转页，让 /COOL-DOC/al/xxx/ 也能用"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url={esc(target)}">
<script>location.replace({json.dumps(target)});</script>
<title>跳转中…</title></head>
<body style="background:#0a0b12;color:#9aa3b8;font:14px sans-serif;display:grid;place-items:center;height:100vh;margin:0">
<p>正在跳转… 若没有自动跳转，<a style="color:#a78bfa" href="{esc(target)}">点这里</a>。</p>
</body></html>
"""


def audit_links(APPS):
    """正文里的跨页链接必须是 ../slug/ 形式。

    文档位于 zh/<app>/<slug>/index.html，写 [x](slug/) 会被浏览器解析成
    zh/<app>/<slug>/slug/ —— 404，而且生成器不报错，只有真点进去才发现。
    """
    known = set()
    for app in APPS.values():
        for pg in app['pages']:
            known.add(pg['slug'])
    bad = []
    for name, app in APPS.items():
        for pg in app['pages']:
            for lang in ('zh', 'en'):
                for m in re.finditer(r'\]\(([^)]+)\)', pg['body'][lang]):
                    h = m.group(1)
                    if h.startswith(('http', '#', '../', './', 'mailto', 'data')):
                        continue
                    if h.rstrip('/') in known:
                        bad.append(f'{name}/{pg["slug"]}[{lang}]: ]({h}) 应为 ](../{h.rstrip("/")}/)')
    return bad


def build(APPS):
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'assets'))
    open(os.path.join(OUT, 'assets', 'style.css'), 'w', encoding='utf-8').write(
        CSS + '\n' + (PYG_CSS or ''))

    app_list = [dict(slug=s, **v) for s, v in APPS.items()]
    count = 0

    for lang in LANGS:
        lp = os.path.join(OUT, lang)
        os.makedirs(lp, exist_ok=True)
        open(os.path.join(lp, 'index.html'), 'w', encoding='utf-8').write(
            home_html(lang, app_list)); count += 1

        for slug, app in APPS.items():
            appdir = os.path.join(lp, slug)
            os.makedirs(appdir, exist_ok=True)
            pages = app['pages']

            open(os.path.join(appdir, 'index.html'), 'w', encoding='utf-8').write(
                app_index_html(lang, slug, app['title'], pages, app_list,
                               app['desc'])); count += 1

            for i, pg in enumerate(pages):
                d = os.path.join(appdir, pg['slug'])
                os.makedirs(d, exist_ok=True)
                body = add_ids(md(pg['body'][lang]))
                h = page_html(lang, slug, app['title'], pg, body,
                              pages[i - 1] if i > 0 else None,
                              pages[i + 1] if i < len(pages) - 1 else None,
                              app_list)
                open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(h)
                count += 1

                # 无语言前缀跳转页（zh 建一次即可）
                if lang == 'zh':
                    rd = os.path.join(OUT, slug, pg['slug'])
                    os.makedirs(rd, exist_ok=True)
                    # 相对路径，不写死站点名 —— 站点改名或挪到子目录时链接不会全断
                    open(os.path.join(rd, 'index.html'), 'w', encoding='utf-8').write(
                        redirect_html(f'../../{lang}/{slug}/{pg["slug"]}/'))
                    count += 1

            if lang == 'zh':
                rd = os.path.join(OUT, slug)
                os.makedirs(rd, exist_ok=True)
                open(os.path.join(rd, 'index.html'), 'w', encoding='utf-8').write(
                    redirect_html(f'../{lang}/{slug}/'))
                count += 1

    return count


def landing():
    """站点根：语言选择，自动跳但给反悔时间"""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>COOL-DOC · Cool-zimo 全部项目的文档</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>📚</text></svg>">
<style>
:root{--v:#7c5cff;--c:#22d3ee;--bg:#0a0b12;--panel:#14161f;--line:#262a38;--ink:#eaecf4;--dim:#9aa3b8;--dim2:#7b8499}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);min-height:100vh;display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding:32px 22px;position:relative;overflow-x:hidden;
  font:15px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
body::before,body::after{content:"";position:fixed;border-radius:50%;filter:blur(100px);z-index:0;pointer-events:none}
body::before{width:520px;height:520px;left:-140px;top:-160px;background:radial-gradient(circle,rgba(124,92,255,.28),transparent 68%)}
body::after{width:440px;height:440px;right:-120px;bottom:-140px;background:radial-gradient(circle,rgba(34,211,238,.2),transparent 68%)}
.wrap{position:relative;z-index:1;max-width:520px;width:100%;text-align:center}
.logo{width:74px;height:74px;margin:0 auto 18px;border-radius:21px;display:grid;place-items:center;font-size:38px;
  background:linear-gradient(135deg,rgba(124,92,255,.2),rgba(34,211,238,.2));border:1px solid var(--line);
  box-shadow:0 18px 44px -18px rgba(124,92,255,.7);animation:fl 5s ease-in-out infinite}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
h1{font-size:32px;font-weight:750;letter-spacing:-.02em}
.sub{margin-top:6px;font-size:14px;color:var(--dim)}
.desc{margin-top:12px;font-size:13px;color:var(--dim2);line-height:1.75}
.picks{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-top:30px}
.pick{display:block;padding:20px 16px;border-radius:16px;background:var(--panel);border:1px solid var(--line);
  color:inherit;transition:.22s cubic-bezier(.22,.9,.3,1);position:relative;overflow:hidden}
.pick::before{content:"";position:absolute;inset:0;opacity:0;transition:.22s;
  background:linear-gradient(135deg,rgba(124,92,255,.1),rgba(34,211,238,.1))}
.pick:hover{transform:translateY(-4px);border-color:#39425a;box-shadow:0 16px 34px -16px rgba(0,0,0,.8);text-decoration:none}
.pick:hover::before{opacity:1}
.pick .fl2{font-size:25px;display:block;margin-bottom:8px;position:relative}
.pick b{display:block;font-size:16px;font-weight:650;position:relative}
.pick span{font-size:12px;color:var(--dim2);position:relative}
.auto{margin-top:20px;font-size:12.5px;color:var(--dim2);min-height:20px}
.auto b{color:#a78bfa}
.auto button{background:none;border:1px solid var(--line);color:var(--dim);font:inherit;font-size:11.5px;
  padding:3px 11px;border-radius:8px;margin-left:7px;cursor:pointer}
.auto button:hover{border-color:var(--v);color:#a78bfa}
.foot{margin-top:28px;font-size:11.5px;color:#4d566b}
.foot a{color:var(--dim2)}
@media(max-width:520px){.picks{grid-template-columns:1fr}h1{font-size:26px}}
@media(prefers-reduced-motion:reduce){.logo{animation:none}.pick:hover{transform:none}}
</style></head>
<body>
<div class="wrap">
  <div class="logo">📚</div>
  <h1>COOL-DOC</h1>
  <div class="sub">Cool-zimo 全部项目的文档</div>
  <p class="desc">一个应用一个目录 · 中英双语 · 链接形如
    <code style="font-family:monospace;font-size:12px">COOL-DOC/al/文档名</code></p>
  <div class="picks">
    <a class="pick" href="zh/"><span class="fl2">🇨🇳</span><b>中文</b><span>中文文档</span></a>
    <a class="pick" href="en/"><span class="fl2">🌐</span><b>English</b><span>English docs</span></a>
  </div>
  <div class="auto" id="auto"></div>
  <div class="foot"><a href="https://github.com/Cool-zimo/COOL-DOC">源码</a> ·
    <a href="https://cool-zimo.github.io/">作者主页</a></div>
</div>
<script>
(function(){
  var box=document.getElementById('auto'); if(!box) return;
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches){
    box.textContent='选择一种语言'; return; }
  var ls=(navigator.languages||[navigator.language||'']).join(',').toLowerCase();
  var zh=/^zh/.test(ls)||ls.indexOf(',zh')>-1||ls.indexOf('zh-')>-1;
  var dest=zh?'zh/':'en/', name=zh?'中文':'English', left=4, t;
  function draw(){
    box.innerHTML='将在 <b>'+left+'</b> 秒后进入'+name+'<button type="button" id="c">取消</button>';
    var b=document.getElementById('c');
    if(b) b.onclick=function(){clearInterval(t); box.textContent='已取消';};
  }
  draw();
  t=setInterval(function(){ left--;
    if(left<=0){clearInterval(t);box.textContent='正在进入'+name+'…';location.href=dest;return;} draw(); },1000);
})();
</script>
</body></html>
"""
