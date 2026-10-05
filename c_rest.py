# -*- coding: utf-8 -*-
"""其余应用文档内容 —— 中英双语"""

CANGSHU = {
    'title': {'zh': '仓鼠 Cangshu', 'en': 'Cangshu'},
    'desc': {'zh': 'GitHub 仓库管理面板：卡片化、在线编辑、Pages 状态一目了然。',
             'en': 'A GitHub repository management panel: card view, in-browser editing, Pages status at a glance.'},
    'pages': [
        {
            'slug': 'getting-started',
            'title': {'zh': '快速开始', 'en': 'Getting started'},
            'desc': {'zh': '登录、看卡片、在线改文件。', 'en': 'Sign in, browse cards, edit files online.'},
            'body': {
                'zh': """
打开 [仓鼠](https://cool-zimo.github.io/cangshu/)，用 GitHub Token 登录。

**和 GitHub Drive 同源** —— 两个应用都在 `cool-zimo.github.io` 下，
token 在浏览器本地共享，登录一次两边都进。

## 卡片上有什么

每张卡片直接显示：

- 仓库名、描述、语言
- **Pages 状态**（是否已部署）
- **最新 commit hash**
- 星标、可见性

不用点进去、不用切到 GitHub 就能知道这个仓库是不是活的。

## 在线改文件

右键文件 → 丢进 **vscode.dev** 编辑。
改完在 vscode.dev 里提交，回来刷新就能看到。

## 批量操作

多选卡片可以批量：设公开/私有、加 topic、删除。

> 删除仓库是不可逆的。批量删之前建议先设私有观察几天。
""",
                'en': """
Open [Cangshu](https://cool-zimo.github.io/cangshu/) and sign in with a GitHub token.

**Same origin as GitHub Drive** — both apps are served from `cool-zimo.github.io`, so
the token is shared in browser localStorage and signing into one signs you into both.

## What's on a card

Each card shows directly:

- Repo name, description, language
- **Pages status** (deployed or not)
- **Latest commit hash**
- Stars, visibility

You can tell whether a repo is alive without opening it or switching to GitHub.

## Editing files online

Right-click a file → open it in **vscode.dev**. Commit there, come back and refresh.

## Bulk operations

Multi-select cards to bulk: set public/private, add topics, delete.

> Deleting a repository is irreversible. Consider setting things private for a few days
> before bulk-deleting.
"""},
        },
        {
            'slug': 'tips',
            'title': {'zh': '使用技巧', 'en': 'Tips'},
            'desc': {'zh': '几个能省时间的用法。', 'en': 'A few time-saving tricks.'},
            'body': {
                'zh': """
## 按 Pages 状态筛选

想知道哪个仓库的 Pages 挂了、哪个还没开，直接筛。

## 快速定位刚推过的仓库

卡片上的 commit hash 是最新的。刚推完来这里看一眼，
比在 GitHub 上翻列表快。

## 和 Drive 配合

- Drive 存文件 → 仓鼠管仓库
- 两边侧边栏底部都有一键跳转

## 归档不用的仓库

比起删除，**归档（archive）** 更安全：只读，历史全留着，
页面上会有归档标记，不会误操作。
""",
                'en': """
## Filter by Pages status

To find which repos have broken Pages or none at all, filter directly.

## Find what you just pushed

The commit hash on each card is the latest. After a push, glance here — faster than
scrolling through GitHub's list.

## Pairing with Drive

- Drive stores files → Cangshu manages repositories
- Both sidebars have a one-click jump to the other

## Archive instead of deleting

**Archiving** is safer than deleting: read-only, full history kept, marked as archived
in the UI so you can't act on it by accident.
"""},
        },
    ],
}

COVERFIT = {
    'title': {'zh': 'CoverFit', 'en': 'CoverFit'},
    'desc': {'zh': '图片裁切与格式转换，纯浏览器本地处理，不上传。',
             'en': 'Image cropping and format conversion, entirely in your browser — nothing is uploaded.'},
    'pages': [
        {
            'slug': 'getting-started',
            'title': {'zh': '怎么用', 'en': 'How to use'},
            'desc': {'zh': '拖入图片、选比例、导出。', 'en': 'Drop an image, pick a ratio, export.'},
            'body': {
                'zh': """
打开 [CoverFit](https://cool-zimo.github.io/coverfit/)。

## 导入

三种方式都行：

- **拖入**文件（支持多张）
- **点选**文件
- **Ctrl+V** 粘贴剪贴板里的图

## 裁切

11 种预设比例：

| 比例 | 常见用途 |
|---|---|
| 1:1 | 头像 |
| 16:9 | 视频封面 |
| 3:4 | 小红书 |
| 2.35:1 | 公众号封面 |
| 1.91:1 | 分享卡片 |

也可以自定义。裁切框可拖可缩放，锁比例时另一边跟着走。

## 格式

PNG / JPEG / WebP / GIF / BMP / ICO / AVIF。

<div class="tip tip-note">
<b>透明图转 JPEG 会变白，不是变黑</b>
<p>JPEG 不支持透明通道，必须填一个底色。填黑会让 logo 边缘发黑，
所以这里填白。</p>
</div>

## 尺寸

原尺寸 / ≤4096 / ≤2048 / ≤1200 / ≤800 / 指定宽度。

## 批量

一次拖多张，每张保留自己的裁切框，可一键全部导出。

## 隐私

图片**不上传服务器**。全部在浏览器里用 Canvas 处理，断网也能用。
""",
                'en': """
Open [CoverFit](https://cool-zimo.github.io/coverfit/).

## Import

Three ways, all supported:

- **Drag and drop** (multiple files)
- **Click to choose** files
- **Ctrl+V** to paste from the clipboard

## Crop

11 preset ratios:

| Ratio | Typical use |
|---|---|
| 1:1 | Avatar |
| 16:9 | Video thumbnail |
| 3:4 | Xiaohongshu |
| 2.35:1 | WeChat cover |
| 1.91:1 | Share card |

Custom ratios work too. The crop box can be dragged and resized; locking the ratio
makes the other side follow.

## Formats

PNG / JPEG / WebP / GIF / BMP / ICO / AVIF.

<div class="tip tip-note">
<b>Transparent → JPEG becomes white, not black</b>
<p>JPEG has no alpha channel, so a background colour must be filled in. Filling black
makes logo edges look dirty, so white is used instead.</p>
</div>

## Size

Original / ≤4096 / ≤2048 / ≤1200 / ≤800 / custom width.

## Batch

Drop several images at once; each keeps its own crop box, and you can export all in
one click.

## Privacy

Images are **never uploaded**. Everything happens in your browser via Canvas, so it
works offline too.
"""},
        },
        {
            'slug': 'under-the-hood',
            'title': {'zh': '实现细节', 'en': 'Under the hood'},
            'desc': {'zh': '为什么 BMP 和 ICO 是自己写的编码器。', 'en': 'Why BMP and ICO encoders are hand-written.'},
            'body': {
                'zh': """
## 自己写编码器

**BMP** 只有部分浏览器支持 `toBlob`，**ICO 所有浏览器都不支持**。

所以这两个格式的编码器是自己写的。不这么做的话，选 BMP 或 ICO 会静默失败 ——
按钮点了没反应，或者下载下来其实是个 PNG 却叫 `.ico`。

## 格式可用性靠探测

不查 User-Agent，而是拿 1×1 画布实际编一次，看返回的 `blob.type`。

<div class="tip tip-warn">
<b>为什么不能只看有没有返回值</b>
<p><code>toBlob</code> 不支持某格式时会<b>静默退化成 PNG</b>，
返回值照样有。只有检查 <code>blob.type</code> 才能发现。</p>
<p>当前浏览器不支持的格式会直接禁用并说明原因。</p>
</div>

## 导出结果验证过

导出的文件用 Pillow 反读校验像素，不是"看起来能用"：

- 透明图转 JPEG → 透明区确实是白色 (255,255,255)
- 大图导 ICO → 自动缩到 256×256（超出多数解析器会拒收）
- 自研 BMP → 读出像素与源图逐点一致
""",
                'en': """
## Hand-written encoders

Only some browsers support `toBlob` for **BMP**, and **no browser supports ICO**.

So the encoders for those two are written by hand. Without them, picking BMP or ICO
would fail silently — the button does nothing, or you download a PNG named `.ico`.

## Format support is probed, not sniffed

Rather than checking the User-Agent, a 1×1 canvas is actually encoded and the
resulting `blob.type` inspected.

<div class="tip tip-warn">
<b>Why checking for a return value isn't enough</b>
<p>When <code>toBlob</code> doesn't support a format it <b>silently falls back to PNG</b>
and still returns a value. Only inspecting <code>blob.type</code> reveals the truth.</p>
<p>Formats your browser can't do are disabled with an explanation.</p>
</div>

## Export results are verified

Exported files are read back with Pillow and pixel-checked — not "seems to work":

- transparent → JPEG really is white (255,255,255) in the transparent area
- large image → ICO really is scaled to 256×256 (larger is rejected by most parsers)
- hand-rolled BMP → decoded pixels match the source point by point
"""},
        },
    ],
}

PYTUTOR = {
    'title': {'zh': 'Python 从零到进阶', 'en': 'Python from zero'},
    'desc': {'zh': 'AnyLearn 的中文单本站，同样能在页面里跑代码。',
             'en': 'The single-book Chinese site — code runs in the page too.'},
    'pages': [
        {
            'slug': 'index',
            'title': {'zh': '介绍', 'en': 'Overview'},
            'desc': {'zh': '和 AnyLearn 什么关系、适合谁。', "en": "How it relates to AnyLearn, and who it is for."},
            'body': {
                'zh': """
打开 [Python 从零到进阶](https://cool-zimo.github.io/python-tutorial/)。

这是 AnyLearn 的**中文单本站** —— 内容集中在 Python 入门这一条线上，
不像 AnyLearn 那样有 25 本教材。

## 和 AnyLearn 的区别

| | 本站 | AnyLearn |
|---|---|---|
| 教材数 | 1 本 | 25 本 |
| 语言 | 中文 | 中英双语 |
| 第三方教材 | 无 | 有 |
| 复习调度 | 有 | 有 |

如果你只想学 Python 基础，这个站更轻。
想看更多方向（算法、网页、数据分析、标准库）或者想自己写教材，用 AnyLearn。

## 共同点

- 代码在浏览器里真跑（Pyodide）
- 笔记同步到你的私有仓库
- 艾宾浩斯复习调度
""",
                'en': """
Open [Python from zero](https://cool-zimo.github.io/python-tutorial/).

This is AnyLearn's **single-book Chinese site** — the content focuses on one Python
beginner track rather than AnyLearn's 25 textbooks.

## How it differs from AnyLearn

| | This site | AnyLearn |
|---|---|---|
| Books | 1 | 25 |
| Languages | Chinese | zh + en |
| Third-party books | no | yes |
| Review scheduling | yes | yes |

If you only want Python basics, this site is lighter. For more tracks (algorithms, web,
data analysis, stdlib) or to author your own book, use AnyLearn.

## Shared

- Code really runs in the browser (Pyodide)
- Notes sync to your private repository
- Ebbinghaus review scheduling
"""},
        },
    ],
}

TINYMD = {
    'title': {'zh': 'tiny-md', 'en': 'tiny-md'},
    'desc': {'zh': '零依赖 Markdown + LaTeX 渲染器，公式不用打 $ 也能渲染。',
             'en': 'A zero-dependency Markdown + LaTeX renderer — formulas render without typing $.'},
    'pages': [
        {
            'slug': 'getting-started',
            'title': {'zh': '怎么用', 'en': 'How to use'},
            'desc': {'zh': '两种方式：JS 调用 和 纯 HTML 内联。', 'en': 'Two ways: JS API and plain HTML inline.'},
            'body': {
                'zh': """
## 用 JS

```js
const TinyMD = require('tiny-md');
document.getElementById('out').innerHTML = TinyMD.render(text);
```

只高亮代码：

```js
TinyMD.highlight('const x = 1;', 'js');
```

## 不想写 JS

```html
<script src="https://cdn.jsdelivr.net/gh/Cool-zimo/tiny-md/tiny-md.js"></script>
<script type="text/tiny-md">
# 直接写 Markdown
公式 $x^2$ 也能渲染
</script>
```

## 演示

[在线演示](https://cool-zimo.github.io/tiny-md/demo.html)
""",
                'en': """
## With JS

```js
const TinyMD = require('tiny-md');
document.getElementById('out').innerHTML = TinyMD.render(text);
```

Highlight only:

```js
TinyMD.highlight('const x = 1;', 'js');
```

## Without writing JS

```html
<script src="https://cdn.jsdelivr.net/gh/Cool-zimo/tiny-md/tiny-md.js"></script>
<script type="text/tiny-md">
# Just write Markdown
Formulas like $x^2$ render too
</script>
```

## Demo

[Live demo](https://cool-zimo.github.io/tiny-md/demo.html)
"""},
        },
        {
            'slug': 'design',
            'title': {'zh': '设计取舍', 'en': 'Design choices'},
            'desc': {'zh': '先转义再生成标签，以及为什么不用 $。', "en": "Escape first, then build tags — and why $ is not required."},
            'body': {
                'zh': """
## 先转义再生成

顺序是**先转义用户输入，再生成 HTML 标签**，而不是反过来。

反过来做的话，`<script>` 这类内容会先变成标签再被"转义"，
实际上已经晚了 —— XSS 就是这么来的。

## 公式不用打 $

很多渲染器要求公式必须包在 `$...$` 里。tiny-md 会自己识别
`x^2`、`a_i` 这类模式，不用额外标记。

代价是**偶尔会误判** —— 比如正文里写了 `a_b` 这种下划线，
可能被当成下标。遇到这种情况用反引号包起来。

## 零依赖

不引任何库，单个 JS 文件。代价是功能不如 marked / markdown-it 全，
但胜在能直接塞进任何页面。
""",
                'en': """
## Escape first, then build

The order is **escape user input first, then generate HTML tags** — not the reverse.

Do it the other way and content like `<script>` becomes a tag before it gets
"escaped", which is too late — that's how XSS happens.

## No $ required

Many renderers require formulas to be wrapped in `$...$`. tiny-md recognises patterns
like `x^2` and `a_i` on its own, with no extra markup.

The cost is **occasional false positives** — writing `a_b` in prose may be read as a
subscript. Wrap it in backticks when that matters.

## Zero dependencies

No libraries, a single JS file. The trade-off is fewer features than marked or
markdown-it, but it drops into any page directly.
"""},
        },
    ],
}

MORE = {
    'title': {'zh': '其它工具', 'en': 'Other tools'},
    'desc': {'zh': 'gdpy、本地服务端、插件市场、修仙模拟器、fengjson、Cat Sigma。',
             'en': 'gdpy, local server, plugin market, xiudao, fengjson, Cat Sigma.'},
    'pages': [
        {
            'slug': 'index',
            'title': {'zh': '一览', 'en': 'Overview'},
            'desc': {'zh': '每个小工具一句话说明和入口。', 'en': 'One line and a link for each small tool.'},
            'body': {
                'zh': """
## GitHub Drive 生态

| 仓库 | 说明 |
|---|---|
| [桌面版（Electron）](https://github.com/Cool-zimo/github-drive-desktop) | 让插件能读写本地文件、执行系统命令，带权限模型 |
| [gdpy](https://github.com/Cool-zimo/gdpy) | Python + Tkinter 版桌面客户端，Actions 编译，免装 Python |
| [本地服务端](https://github.com/Cool-zimo/github-drive-server) | Go 写的本地能力平台：CORS 代理、B 站解析、命令执行 |
| [插件市场](https://github.com/Cool-zimo/github_drive_plugins) | 建 `GD-Plugin-xxx` 仓库就能被搜到 |
| [CoolClock 插件](https://github.com/Cool-zimo/GD-Plugin-CoolClock) | 第三方插件的参考实现 |

## 库与组件

| 仓库 | 说明 |
|---|---|
| [tiny-md](https://github.com/Cool-zimo/tiny-md) | 零依赖 Markdown + LaTeX 渲染器 |
| [fengjson](https://github.com/Cool-zimo/fengjson) | Python json 标准库封装，带单元测试和日志 |

## 玩票

| 仓库 | 说明 |
|---|---|
| [修仙模拟器](https://github.com/Cool-zimo/xiudao) | 纯前端文字修仙游戏 |
| [Cat Sigma](https://github.com/Cool-zimo/cat-sigma) | Cat Sigma GIF 展示页 |

## AnyLearn 相关

| 仓库 | 说明 |
|---|---|
| [al](https://github.com/Cool-zimo/al) | AnyLearn 主站 |
| [al-textbooks](https://github.com/Cool-zimo/al-textbooks) | 教材内容仓库 |
| [al-docs](https://github.com/Cool-zimo/al-docs) | 第三方书籍索引与格式规范 |
""",
                'en': """
## GitHub Drive ecosystem

| Repo | Notes |
|---|---|
| [Desktop (Electron)](https://github.com/Cool-zimo/github-drive-desktop) | Lets plugins read/write local files and run commands, behind a permission model |
| [gdpy](https://github.com/Cool-zimo/gdpy) | Python + Tkinter desktop client, built by Actions, no Python install needed |
| [Local server](https://github.com/Cool-zimo/github-drive-server) | Go-based local capability platform: CORS proxy, Bilibili parsing, command execution |
| [Plugin market](https://github.com/Cool-zimo/github_drive_plugins) | Create a `GD-Plugin-xxx` repo and it gets found |
| [CoolClock plugin](https://github.com/Cool-zimo/GD-Plugin-CoolClock) | Reference implementation for third-party plugins |

## Libraries

| Repo | Notes |
|---|---|
| [tiny-md](https://github.com/Cool-zimo/tiny-md) | Zero-dependency Markdown + LaTeX renderer |
| [fengjson](https://github.com/Cool-zimo/fengjson) | Python json stdlib wrapper with tests and logging |

## Just for fun

| Repo | Notes |
|---|---|
| [xiudao](https://github.com/Cool-zimo/xiudao) | A browser-based text cultivation game |
| [Cat Sigma](https://github.com/Cool-zimo/cat-sigma) | Cat Sigma GIF showcase |

## AnyLearn

| Repo | Notes |
|---|---|
| [al](https://github.com/Cool-zimo/al) | The AnyLearn site |
| [al-textbooks](https://github.com/Cool-zimo/al-textbooks) | Textbook content repository |
| [al-docs](https://github.com/Cool-zimo/al-docs) | Third-party book index and format spec |
"""},
        },
    ],
}
