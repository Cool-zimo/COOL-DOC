#!/usr/bin/env python3
"""从 src/ 读 Markdown，组装成 APPS 数据，调用 build() 生成站点。"""
import os, re, sys

ROOT = '/data/workspace/cooldoc'
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, ROOT)
from build import build, OUT

# 每个应用：显示名、图标、简介、以及文档清单（slug, 标题, 描述, 源文件）
SPEC = {
    'al': {
        'title': 'AnyLearn',
        'icon': '🦉',
        'desc': '浏览器里真跑代码的编程教程，会记笔记、按艾宾浩斯曲线安排复习。',
        'live': 'https://cool-zimo.github.io/al/',
        'repo': 'https://github.com/Cool-zimo/al',
        'pages': [
            ('spec', '格式规范', 'al-book v1：三重标记、目录结构、字段说明、九种题型、机器人检查规则'),
            ('registry', '收录与索引', '机器人怎么发现、校验、收录一本书，索引站是怎么组织的'),
        ],
    },
    'github_drive': {
        'title': 'GitHub Drive',
        'icon': '📁',
        'desc': '用仓库存文件、分片上传、一键分享、插件扩展的虚拟文件系统。',
        'live': 'https://cool-zimo.github.io/github_drive/',
        'repo': 'https://github.com/Cool-zimo/github_drive',
        'pages': [
            ('getting-started', '快速开始', '登录、上传、下载基础操作'),
            ('user-guide', '完整用户指南', '所有功能详解'),
            ('backend', '后端服务', '可选的本地后端，突破跨域限制'),
            ('version-switch', '版本切换', '体验他人改进的预览分支'),
            ('faq', '常见问题', 'FAQ'),
            ('plugin-development', '插件开发指南', '如何开发一个插件'),
            ('plugin-api', '插件 API 参考', '插件可调用的 API 列表'),
            ('contributing', '贡献指南', '提交改进与 CI/CD 流程'),
            ('share-format', '分享格式规范', '分享仓库的标准格式'),
            ('cangshu-integration', '仓鼠联动', '与配套应用的互通'),
            ('changelog', '更新日志', '版本更新记录'),
        ],
    },
}


def strip_fm(md):
    if md.lstrip().startswith('---'):
        m = re.match(r'^\s*---\n.*?\n---\n', md, re.S)
        if m:
            return md[m.end():]
    return md


def load(app, slug):
    d = os.path.join(SRC, app)
    if not os.path.isdir(d):
        return None
    for fn in os.listdir(d):
        if re.sub(r'\.md$', '', fn).lower() == slug:
            return strip_fm(open(os.path.join(d, fn), encoding='utf-8').read())
    return None


def main():
    APPS = {}
    missing = []
    for slug, meta in SPEC.items():
        pages = []
        for ps, title, desc in meta['pages']:
            body = load(slug, ps)
            if body is None:
                missing.append(f'{slug}/{ps}')
                continue
            pages.append({
                'slug': ps,
                'title': {'zh': title, 'en': title},
                'desc': {'zh': desc, 'en': desc},
                'body': {'zh': body, 'en': body},
            })
        APPS[slug] = {
            'title': {'zh': meta['title'], 'en': meta['title']},
            'icon': meta['icon'],
            'desc': {'zh': meta['desc'], 'en': meta['desc']},
            'live': meta['live'],
            'repo': meta['repo'],
            'pages': pages,
        }

    if missing:
        print('缺源文件:', missing)

    n = build(APPS)
    total = sum(len(a['pages']) for a in APPS.values())
    print(f'生成 {n} 个页面（文档 {total} 篇 + 首页/索引）→ {OUT}')
    return 0 if not missing else 1


if __name__ == '__main__':
    sys.exit(main())
