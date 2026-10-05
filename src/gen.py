#!/usr/bin/env python3
"""组装内容并生成 COOL-DOC"""
import os, sys
sys.path.insert(0, '/data/workspace/cooldoc')
from build import build, landing, audit_links, OUT
from c_al import AL
from c_gd import GD
from c_rest import CANGSHU, COVERFIT, PYTUTOR, TINYMD, MORE
from c_facehub import FACEHUB
from c_al_tech import AL_TECH
from c_tech2 import GD_TECH, COVERFIT_TECH, FACEHUB_TECH

# 技术文档接在使用教程后面
AL['pages'] += AL_TECH
GD['pages'] += GD_TECH
COVERFIT['pages'] += COVERFIT_TECH
FACEHUB['pages'] += FACEHUB_TECH

APPS = {
    'al': AL,
    'github_drive': GD,
    'cangshu': CANGSHU,
    'coverfit': COVERFIT,
    'python-tutorial': PYTUTOR,
    'tiny-md': TINYMD,
    'facehub': FACEHUB,
    'more': MORE,
}

bad = audit_links(APPS)
if bad:
    print('正文链接有误：')
    for x in bad: print('  ✗', x)
    raise SystemExit(1)

n = build(APPS)
# 站点根：语言选择页
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(landing())
n += 1

# .nojekyll：不让 GitHub 用 Jekyll 处理（我们生成的就是静态 HTML）
open(os.path.join(OUT, '.nojekyll'), 'w').write('')
# 自定义域名不需要，但加个 README
open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8').write(
    "# COOL-DOC\n\nCool-zimo 全部项目的文档站，中英双语。\n\n"
    "在线：<https://cool-zimo.github.io/COOL-DOC/>\n\n"
    "## 链接形式\n\n"
    "- `/COOL-DOC/zh/al/快速开始/` —— 带语言\n"
    "- `/COOL-DOC/al/getting-started/` —— 自动跳到对应语言\n\n"
    "## 改内容\n\n"
    "编辑 `c_al.py` / `c_gd.py` / `c_rest.py`，然后：\n\n"
    "```bash\npython3 gen.py\npython3 push.py\n```\n")

print(f'生成 {n} 个文件')

# 统计
import json
total = 0
for slug, app in APPS.items():
    total += len(app['pages'])
print(f'应用 {len(APPS)} 个，文档 {total} 篇 × 2 语言 = {total*2} 页')
