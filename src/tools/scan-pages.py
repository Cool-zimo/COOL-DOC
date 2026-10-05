#!/usr/bin/env python3
"""
扫一遍账号下所有开了 Pages 的仓库，看站点根路径是不是真能打开。

用法：
    GH_TOKEN=xxx python3 tools/scan-pages.py

查两件事：
  1. 根目录有没有 index.html / index.md —— 没有的话访问 / 就是 404
  2. 如果是 .html，里面是不是混进了 Markdown 语法 —— Jekyll 只转换 .md，
     .html 里的 "# 标题" 会原样显示成井号

第 2 条只对 .html 生效。.md 里是 Markdown 是它的正常形态，不能误报
（第一版就报过错，把 docs/index.md 当成了问题）。

分享仓库（gd-share-* / share-*）本来就不是站点，没有首页不算错，单独归类。
"""
import os, re, sys, json, base64, urllib.request, urllib.error, time

TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not TOKEN:
    p = os.path.expanduser('~/.tokens')
    if os.path.exists(p):
        TOKEN = open(p).read().strip().split('\n')[0]
if not TOKEN:
    sys.exit('需要 GH_TOKEN')

OWNER = 'Cool-zimo'
HEAD = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'scan-pages'}

SHARE_PREFIX = ('gd-share', 'share-')


def api(path):
    r = urllib.request.Request('https://api.github.com' + path, headers=HEAD)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            return json.loads(x.read())
    except urllib.error.HTTPError as e:
        return {'__err__': True, 'code': e.code}
    except Exception as e:
        return {'__err__': True, 'code': str(e)}


def root_names(repo, br):
    d = api(f'/repos/{OWNER}/{repo}/contents/?ref={br}')
    return [x['name'] for x in d] if isinstance(d, list) else None


def sniff_md_in_html(repo, path, br):
    """.html 里主要是 Markdown 语法就报警。只对 .html 调。"""
    if not path.endswith('.html'):
        return None
    d = api(f'/repos/{OWNER}/{repo}/contents/{path}?ref={br}')
    if not isinstance(d, dict) or d.get('content') is None:
        return None
    try:
        c = base64.b64decode(d['content'].replace('\n', '')).decode('utf-8', 'ignore')
    except Exception:
        return None
    md = len(re.findall(r'^#{1,6} ', c, re.M)) + len(re.findall(r'^[-*] ', c, re.M))
    tag = len(re.findall(r'<[a-zA-Z][^>]*>', c))
    if md >= 3 and tag < md:
        return (f'里面是 Markdown（{md} 处 / {tag} 个标签）。'
                f'Jekyll 只转换 .md，.html 里的 # 会原样显示成井号')
    return None


def main():
    repos = []
    for pg in range(1, 6):
        d = api(f'/users/{OWNER}/repos?per_page=100&page={pg}&sort=full_name')
        if not isinstance(d, list) or not d:
            break
        repos += d
        if len(d) < 100:
            break

    sites = []
    for r in repos:
        p = api(f"/repos/{OWNER}/{r['name']}/pages")
        if not p.get('__err__'):
            sites.append({'name': r['name'], 'status': p.get('status'),
                          'br': r.get('default_branch', 'main')})
        time.sleep(0.05)

    sites.sort(key=lambda x: x['name'])
    print(f'{len(repos)} 个仓库，其中 {len(sites)} 个开了 Pages\n')
    print(f"{'仓库':32s} {'Pages':8s} {'根首页':11s} 判定")
    print('-' * 84)

    bad, share_no_idx = [], []
    for s in sites:
        n, br = s['name'], s['br']
        fs = root_names(n, br)
        if fs is None:
            print(f'{n:32s} {s["status"]:8s} {"(读不到)":11s} ?')
            continue
        idx = next((c for c in ('index.html', 'index.md') if c in fs), None)
        is_share = n.startswith(SHARE_PREFIX)

        if not idx:
            if is_share:
                share_no_idx.append(n)
                print(f'{n:32s} {s["status"]:8s} {"无":11s} 分享仓库（非站点，正常）')
            else:
                bad.append((n, '根路径没有 index.html / index.md → 访问 / 会 404'))
                print(f'{n:32s} {s["status"]:8s} {"无":11s} ✗ 根路径会 404')
            continue

        warn = sniff_md_in_html(n, idx, br)   # 内部已限定只对 .html
        if warn:
            bad.append((n, f'{idx}：{warn}'))
            print(f'{n:32s} {s["status"]:8s} {idx:11s} ✗ 会显示成源码')
        else:
            print(f'{n:32s} {s["status"]:8s} {idx:11s} ✓')
        time.sleep(0.08)

    print('-' * 84)
    print(f'分享仓库 {len(share_no_idx)} 个（没有首页是正常的）')
    if bad:
        print(f'\n有 {len(bad)} 个站点有问题：')
        for n, w in bad:
            print(f'  ✗ {n}\n      {w}')
        print('\n修法：python3 tools/make-landing.py <repo>（从 README 生成落地页）')
        return 1
    print('\n全部站点根路径都能打开')
    return 0


if __name__ == '__main__':
    sys.exit(main())
