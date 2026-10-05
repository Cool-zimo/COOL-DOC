# -*- coding: utf-8 -*-
"""GitHub Drive 文档内容 —— 中英双语"""

GD = {
    'title': {'zh': 'GitHub Drive', 'en': 'GitHub Drive'},
    'desc': {'zh': '把 GitHub 仓库当网盘用：存文件、分片上传、一键分享、插件扩展。',
             'en': 'Use GitHub repositories as a drive: store files, chunked upload, one-click sharing, plugins.'},
    'pages': [
        {
            'slug': 'getting-started',
            'title': {'zh': '快速开始', 'en': 'Getting started'},
            'desc': {'zh': '登录、上传、下载、分享，五分钟走一遍。', 'en': 'Sign in, upload, download, share — a five-minute tour.'},
            'body': {
                'zh': """
## 1. 登录

打开 [GitHub Drive](https://cool-zimo.github.io/github_drive/)，
输入 GitHub Personal Access Token（需要 `repo` 权限），点「验证并进入」。

> Token 仅保存在浏览器本地，不会上传到任何服务器。

## 2. 上传文件

- 点工具栏「⬆️ 上传文件」，选一个或多个文件
- 或直接把文件拖到页面区域
- 大文件自动分片，存到多个仓库

## 3. 上传文件夹

- 点「📂 上传文件夹」，选本地文件夹
- 自动保持目录结构，递归上传

## 4. 管理文件

- **双击**文件夹进入，双击文件预览
- **右键**文件：重命名、移动、复制、删除、收藏、分享、下载
- **Ctrl/Cmd + 点击**多选，批量操作
- **拖拽**文件到文件夹或面包屑路径，即可移动

## 5. 分享文件

- 右键文件 → 分享
- 填名称和描述
- 自动创建公开仓库 + 启用 GitHub Pages
- 分享链接可直接访问，支持打包下载

## 6. 插件

- 侧边栏 → 🧩 插件广场
- 浏览插件，点「安装」
- 点「运行」**全屏**打开，按 **ESC** 或右上角「✕」退出

## 7. 仓鼠（配套应用）

仓鼠是配套的仓库管理面板，卡片化管理多个仓库。

- 地址：<https://cool-zimo.github.io/cangshu/>
- **登录一次，两边都进** —— 两个应用同源于 `cool-zimo.github.io`，
  token 在浏览器本地共享
- 两边侧边栏底部都有一键跳转
""",
                'en': """
## 1. Sign in

Open [GitHub Drive](https://cool-zimo.github.io/github_drive/), enter a GitHub
Personal Access Token (needs the `repo` scope), and click verify.

> The token is kept in your browser only and never uploaded anywhere.

## 2. Upload files

- Click "Upload files" in the toolbar and pick one or more files
- Or just drag files onto the page
- Large files are chunked automatically across several repositories

## 3. Upload a folder

- Click "Upload folder" and choose a local folder
- Directory structure is preserved, uploaded recursively

## 4. Manage files

- **Double-click** a folder to enter it, double-click a file to preview
- **Right-click** a file: rename, move, copy, delete, favourite, share, download
- **Ctrl/Cmd + click** to multi-select and act in bulk
- **Drag** a file onto a folder or onto breadcrumb path to move it

## 5. Share files

- Right-click a file → Share
- Fill in a name and description
- A public repository is created and GitHub Pages enabled automatically
- The share link works directly and supports downloading everything

## 6. Plugins

- Sidebar → Plugin market
- Browse plugins and click "Install"
- Click "Run" to open it **full screen**; press **ESC** or the top-right "✕" to exit

## 7. Cangshu (companion app)

Cangshu is the companion repository management panel, showing your repos as cards.

- URL: <https://cool-zimo.github.io/cangshu/>
- **Sign in once, both work** — both apps are served from `cool-zimo.github.io`,
  so the token is shared in browser localStorage
- Each app's sidebar has a one-click jump to the other
"""},
        },
        {
            'slug': 'user-guide',
            'title': {'zh': '用户指南', 'en': 'User guide'},
            'desc': {'zh': '视图、多选、收藏、分享、插件、清理仓库。', 'en': 'Views, multi-select, favourites, sharing, plugins, housekeeping.'},
            'body': {
                'zh': """
## 文件管理

### 视图切换
工具栏 ▦/☰ 切换网格视图和列表视图，偏好自动保存。

### 多选操作
- 按住 Ctrl/Cmd 点击文件，切换选中
- 选中多个后右键任意一个，可批量：删除、移动、复制、收藏、下载、分享

### 拖拽移动
- 拖到当前目录的文件夹上 → 移进去
- 拖到顶部面包屑的任意一级 → 移到对应目录
- 拖到「Drive Home」→ 移到根目录

### 路径导航
顶部面包屑显示当前路径，点任意一级跳转。路径过长可横向滚动。

## 收藏与最近使用

- 右键 → 收藏 / 取消收藏
- 侧边栏「⭐ 收藏」看所有收藏（含文件夹）
- 侧边栏「🕐 最近使用」看最近打开的文件

## 分享

### 创建分享

1. 右键文件（可多选）→ 分享
2. 填名称和描述
3. 自动创建 `gd-share-{名称}-{时间戳}` 格式的公开仓库
4. 启用 GitHub Pages，生成分享链接

创建过程有**进度窗口**，五步：
创建仓库 → 复制文件 → 上传 → 启用 Pages → 完成。每步三态：待办 / 进行中 / 已完成。

### 我的分享

侧边栏「📤 我的分享」看自己创建的所有分享。

<div class="tip tip-note">
<b>列表直接从 GitHub 读</b>
<p>扫描你账号下 <code>gd-share-*</code> 仓库，不是读浏览器本地记录 ——
换设备、清缓存后依然看得到。每条带「云端」徽章，显示真实体积，可一键删仓库。</p>
</div>

### 发现分享

- 侧边栏「🌐 发现分享」
- 自动搜索所有 `gd-share-` 开头的公开仓库
- 校验标准分享格式（share.json）
- 卡片显示作者、简介、文件数，一键跳转

## 插件

### 安装与运行
1. 侧边栏「🧩 插件广场」
2. 点「⬇️ 安装」
3. 点「▶️ 运行」—— 全屏打开

顶部工具条显示插件名与版本，按 ESC 或「✕」退出。可同时开多个插件。

### 管理
已安装的显示「已安装」标签，点「🗑️ 卸载」移除。插件 HTML 存在浏览器 localStorage。

## 设置与维护

### 清理仓库历史
大文件反复修改会让 Git 仓库膨胀。仓库已配 GitHub Actions，每周日自动压缩历史。
也可手动：仓库 → Actions → 「清理仓库历史」→ Run workflow。

### 退出登录
侧边栏底部「退出登录」，清掉本地 Token 和所有数据。
""",
                'en': """
## File management

### Switching views
The ▦/☰ buttons toggle grid and list view; the preference is saved.

### Multi-select
- Hold Ctrl/Cmd and click files to toggle selection
- With several selected, right-click any of them for bulk: delete, move, copy,
  favourite, download, share

### Drag to move
- Onto a folder in the current directory → moves into it
- Onto any level of the top breadcrumb → moves to that directory
- Onto "Drive Home" → moves to the root

### Path navigation
The breadcrumb shows the current path; click any level to jump. It scrolls
horizontally when too long.

## Favourites & recent

- Right-click → favourite / unfavourite
- Sidebar "Favourites" lists everything starred (folders included)
- Sidebar "Recent" lists recently opened files

## Sharing

### Creating a share

1. Right-click a file (multi-select works) → Share
2. Fill in name and description
3. A public repo named `gd-share-{name}-{timestamp}` is created
4. GitHub Pages is enabled and a share link produced

A **progress window** shows five steps:
create repo → copy files → upload → enable Pages → done. Each step is
pending / in progress / complete.

### My shares

Sidebar "My shares" lists everything you've created.

<div class="tip tip-note">
<b>The list is read straight from GitHub</b>
<p>It scans your account for <code>gd-share-*</code> repositories rather than reading
browser-local records — so it still works after switching devices or clearing cache.
Each entry carries a "cloud" badge, shows its real size, and can delete the repo in one click.</p>
</div>

### Discovering shares

- Sidebar "Discover shares"
- Searches every public repository starting with `gd-share-`
- Validates the standard share format (share.json)
- Cards show author, description and file count, with a one-click jump

## Plugins

### Install & run
1. Sidebar → Plugin market
2. Click "Install"
3. Click "Run" — opens full screen

The top bar shows the plugin name and version; press ESC or "✕" to exit.
Multiple plugins can run at once.

### Manage
Installed ones show an "Installed" tag; click "Uninstall" to remove.
Plugin HTML is stored in browser localStorage.

## Settings & housekeeping

### Clean repository history
Repeatedly editing large files bloats a Git repository. A GitHub Action compresses
history automatically every Sunday. You can also trigger it manually:
repo → Actions → "Clean repository history" → Run workflow.

### Sign out
Sidebar bottom → "Sign out", which clears the local token and all data.
"""},
        },
        {
            'slug': 'plugin-development',
            'title': {'zh': '插件开发', 'en': 'Plugin development'},
            'desc': {'zh': '建一个 GD-Plugin-xxx 仓库就能被插件广场搜到。', 'en': 'Create a GD-Plugin-xxx repo and the market will find it.'},
            'body': {
                'zh': """
## 插件就是一个仓库

仓库名以 `GD-Plugin-` 开头，插件广场会自动搜到。

```
GD-Plugin-MyTool/
  plugin.json
  index.html
```

## plugin.json

```json
{
  "name": "MyTool",
  "version": "1.0.0",
  "description": "一句话说明这个插件做什么",
  "author": "your-name",
  "entry": "index.html",
  "icon": "🧩"
}
```

## 页面里能用什么

插件在 iframe 里**全屏**运行，通过 `postMessage` 跟宿主通信。

可参考 [GD-Plugin-CoolClock](https://github.com/Cool-zimo/GD-Plugin-CoolClock)，
照它的结构改就能做自己的。

## 桌面版才有能力

网页版插件跑在浏览器沙箱里，**碰不到本地文件系统**。

需要读写本地文件、执行系统命令的话，要用
[桌面版](https://github.com/Cool-zimo/github-drive-desktop)
或 [gdpy](https://github.com/Cool-zimo/gdpy)。两者都带权限模型兜底。

## 发布

推到 GitHub，仓库名以 `GD-Plugin-` 开头即可。
插件广场搜索有延迟，刚推的可能要等几分钟。
""",
                'en': """
## A plugin is just a repository

Name the repository with a `GD-Plugin-` prefix and the market will find it automatically.

```
GD-Plugin-MyTool/
  plugin.json
  index.html
```

## plugin.json

```json
{
  "name": "MyTool",
  "version": "1.0.0",
  "description": "One line on what this plugin does",
  "author": "your-name",
  "entry": "index.html",
  "icon": "🧩"
}
```

## What you can use in the page

Plugins run **full screen** in an iframe and talk to the host via `postMessage`.

See [GD-Plugin-CoolClock](https://github.com/Cool-zimo/GD-Plugin-CoolClock) as a
reference — copy its structure and adapt.

## Desktop-only capabilities

Web plugins run in the browser sandbox and **cannot touch the local filesystem**.

If you need to read/write local files or run system commands, use the
[desktop app](https://github.com/Cool-zimo/github-drive-desktop) or
[gdpy](https://github.com/Cool-zimo/gdpy). Both have a permission model as a guardrail.

## Publishing

Push to GitHub with a `GD-Plugin-` prefix. The market's search has some lag, so a
freshly pushed plugin may take a few minutes to appear.
"""},
        },
        {
            'slug': 'faq',
            'title': {'zh': '常见问题', 'en': 'FAQ'},
            'desc': {'zh': '单文件大小、仓库上限、跨域、多账号。', 'en': 'File size limits, repo limits, CORS, multiple accounts.'},
            'body': {
                'zh': """
## 单个文件能多大？

GitHub 对单个文件有 **100MB** 限制。超过的文件会自动分片，
存到多个仓库，读取时再拼回来。这个过程是透明的。

## 能装多少东西？

取决于你的 GitHub 账号配额。免费账号仓库总量没有硬性上限，
但单个仓库建议控制在 1GB 以内 —— 超过之后 Git 操作会明显变慢。

## 为什么有时候要开后端？

浏览器直连 GitHub API 有跨域限制，部分场景（比如某些企业网络）
会失败。这时可以跑
[本地服务端](https://github.com/Cool-zimo/github-drive-server)，
它做 CORS 代理、B 站视频解析、命令执行。

## 支持多账号吗？

支持。侧边栏可以切换多个 GitHub 账号，每个账号的 token 独立保存。

## 插件数据存在哪？

插件 HTML 存在浏览器 localStorage。换设备不会同步 ——
插件本身的数据由插件自己决定存在哪。
""",
                'en': """
## How large can a single file be?

GitHub caps a single file at **100MB**. Larger files are chunked automatically across
several repositories and reassembled on read. The process is transparent.

## How much can I store?

It depends on your GitHub account quota. Free accounts have no hard total limit, but
keeping a single repository under 1GB is advisable — Git operations slow down noticeably
beyond that.

## Why would I need the local backend?

Talking to the GitHub API directly from the browser hits CORS restrictions, and some
networks (corporate ones especially) will fail. In that case run the
[local server](https://github.com/Cool-zimo/github-drive-server), which provides a
CORS proxy, Bilibili video resolution, and command execution.

## Multiple accounts?

Yes. The sidebar can switch between several GitHub accounts, each with its own
independently stored token.

## Where is plugin data stored?

Plugin HTML lives in browser localStorage and does not sync across devices — where a
plugin keeps its own data is up to the plugin.
"""},
        },
    ],
}
