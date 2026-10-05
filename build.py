#!/usr/bin/env python3
"""
COOL-DOC 站点生成器。

设计要点
--------
1. 目录式 URL：al/getting-started/index.html → /COOL-DOC/zh/al/getting-started/
   用户要「COOL-DOC/al/文档名」这种好跳转的链接，所以不用 .html 后缀。

2. 语言：可双语（zh/ 与 en/ 两套）。当前只生成中文 —— 英文要真翻译，
   不做占位半成品。LANGS 加上 'en' 即可启用另一套。

3. 正文是 Markdown，在这里用 mistune 转成真 HTML 再写文件。
   绝不能把 Markdown 原样塞进 .html —— 引擎不会转换，用户看到的是带井号的源码。

4. 侧边栏目录、上下页、锚点 id 全部自动生成。
"""
import os, re, json, shutil, html as H

try:
    import mistune
except ImportError:
    raise SystemExit('需要 mistune：pip install mistune')

ROOT = '/data/workspace/cooldoc'
OUT = os.path.join(ROOT, 'dist')
CSS = open(os.path.join(ROOT, 'css.tpl'), encoding='utf-8').read()

LANGS = ('zh',)   # 先上中文；英文要真翻译，不做占位半成品
LANG_NAME = {'zh': '中文', 'en': 'English'}

SITE = {
    'zh': {
        'tagline': 'Cool-zimo 全部项目的文档',
        'home': '首页', 'allProjects': '全部项目', 'onThisPage': '本页目录',
        'prev': '上一页', 'next': '下一页', 'edit': '在 GitHub 编辑',
        'updated': '最后更新', 'backHome': '返回文档首页',
        'langSwitch': 'English', 'otherLangs': '其它语言',
    },
    'en': {
        'tagline': 'Docs for every Cool-zimo project',
        'home': 'Home', 'allProjects': 'All projects', 'onThisPage': 'On this page',
        'prev': 'Previous', 'next': 'Next', 'edit': 'Edit on GitHub',
        'updated': 'Last updated', 'backHome': 'Back to docs home',
        'langSwitch': '中文', 'otherLangs': 'Other languages',
    },
}

# 代码块走 pygments 高亮 —— 插件 API 参考里有大段代码，不着色很难读
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
    print('提示：没装 pygments，代码块不高亮（pip install pygments）')


def slugify(text):
    """给标题做锚点 id。中文保留（GitHub 也是这么做的），空格转连字符。"""
    s = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', text.strip())
    s = s.replace(' ', '-').lower()
    return s or 'sec'


def add_ids(mdhtml):
    """给 h2/h3 加 id，供侧边栏本页目录跳转"""
    out = []
    for line in mdhtml.split('\n'):
        m = re.match(r'^<h([23])>(.*?)</h\1>$', line.strip())
        if m:
            lvl, inner = m.group(1), m.group(2)
            text = re.sub(r'<[^>]+>', '', inner)
            sid = slugify(H.unescape(text))
            out.append(f'<h{lvl} id="{sid}">{inner}</h{lvl}>')
        else:
            out.append(line)
    return '\n'.join(out)


def toc_of(mdhtml):
    """提取 h2/h3 做本页目录。

    注意：传入的 HTML 通常已经过 add_ids，标题是 <h2 id="x"> 这种形式。
    正则必须容忍 id 属性 —— 否则一条都匹配不到，「本页目录」永远是空的。
    """
    items = []
    for line in mdhtml.split('\n'):
        m = re.match(r'^<h([23])(?:\s+id="[^"]*")?>(.*?)</h\1>$', line.strip())
        if m:
            lvl, inner = int(m.group(1)), m.group(2)
            text = re.sub(r'<[^>]+>', '', inner)
            items.append((lvl, H.unescape(text), slugify(H.unescape(text))))
    return items


def lang_nav(up, sub, lang):
    """语言切换。只有一种语言时不输出 —— 否则那个链接点了就是 404。"""
    if len(LANGS) < 2:
        return ''
    zh = f'{up}../zh/{sub}'
    en = f'{up}../en/{sub}'
    return (f'<div class="lang">'
            f'<a class="{"on" if lang=="zh" else ""}" href="{zh}">中</a>'
            f'<a class="{"on" if lang=="en" else ""}" href="{en}">EN</a>'
            f'</div>')


def esc(s):
    return H.escape(s, quote=True)


def page_html(lang, app, appname, page, nav, body_html, prevp, nextp, app_list,
              base_depth):
    """生成一个文档页。base_depth 用于算相对路径前缀（zh/ 里是 2 层）"""
    up = '../' * base_depth
    L = SITE[lang]
    toc = toc_of(body_html)
    toc_html = ''
    if len(toc) > 1:
        lis = []
        for lvl, text, sid in toc:
            pad = 10 if lvl == 2 else 24
            lis.append(f'<a href="#{sid}" style="padding-left:{pad}px;font-size:{13 if lvl==2 else 12.5}px">{esc(text)}</a>')
        toc_html = (f'<div class="app-t">{esc(L["onThisPage"])}</div>' + ''.join(lis))

    # 应用导航
    nav_html = ''
    for a in app_list:
        title = a['title'][lang]
        cur = ' on' if a['slug'] == app else ''
        nav_html += f'<a class="{cur.strip()}" href="{up}{a["slug"]}/">{esc(title)}</a>'

    # 语言切换
    lang_html = lang_nav(up, f'{app}/{page["slug"]}/', lang)

    pager = ''
    if prevp or nextp:
        parts = []
        if prevp:
            parts.append(f'<a href="{up}{prevp["slug"]}/"><small>← {esc(L["prev"])}</small>'
                         f'<b>{esc(prevp["title"][lang])}</b></a>')
        else:
            parts.append('<a style="visibility:hidden"></a>')
        if nextp:
            parts.append(f'<a class="next" href="{up}{nextp["slug"]}/"><small>{esc(L["next"])} →</small>'
                         f'<b>{esc(nextp["title"][lang])}</b></a>')
        pager = f'<div class="pager">{"".join(parts)}</div>'

    other = ''.join(
        f'<a href="{up}{a["slug"]}/">{esc(a["title"][lang])}</a>'
        for a in app_list if a['slug'] != app)

    return f"""<!DOCTYPE html>
<html lang="{'zh-CN' if lang=='zh' else 'en'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page['title'][lang])} · {esc(appname[lang])} · COOL-DOC</title>
<meta name="description" content="{esc(page.get('desc',{}).get(lang,''))}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>📚</text></svg>">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="top">
  <button class="menu-btn" id="mbtn" aria-label="menu">☰</button>
  <a class="brand" href="{up}"><span class="lg">📚</span>COOL-DOC<small>{esc(L['tagline'])}</small></a>
  <div class="top-sp"></div>
  {lang_html}
</header>
<div class="scrim" id="scrim"></div>
<div class="wrap">
  <nav class="side" id="side">
    <a class="home" href="{up}">🏠 {esc(L['backHome'])}</a>
    <div class="app-t">{esc(L['allProjects'])}</div>
    {nav_html}
    {toc_html}
  </nav>
  <main class="main">
    <div class="crumb"><a href="{up}">COOL-DOC</a><span>/</span><a href="{up}{app}/">{esc(appname[lang])}</a><span>/</span>{esc(page['title'][lang])}</div>
    <article class="doc">
      <h1>{esc(page['title'][lang])}</h1>
      <p class="lead">{esc(page.get('desc',{}).get(lang,''))}</p>
      {body_html}
      {pager}
    </article>
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
  b.onclick=function(){{
    var on=s.classList.toggle('on');c.classList.toggle('on',on);
  }};
  c.onclick=close;
  s.addEventListener('click',function(e){{ if(e.target.tagName==='A'&&innerWidth<900) close(); }});
}})();
</script>
</body>
</html>
"""


def app_index_html(lang, app, appname, pages, app_list, base_depth):
    up = '../' * base_depth
    L = SITE[lang]
    cards = ''
    for p in pages:
        cards += (f'<a class="card" href="{up}{p["slug"]}/">'
                  f'<b>{esc(p["title"][lang])}</b>'
                  f'<span>{esc(p.get("desc",{}).get(lang,""))}</span>'
                  f'<span class="go">{"阅读" if lang=="zh" else "Read"} →</span></a>')
    nav_html = ''.join(
        f'<a class="{"on" if a["slug"]==app else ""}" href="{up}{a["slug"]}/">{esc(a["title"][lang])}</a>'
        for a in app_list)
    return f"""<!DOCTYPE html>
<html lang="{'zh-CN' if lang=='zh' else 'en'}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(appname[lang])} · COOL-DOC</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>📚</text></svg>">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="top">
  <button class="menu-btn" id="mbtn">☰</button>
  <a class="brand" href="{up}"><span class="lg">📚</span>COOL-DOC<small>{esc(L['tagline'])}</small></a>
  <div class="top-sp"></div>
  {lang_nav(up, app + '/', lang)}
</header>
<div class="scrim" id="scrim"></div>
<div class="wrap">
  <nav class="side" id="side">
    <a class="home" href="{up}">🏠 {esc(L['backHome'])}</a>
    <div class="app-t">{esc(L['allProjects'])}</div>
    {nav_html}
  </nav>
  <main class="main">
    <div class="crumb"><a href="{up}">COOL-DOC</a><span>/</span>{esc(appname[lang])}</div>
    <article class="doc">
      <h1>{esc(appname[lang])}</h1>
      <p class="lead">{esc(app_list[[a['slug'] for a in app_list].index(app)]['desc'][lang])}</p>
      <div class="cards">{cards}</div>
    </article>
  </main>
</div>
<footer>COOL-DOC · <a href="https://github.com/Cool-zimo/COOL-DOC">GitHub</a></footer>
<script>
(function(){{
  var b=document.getElementById('mbtn'),s=document.getElementById('side'),c=document.getElementById('scrim');
  function close(){{s.classList.remove('on');c.classList.remove('on');}}
  b.onclick=function(){{var on=s.classList.toggle('on');c.classList.toggle('on',on);}};
  c.onclick=close;
  s.addEventListener('click',function(e){{if(e.target.tagName==='A'&&innerWidth<900)close();}});
}})();
</script>
</body></html>
"""


def home_html(lang, app_list, base_depth):
    up = '../' * base_depth
    L = SITE[lang]
    cards = ''
    for a in app_list:
        cards += (f'<a class="card" href="{up}{a["slug"]}/">'
                  f'<b>{esc(a["title"][lang])}</b>'
                  f'<span>{esc(a["desc"][lang])}</span>'
                  f'<span class="go">{"进入" if lang=="zh" else "Open"} →</span></a>')
    nav_html = ''.join(f'<a href="{up}{a["slug"]}/">{esc(a["title"][lang])}</a>' for a in app_list)
    return f"""<!DOCTYPE html>
<html lang="{'zh-CN' if lang=='zh' else 'en'}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>COOL-DOC · {esc(L['tagline'])}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>📚</text></svg>">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="top">
  <button class="menu-btn" id="mbtn">☰</button>
  <a class="brand" href="{up}"><span class="lg">📚</span>COOL-DOC<small>{esc(L['tagline'])}</small></a>
  <div class="top-sp"></div>
  {lang_nav(up, '', lang)}
</header>
<div class="scrim" id="scrim"></div>
<div class="wrap">
  <nav class="side" id="side">
    <a class="home" href="{up}">🏠 {esc(L['home'])}</a>
    <div class="app-t">{esc(L['allProjects'])}</div>
    {nav_html}
  </nav>
  <main class="main">
    <article class="doc">
      <h1>COOL-DOC</h1>
      <p class="lead">{esc(L['tagline'])}{' · 中英双语' if len(LANGS)>1 else ''}</p>
      <div class="cards">{cards}</div>
    </article>
  </main>
</div>
<footer>COOL-DOC · <a href="https://github.com/Cool-zimo/COOL-DOC">GitHub</a></footer>
<script>
(function(){{
  var b=document.getElementById('mbtn'),s=document.getElementById('side'),c=document.getElementById('scrim');
  function close(){{s.classList.remove('on');c.classList.remove('on');}}
  b.onclick=function(){{var on=s.classList.toggle('on');c.classList.toggle('on',on);}};
  c.onclick=close;
  s.addEventListener('click',function(e){{if(e.target.tagName==='A'&&innerWidth<900)close();}});
}})();
</script>
</body></html>
"""


def redirect_html(target):
    """无语言前缀的跳转页，让 /COOL-DOC/al/xxx/ 也能用"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url={target}">
<script>location.replace({json.dumps(target)});</script>
<title>跳转中…</title></head>
<body style="background:#0a0b12;color:#9aa3b8;font:14px sans-serif;display:grid;place-items:center;height:100vh;margin:0">
<p>正在跳转… 若没有自动跳转，<a style="color:#a78bfa" href="{esc(target)}">点这里</a>。</p>
</body></html>
"""


def build(APPS):
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'assets'))
    open(os.path.join(OUT, 'assets', 'style.css'), 'w', encoding='utf-8').write(
        CSS + '\n' + (PYG_CSS or ''))

    app_list = [{'slug': s, **v} for s, v in APPS.items()]
    count = 0

    for lang in LANGS:
        # 单语时直接把首页放在根，URL 形如 COOL-DOC/al/spec/
        p = OUT
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, 'index.html'), 'w', encoding='utf-8').write(
            home_html(lang, app_list, 0)); count += 1

        for slug, app in APPS.items():
            appdir = os.path.join(p, slug)
            os.makedirs(appdir, exist_ok=True)
            pages = app['pages']

            # 应用首页
            open(os.path.join(appdir, 'index.html'), 'w', encoding='utf-8').write(
                app_index_html(lang, slug, app['title'], pages, app_list, 1)); count += 1

            for i, pg in enumerate(pages):
                d = os.path.join(appdir, pg['slug'])
                os.makedirs(d, exist_ok=True)
                body = add_ids(md(pg['body'][lang]))
                prevp = pages[i - 1] if i > 0 else None
                nextp = pages[i + 1] if i < len(pages) - 1 else None
                h = page_html(lang, slug, app['title'], pg, None, body,
                              prevp, nextp, app_list, 2)
                open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(h)
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
  <p class="desc">一个应用一个目录 · 中英双语 · 链接形如 <code style="font-family:monospace;font-size:12px">COOL-DOC/al/文档名</code></p>
  <div class="picks">
    <a class="pick" href="zh/"><span class="fl2">🇨🇳</span><b>中文</b><span>Documentation in Chinese</span></a>
    <a class="pick" href="en/"><span class="fl2">🌐</span><b>English</b><span>English documentation</span></a>
  </div>
  <div class="auto" id="auto"></div>
  <div class="foot"><a href="https://github.com/Cool-zimo/COOL-DOC">源码</a> ·
    <a href="https://cool-zimo.github.io/">作者主页</a></div>
</div>
<script>
(function(){
  var box=document.getElementById('auto'); if(!box) return;
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches){
    box.textContent='按浏览器语言选择'; return; }
  var ls=(navigator.languages||[navigator.language||'']).join(',').toLowerCase();
  var zh=/^zh/.test(ls)||ls.indexOf(',zh')>-1||ls.indexOf('zh-')>-1;
  var dest=zh?'zh/':'en/', name=zh?'中文':'English', left=4, t;
  function draw(){
    box.innerHTML='将在 <b>'+left+'</b> 秒后进入'+name+'<button type="button" id="c">取消</button>';
    var b=document.getElementById('c');
    if(b) b.onclick=function(){clearInterval(t); box.textContent='已取消';};
  }
  draw();
  t=setInterval(function(){ left--; if(left<=0){clearInterval(t);box.textContent='正在进入'+name+'…';location.href=dest;return;} draw(); },1000);
})();
</script>
</body></html>
"""
