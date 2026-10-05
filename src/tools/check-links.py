#!/usr/bin/env python3
"""
检查主页上所有外链是否真的打得开。

为什么需要这个：
  之前只查 Pages 的 status == 'built'，但「构建成功」不等于「根路径有内容」。
  有个文档仓库根目录只有 README.md，没有 index.html / index.md，
  Jekyll 没有首页可渲染，根路径照样 404 —— 而 Pages 状态是 built。
  用户点开才发现。

所以这里查的是：那个 URL 落到仓库里的那个文件，到底存在不存在。
  · 根路径 → 要 index.html 或 index.md
  · 具体路径 → 要那个文件存在（源码里没有 .html 时，当作 Jekyll 会渲染 .md，降级提示）
"""
import urllib.request, urllib.error, json, base64, sys, os

TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    p = os.path.expanduser('~/.tokens')
    if os.path.exists(p):
        TOKEN = open(p).read().strip().split('\n')[0]
if not TOKEN:
    sys.exit('需要 GH_TOKEN（或 ~/.tokens）。只读 public repo 也够用。')

HEAD = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'linkcheck'}


def api(path):
    r = urllib.request.Request('https://api.github.com' + path, headers=HEAD)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            return json.loads(x.read())
    except urllib.error.HTTPError as e:
        return {'__err__': True, 'code': e.code}
    except Exception as e:
        return {'__err__': True, 'code': str(e)}


def exists(repo, path, br):
    """文件是否存在（blob 才算，目录不算）"""
    d = api(f'/repos/Cool-zimo/{repo}/contents/{path}?ref={br}')
    if isinstance(d, dict) and d.get('type') == 'file':
        return True, None
    return False, (d.get('code') if isinstance(d, dict) else 'unknown')


def sniff_md_in_html(repo, path, br):
    """.html 文件里如果主要是 Markdown 语法，Jekyll 不会转换，页面会显示成源码。"""
    if not path.endswith('.html'):
        return None
    d = api(f'/repos/Cool-zimo/{repo}/contents/{path}?ref={br}')
    if not isinstance(d, dict) or d.get('content') is None:
        return None
    try:
        import re as _re
        c = base64.b64decode(d['content'].replace('\n', '')).decode('utf-8', 'ignore')
    except Exception:
        return None
    md_hits = len(_re.findall(r'^#{1,6} ', c, _re.M)) + len(_re.findall(r'^[-*] ', c, _re.M))
    tag_hits = len(_re.findall(r'<[a-zA-Z][^>]*>', c))
    # Markdown 行多而 HTML 标签少 → 基本可以断定是"后缀写错了"
    if md_hits >= 3 and tag_hits < md_hits:
        return f'里面是 Markdown 语法（{md_hits} 处 Markdown / {tag_hits} 个标签）。' \
               f'Jekyll 只对 .md 做转换，.html 里的 # 会原样显示成井号 → 改成 .md 或写成真 HTML'
    return None


def check(repo, urlpath, label):
    """urlpath 形如 /al/zh/ 或 /tiny-md/demo.html"""
    r = api(f'/repos/Cool-zimo/{repo}')
    if r.get('__err__'):
        return False, f'仓库不存在({r.get("code")})'
    br = r.get('default_branch', 'main')

    parts = [p for p in urlpath.split('/') if p]
    # 第一段是仓库名（Pages 项目站），后面才是仓库内路径
    inner = parts[1:] if parts and parts[0].lower() == repo.lower() else parts

    if not inner:
        # 根路径：必须有 index.html 或 index.md
        for cand in ('index.html', 'index.md'):
            ok, _ = exists(repo, cand, br)
            if ok:
                return True, f'根目录有 {cand}'
        return False, '根目录没有 index.html / index.md → 访问 / 会 404'

    p = '/'.join(inner)
    # 目录路径（/al/zh/ 这种）要落到目录里的 index，不能只查 'zh' 本身
    cands = [p]
    if not p.endswith('.html') and not p.endswith('.md'):
        cands += [p + '/index.html', p + '/index.md']
    hit = None
    for c in cands:
        ok, code = exists(repo, c, br)
        if ok:
            hit = c
            break
    if hit:
        # 文件存在还不够：.html 里写 Markdown 语法的话，Jekyll 不会转换，
        # 用户看到的就是带井号的源码。这个文件后缀的坑真实踩过一次。
        warn = sniff_md_in_html(repo, hit, br)
        if warn:
            return False, f'{hit} 存在，但 ' + warn
        return True, f'{hit} 存在'
    # 源码里是 .md，Pages 上由 Jekyll 渲染成 .html —— 算通过但标出来
    if p.endswith('.html'):
        ok2, _ = exists(repo, p[:-5] + '.md', br)
        if ok2:
            return True, f'{p} 由 Jekyll 从 .md 渲染（源码里没有 .html）'
    return False, f'{p} 不存在（{code}）'


def main():
    # 从主页数据里抽出所有链接
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = open(os.path.join(root, 'js', 'data.js'), encoding='utf-8').read()
    import re
    urls = []
    for m in re.finditer(r"(live|repo):\s*'([^']+)'", data):
        urls.append(m.group(2))

    seen, targets = set(), []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        # 只查自己账号下的 Pages 站（github.com 的仓库链接不会 404）
        mm = re.match(r'https://cool-zimo\.github\.io/([^/]+)(/.*)?$', u)
        if mm:
            targets.append((mm.group(1), mm.group(2) or '/', u))

    print(f'检查 {len(targets)} 个 Pages 链接\n' + '=' * 72)
    bad = []
    for repo, path, url in targets:
        ok, why = check(repo, path, url)
        print(f"  {'✓' if ok else '✗'} {url}")
        print(f"      {why}")
        if not ok:
            bad.append((url, why))

    print('=' * 72)
    if bad:
        print(f'\n有 {len(bad)} 个链接会 404：')
        for u, w in bad:
            print(f'  {u}\n    → {w}')
        return 1
    print('\n全部可访问')
    return 0


if __name__ == '__main__':
    sys.exit(main())
