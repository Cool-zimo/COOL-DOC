#!/usr/bin/env python3
"""把 dist/ 推到 COOL-DOC。用 commitTree 一次提交，原子性。"""
import os, sys, json, base64, time, urllib.request, urllib.error

TOKEN = os.environ.get('GH_TOKEN')
if not TOKEN:
    p = os.path.expanduser('/data/workspace/.tokens')
    if os.path.exists(p): TOKEN = open(p).read().strip().split('\n')[0]
if not TOKEN: sys.exit('需要 GH_TOKEN')

OWNER, NAME = 'Cool-zimo', 'COOL-DOC'
DIST = '/data/workspace/cooldoc/dist'
HEAD = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'cooldoc-push'}


def api(m, path, payload=None):
    d = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request('https://api.github.com' + path, method=m, headers=HEAD, data=d)
    try:
        with urllib.request.urlopen(r, timeout=180) as x:
            b = x.read(); return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        b = e.read()
        try: return {**json.loads(b), '__err__': True, 'status': e.code}
        except Exception: return {'__err__': True, 'status': e.code, 'raw': b[:200].decode('utf-8','ignore')}


def main():
    extra = []   # 站点源码：改文档要用的脚本和内容文件
    for rel in ['build.py', 'gen.py', 'push.py', 'css.tpl',
                'c_al.py', 'c_gd.py', 'c_rest.py', 'c_facehub.py',
                'tools/check-links.py', 'tools/scan-pages.py', 'tools/make-landing.py']:
        fp = os.path.join('/data/workspace/cooldoc', rel)
        if os.path.exists(fp):
            extra.append(('src/' + rel, fp))

    files = []
    for dp, _, fns in os.walk(DIST):
        for fn in fns:
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, DIST).replace(os.sep, '/')
            if '__pycache__' in rel: continue
            files.append((rel, full))
    files += extra
    print(f'{len(files)} 个文件（含 {len(extra)} 个源码）')

    # 当前线上文件，用于删除已消失的
    ref = api('GET', f'/repos/{OWNER}/{NAME}/git/ref/heads/main')
    if ref.get('__err__'):
        print('读不到 main:', json.dumps(ref)[:200]); return 1
    base = ref['object']['sha']
    cm = api('GET', f'/repos/{OWNER}/{NAME}/git/commits/{base}')
    cur = api('GET', f'/repos/{OWNER}/{NAME}/git/trees/{cm["tree"]["sha"]}?recursive=1')
    live = {x['path']: x for x in cur.get('tree', []) if x['type'] == 'blob'}
    newset = {r for r, _ in files}

    blobs = []
    for rel, full in files:
        c = open(full, 'rb').read()
        old = live.get(rel)
        if old and old.get('sha'):
            # 内容没变就复用
            import hashlib
            if hashlib.sha1(b'blob %d\0' % len(c) + c).hexdigest() == old['sha']:
                blobs.append({'path': rel, 'sha': old['sha'], 'mode': '100644', 'type': 'blob'})
                continue
        r = api('POST', f'/repos/{OWNER}/{NAME}/git/blobs',
                {'content': base64.b64encode(c).decode(), 'encoding': 'base64'})
        if r.get('__err__'):
            print('blob 失败', rel, json.dumps(r)[:200]); return 1
        blobs.append({'path': rel, 'sha': r['sha'], 'mode': '100644', 'type': 'blob'})

    # 删掉线上有、本地没有的
    for p in set(live) - newset:
        blobs.append({'path': p, 'sha': None, 'mode': '100644', 'type': 'blob'})
        print('  删除', p)

    tr = api('POST', f'/repos/{OWNER}/{NAME}/git/trees', {'base_tree': cm['tree']['sha'], 'tree': blobs})
    if tr.get('__err__'):
        print('tree 失败', json.dumps(tr)[:300]); return 1
    com = api('POST', f'/repos/{OWNER}/{NAME}/git/commits', {
        'message': f'更新文档站（{len(files)} 个文件）',
        'tree': tr['sha'], 'parents': [base]})
    if com.get('__err__'):
        print('commit 失败', json.dumps(com)[:300]); return 1
    api('PATCH', f'/repos/{OWNER}/{NAME}/git/refs/heads/main', {'sha': com['sha']})
    print('已提交', com['sha'][:12])

    # 核对
    t = api('GET', f'/repos/{OWNER}/{NAME}/git/trees/main?recursive=1')
    live2 = {x['path'] for x in t.get('tree', []) if x['type'] == 'blob'}
    miss = newset - live2
    print('文件核对:', '全部到位' if not miss else f'缺 {sorted(miss)[:5]}')

    for i in range(14):
        time.sleep(10)
        pg = api('GET', f'/repos/{OWNER}/{NAME}/pages')
        st = pg.get('status')
        if st == 'built':
            print(f'Pages built ({i*10+10}s) — https://cool-zimo.github.io/COOL-DOC/'); return 0
        print(f'  {i*10+10}s: {st}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
