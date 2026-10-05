#!/usr/bin/env python3
"""
给一个「开了 Pages 却没有首页」的源码仓库，从 README 生成一个落地页。

用法：
    GH_TOKEN=xxx python3 tools/make-landing.py <repo> [repo...]
    GH_TOKEN=xxx python3 tools/make-landing.py --all      # 所有有问题的站点

为什么需要它：
  不少仓库开了 Pages，但根目录只有 README.md，没有 index.html / index.md，
  访问站点根路径直接 404。Pages 白开着，从搜索引擎点进来的人什么都看不到。

  这个脚本读 README.md，在**本地转成真正的 HTML** 再上传，
  不是把 Markdown 原样塞进 .html —— 那样 Jekyll 不会转换，用户看到的是带井号的源码。
  （这个坑真实踩过：曾给一个文档站传了 .html 后缀却写 Markdown 语法的内容。）

依赖：mistune（pip install mistune）
"""
import os, re, sys, json, base64, urllib.request, urllib.error, time

try:
    import mistune
except ImportError:
    sys.exit('需要 mistune：pip install mistune')

TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    p = os.path.expanduser('~/.tokens')
    if os.path.exists(p):
        TOKEN = open(p).read().strip().split('\n')[0]
if not TOKEN:
    sys.exit('需要 GH_TOKEN')

OWNER = 'Cool-zimo'
HEAD = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'make-landing'}


def api(method, path, payload=None):
    d = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request('https://api.github.com' + path, method=method, headers=HEAD, data=d)
    try:
        with urllib.request.urlopen(r, timeout=120) as x:
            b = x.read()
            return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        b = e.read()
        try:
            return {**json.loads(b), '__err__': True, 'status': e.code}
        except Exception:
            return {'__err__': True, 'status': e.code, 'raw': b[:200].decode('utf-8', 'ignore')}


def get_file(repo, path, br):
    d = api('GET', f'/repos/{OWNER}/{repo}/contents/{path}?ref={br}')
    if not isinstance(d, dict) or d.get('content') is None:
        return None
    return base64.b64decode(d['content'].replace('\n', '')).decode('utf-8', 'ignore')


# ---------------- 模板 ----------------
CSS = """
:root{
  --v:#7c5cff; --v2:#a78bfa; --c:#22d3ee;
  --bg:#0a0b12; --panel:#14161f; --panel2:#1a1d29;
  --line:#262a38; --ink:#eaecf4; --dim:#9aa3b8; --dim2:#7b8499;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  background:var(--bg);color:var(--ink);
  font:15px/1.78 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;padding:0 0 60px;
  /* 代码块、表格各自横滚，页面本身不该能横滚 */
  overflow-x:hidden;
}
a{color:var(--v2);text-decoration:none}
a:hover{text-decoration:underline}
body::before{
  content:"";position:fixed;top:-200px;left:50%;transform:translateX(-50%);
  width:900px;height:520px;border-radius:50%;filter:blur(120px);
  background:radial-gradient(circle,rgba(124,92,255,.22),transparent 68%);
  z-index:0;pointer-events:none;
}
.top{
  position:relative;z-index:1;text-align:center;padding:52px 22px 30px;
  border-bottom:1px solid var(--line);
}
.top h1{font-size:31px;font-weight:750;letter-spacing:-.02em;margin-bottom:8px}
.top .sub{color:var(--dim);font-size:14px}
.top .repo{
  display:inline-block;margin-top:14px;font-size:12px;padding:4px 13px;border-radius:999px;
  background:var(--panel2);border:1px solid var(--line);color:var(--dim2);
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
}
.body{position:relative;z-index:1;max-width:820px;margin:0 auto;padding:34px 22px 0}
.body h1,.body h2,.body h3{margin:30px 0 12px;line-height:1.4}
.body h1{font-size:25px}
.body h2{
  font-size:19px;padding-bottom:8px;border-bottom:1px solid var(--line);
}
.body h3{font-size:16px}
.body p{margin:12px 0;color:#cfd5e4;overflow-wrap:break-word}
.body ul,.body ol{margin:12px 0 12px 24px;color:#cfd5e4}
.body li{margin:5px 0}
.body code{
  background:var(--panel2);border:1px solid var(--line);border-radius:5px;
  padding:1.5px 6px;font-size:13px;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#e5c9ff;
}
.body pre{
  background:var(--panel);border:1px solid var(--line);border-radius:11px;
  padding:15px 17px;margin:15px 0;line-height:1.6;
  /* 必须限宽再滚：只写 overflow-x:auto 的话，长代码行会把容器撑开，
     整页跟着能横向滚 —— 实测 390px 视口下页面宽到了 476px。 */
  max-width:100%;overflow-x:auto;
}
.body pre code{
  background:none;border:none;padding:0;color:#d7dceb;font-size:13px;
  white-space:pre;
}
.body table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px;
  display:block;max-width:100%;overflow-x:auto}
.body th,.body td{border:1px solid var(--line);padding:9px 12px;text-align:left}
.body th{background:var(--panel2);font-weight:650}
.body blockquote{
  border-left:3px solid var(--v);background:rgba(124,92,255,.07);
  margin:15px 0;padding:11px 16px;border-radius:0 9px 9px 0;color:#c3cadb;
}
.body img{max-width:100%;border-radius:9px}
.body hr{border:none;border-top:1px solid var(--line);margin:28px 0}
.acts{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:34px}
.act{
  display:inline-block;padding:11px 22px;border-radius:11px;font-size:14px;font-weight:600;
  transition:.2s cubic-bezier(.22,.9,.3,1);
}
.act.go{
  background:linear-gradient(135deg,var(--v),#b06cf0);color:#fff;
  box-shadow:0 10px 24px -10px var(--v);
}
.act.go:hover{transform:translateY(-2px);text-decoration:none;
  box-shadow:0 14px 30px -10px var(--v)}
.act.src{background:var(--panel);border:1px solid var(--line);color:var(--dim)}
.act.src:hover{border-color:var(--v);color:var(--ink);text-decoration:none;
  transform:translateY(-2px)}
footer{
  text-align:center;margin-top:44px;padding-top:22px;border-top:1px solid var(--line);
  font-size:12px;color:var(--dim2);
}
footer a{color:var(--dim)}
@media(max-width:600px){
  .top{padding:38px 18px 24px}
  .top h1{font-size:25px}
  .body{padding:26px 16px 0}
}
"""


def build_html(title, subtitle, repo, md_text, live=None):
    """Markdown → HTML，套进模板。这里必须真转换，不能原样塞。"""
    body = mistune.create_markdown(escape=False, plugins=['table']) (md_text)
    live_html = ''
    if live:
        live_html = f'<a class="act go" href="{live}">打开应用 →</a>'
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<div class="top">
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
  <div class="repo">{repo}</div>
</div>
<div class="body">
{body}
  <div class="acts">
    {live_html}
    <a class="act src" href="https://github.com/{OWNER}/{repo}">看源码 →</a>
  </div>
</div>
<footer>托管在 GitHub Pages · <a href="https://github.com/{OWNER}/{repo}">{OWNER}/{repo}</a></footer>
</body>
</html>
"""


def strip_front_matter(md):
    if md.lstrip().startswith('---'):
        parts = md.lstrip().split('\n', 1)
        rest = parts[1] if len(parts) > 1 else md
        m = re.match(r'^.*?\n---\n', rest, re.S)
        if m:
            return rest[m.end():]
    return md


def make(repo, live=None):
    r = api('GET', f'/repos/{OWNER}/{repo}')
    if r.get('__err__'):
        return False, f'仓库不存在/读不到 ({r.get("status")})'
    br = r.get('default_branch', 'main')
    desc = r.get('description') or ''

    md = get_file(repo, 'README.md', br)
    if md is None:
        return False, '没有 README.md，不知道该写什么'

    md = strip_front_matter(md)
    # 去掉 README 顶部那个巨大的标题和徽章行，模板已经有大标题了
    lines = md.split('\n')
    out, skipped_h1 = [], False
    for ln in lines:
        if not skipped_h1 and re.match(r'^#{1,2}\s+\S', ln):
            skipped_h1 = True
            continue
        if re.match(r'^\s*\[!\[', ln) or re.match(r'^\s*!\[.*\]\(.*badge', ln, re.I):
            continue  # 徽章
        out.append(ln)
    md_body = '\n'.join(out).strip()

    title = r.get('name') or repo
    html = build_html(title, desc or 'GitHub Pages', repo, md_body, live)

    cur = api('GET', f'/repos/{OWNER}/{repo}/contents/index.html?ref={br}')
    payload = {'message': '加一个落地页：仓库开了 Pages 但根目录没有首页，访问 / 会 404。\n'
                          '内容由 README 生成（在本地转成真 HTML，不是把 Markdown 塞进 .html）。',
               'content': base64.b64encode(html.encode()).decode(), 'branch': br}
    if not cur.get('__err__'):
        payload['sha'] = cur['sha']
    res = api('PUT', f'/repos/{OWNER}/{repo}/contents/index.html', payload)
    if res.get('__err__'):
        return False, f"上传失败 ({res.get('status')}) {res.get('message','')}"
    return True, f'已生成 index.html（{len(html)}B）'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    # --live=repo=url 形式指定「打开应用」入口
    live_map = {}
    for a in sys.argv[1:]:
        m = re.match(r'^--live=([^=]+)=(.+)$', a)
        if m:
            live_map[m.group(1)] = m.group(2)
    ok = 0
    for repo in args:
        good, msg = make(repo, live_map.get(repo))
        print(f"  {'✓' if good else '✗'} {repo:28s} {msg}")
        if good:
            ok += 1
            time.sleep(1)
    print(f'\n完成 {ok}/{len(args)}')
    return 0 if ok == len(args) else 1


if __name__ == '__main__':
    sys.exit(main())
