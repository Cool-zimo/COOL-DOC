# -*- coding: utf-8 -*-
"""GitHub Drive / CoverFit / FaceHub 技术文档 —— 中英双语。
对照 js/ 实际源码写，包含若干"早期文档写错了"的订正。"""

GD_TECH = [
    {
        'slug': 'architecture',
        'title': {'zh': '虚拟文件系统', 'en': 'Virtual filesystem'},
        'desc': {'zh': '多个仓库怎么合成一个硬盘，路径怎么映射。',
                 'en': 'How several repos become one drive, and how paths map.'},
        'body': {
            'zh': """
GitHub Drive 的核心是一个**虚拟文件系统**：你看到的是一个统一的目录树，
实际上文件分散在好几个 GitHub 仓库里。

## 路径映射

```
/drive_home/文档/报告.pdf
     ↓
{ owner: 'Cool-zimo', repo: 'drive-storage-1',
  path: 'a1b2c3/报告.pdf' }
```

界面上显示的是虚拟路径，底层真实路径带一个**时间戳前缀目录**：

```js
const chunkPath = `${Date.now().toString(36)}/${chunkFileName}`;
```

用 `toString(36)` 是为了短 —— 同一个目录下不会撞名，也方便按时间排序。

## 为什么文件不直接放在仓库根目录

仓库根目录会被 README、配置文件之类的东西占。
用一层时间戳目录隔开，虚拟文件和真实文件不会混在一起。

## 一个文件跨多个仓库

大文件会被切成分片，每个分片**独立选仓库**：

```js
const repo = await this.autoSelectRepo(chunkSizeActual);
```

所以"一个文件"在物理上可能横跨三个仓库。下载时按记录的顺序读回来拼起来。

## 仓库容量追踪

```
maxRepoSize    900MB   单仓库上限
warnThreshold  0.8     用到 80% 就警告
autoCreateRepo true    不够了自动建新仓库
repoNamePrefix drive-storage
```

`getRepoUsage()` 记录每个仓库用了多少，`autoSelectRepo()` 挑一个还放得下的。

<div class="tip tip-note">
<b>容量是本地估算，不是实时查询</b>
<p>每上传一个分片就 <code>addToRepoUsage()</code> 累加。想校准可以跑
<code>syncAllRepoUsage()</code>，那会真的去查每个仓库的实际大小 ——
但要点时间，所以是手动触发的。</p>
</div>

## 分片后的元数据

```
file: {
  name, size, chunks: [
    { owner, repo, path, size, sha },
    ...
  ]
}
```

`sha` 必须记下来 —— 删除文件时 GitHub 的 contents API **要求提供 sha**，
没有就删不掉。

## 上传失败要回滚

分片上传是逐个来的，中途挂了会留下一堆孤儿分片：

```js
console.warn(`[FileManager] 上传失败，正在清理 ${chunks.length} 个已上传分片...`);
for (const chunk of chunks) {
  if (chunk.sha) {
    await this.api.deleteFile(..., chunk.sha);
    this.storage.subtractFromRepoUsage?.(...);
  }
}
```

不清的话，仓库里会越积越多没人认领的碎片，还会虚占容量。
""",
        'en': """
At the core of GitHub Drive is a **virtual filesystem**: you see one unified directory
tree, but the files physically live across several GitHub repositories.

## Path mapping

```
/drive_home/docs/report.pdf
     ↓
{ owner: 'Cool-zimo', repo: 'drive-storage-1',
  path: 'a1b2c3/report.pdf' }
```

The UI shows virtual paths; the underlying real path carries a **timestamp directory
prefix**:

```js
const chunkPath = `${Date.now().toString(36)}/${chunkFileName}`;
```

`toString(36)` keeps it short — no name collisions within a directory, and it sorts
nicely by time.

## Why files aren't at the repo root

The repo root gets occupied by READMEs, config files and the like. One timestamp
directory layer keeps virtual files from mixing with real ones.

## One file spanning several repos

Large files are split into chunks, and each chunk **picks its own repo**:

```js
const repo = await this.autoSelectRepo(chunkSizeActual);
```

So a single "file" can physically straddle three repositories. Downloading reads them
back in recorded order and reassembles.

## Repo capacity tracking

```
maxRepoSize    900MB   per-repo ceiling
warnThreshold  0.8     warn at 80% full
autoCreateRepo true    create a new repo when out of room
repoNamePrefix drive-storage
```

`getRepoUsage()` records how much each repo has used; `autoSelectRepo()` picks one that
still fits.

<div class="tip tip-note">
<b>Capacity is a local estimate, not a live query</b>
<p>Every uploaded chunk calls <code>addToRepoUsage()</code> to accumulate. To recalibrate,
run <code>syncAllRepoUsage()</code>, which actually queries real sizes — but it takes a
while, so it's manual.</p>
</div>

## Post-chunk metadata

```
file: {
  name, size, chunks: [
    { owner, repo, path, size, sha },
    ...
  ]
}
```

The `sha` must be recorded — GitHub's contents API **requires it** to delete a file.
Without it, deletion fails.

## Upload failures must roll back

Chunk upload is sequential; dying halfway leaves orphaned chunks behind:

```js
console.warn(`[FileManager] 上传失败，正在清理 ${chunks.length} 个已上传分片...`);
for (const chunk of chunks) {
  if (chunk.sha) {
    await this.api.deleteFile(..., chunk.sha);
    this.storage.subtractFromRepoUsage?.(...);
  }
}
```

Skip this and unclaimed fragments pile up in your repos, inflating used capacity.
""",
        },
    },
    {
        'slug': 'storage-internals',
        'title': {'zh': '分片与容量', 'en': 'Chunking and capacity'},
        'desc': {'zh': '文件怎么切、什么时候切、配置怎么迁移。',
                 'en': 'How files are split, when, and how config migrates.'},
        'body': {
            'zh': """
## 默认配置

```js
const defaults = {
    maxRepoSize:    900 * 1024 * 1024,   // 900MB
    autoCreateRepo: true,
    repoNamePrefix: 'drive-storage',
    warnThreshold:  0.8,
    chunkSize:      512 * 1024,          // 512KB
    minChunkSize:   512 * 1024,
    configVersion:  2
};
```

<div class="tip tip-warn">
<b>早期文档写的是 10MB 分片，那是错的</b>
<p>默认值一直是 <b>512KB</b>，也就是说超过 512KB 的文件就会被切分，
不是等到 10MB。源码注释里专门写了这一条订正。</p>
</div>

## 什么时候切

```js
const chunkSize = needSplit ? config.chunkSize : totalSize;
const totalChunks = Math.ceil(totalSize / chunkSize);
```

小于 `minChunkSize` 的文件不切，整个当一个分片（也就是直接上传）。

## 分片命名

```js
const chunkFileName = totalChunks > 1 ? `${file.name}.${i + 1}` : file.name;
```

- 只有一片：用原名
- 多片：`报告.pdf.1`、`报告.pdf.2`……

为什么用 `.1` `.2` 而不是 `.part1`？简短，而且排序天然正确。

## 两条上传通道

```js
if (chunkSizeActual > 1024 * 1024) {
    await this.api.uploadLargeFile(...);        // Git Data API
} else {
    await this.api.createOrUpdateFileBinary(...); // contents API + base64
}
```

| 通道 | 适用 | 限制 |
|---|---|---|
| contents API | ≤ 1MB | base64 后体积涨 33% |
| Git Data API | > 1MB | 走 blob/tree/commit，能到 100MB |

contents API 对单个文件有 1MB 硬限制，超了必须走 blob API。

## 配置迁移

```js
if (saved.chunkSize === 50 * 1024 * 1024
    || saved.chunkSize === 20 * 1024 * 1024
    || saved.chunkSize === 5 * 1024 * 1024) {
    saved.chunkSize = 512 * 1024;
    needUpdate = true;
}
```

早期的分片大小是 50MB、20MB、5MB，都统一改成 512KB。
**为什么要改小**：分片太大，一次上传失败要重传的就多；
而且 contents API 有 1MB 限制，大分片只能全走 blob API。

缺字段也会自动补：

```js
for (const key of Object.keys(defaults)) {
    if (saved[key] === undefined) { saved[key] = defaults[key]; needUpdate = true; }
}
```

这样加新配置项时，老用户的配置不会变成半截。

## 容量是怎么算的

每个分片上传成功后累加：

```js
this.storage.addToRepoUsage(repo.owner, repo.repo, chunkSizeActual);
```

删除时减回去。`getRepoUsage()` 返回：

```
{ "owner/repo": { size: 123456, updatedAt: "2026-10-05T..." } }
```
""",
        'en': """
## Defaults

```js
const defaults = {
    maxRepoSize:    900 * 1024 * 1024,   // 900MB
    autoCreateRepo: true,
    repoNamePrefix: 'drive-storage',
    warnThreshold:  0.8,
    chunkSize:      512 * 1024,          // 512KB
    minChunkSize:   512 * 1024,
    configVersion:  2
};
```

<div class="tip tip-warn">
<b>Early docs said 10MB chunks — that was wrong</b>
<p>The default has always been <b>512KB</b>, meaning files over 512KB get split — not
only past 10MB. The source comment carries this correction explicitly.</p>
</div>

## When splitting happens

```js
const chunkSize = needSplit ? config.chunkSize : totalSize;
const totalChunks = Math.ceil(totalSize / chunkSize);
```

Files below `minChunkSize` aren't split — they're uploaded as a single chunk (i.e.
directly).

## Chunk naming

```js
const chunkFileName = totalChunks > 1 ? `${file.name}.${i + 1}` : file.name;
```

- One chunk: keep the original name
- Many chunks: `report.pdf.1`, `report.pdf.2`, …

Why `.1` `.2` instead of `.part1`? Shorter, and it sorts correctly by nature.

## Two upload paths

```js
if (chunkSizeActual > 1024 * 1024) {
    await this.api.uploadLargeFile(...);        // Git Data API
} else {
    await this.api.createOrUpdateFileBinary(...); // contents API + base64
}
```

| Path | Use when | Limit |
|---|---|---|
| contents API | ≤ 1MB | base64 inflates size by 33% |
| Git Data API | > 1MB | blob/tree/commit, up to 100MB |

The contents API has a hard 1MB per-file limit; anything bigger must go through the
blob API.

## Config migration

```js
if (saved.chunkSize === 50 * 1024 * 1024
    || saved.chunkSize === 20 * 1024 * 1024
    || saved.chunkSize === 5 * 1024 * 1024) {
    saved.chunkSize = 512 * 1024;
    needUpdate = true;
}
```

Older chunk sizes — 50MB, 20MB, 5MB — are all normalised to 512KB.
**Why smaller**: a big chunk means more to re-upload when one attempt fails, and the
contents API's 1MB cap forces large chunks onto the blob API anyway.

Missing fields are filled in too:

```js
for (const key of Object.keys(defaults)) {
    if (saved[key] === undefined) { saved[key] = defaults[key]; needUpdate = true; }
}
```

So adding a new config option never leaves existing users with a half-populated config.

## How capacity is computed

Every successful chunk upload accumulates:

```js
this.storage.addToRepoUsage(repo.owner, repo.repo, chunkSizeActual);
```

Deletion subtracts. `getRepoUsage()` returns:

```
{ "owner/repo": { size: 123456, updatedAt: "2026-10-05T..." } }
```
""",
        },
    },
]

COVERFIT_TECH = [
    {
        'slug': 'encoders',
        'title': {'zh': '自研编码器', 'en': 'Hand-written encoders'},
        'desc': {'zh': 'BMP 和 ICO 为什么不交给浏览器，以及二进制格式的两个坑。',
                 'en': 'Why BMP and ICO aren\'t left to the browser — and two binary format traps.'},
        'body': {
            'zh': """
## 为什么不都用 toBlob

`canvas.toBlob()` 支持 PNG / JPEG / WebP，但：

- **BMP** —— 只有部分浏览器支持（Firefox 就不行）
- **ICO** —— **所有浏览器都不支持**

更麻烦的是：**不支持时它是静默失败**。调用返回成功，
但给你的是一个 PNG，却贴着 `.ico` 的文件名 —— 用户下载下来打不开，也不知道为什么。

所以这两种格式自己编码。

## 怎么判断浏览器到底支持不支持

不能查 UA（不可靠），得**真的编一次**：

```js
function probe(mime) {
  // 拿 1×1 画布实际编码，看返回的 blob.type 是不是要的那个
}
```

`toBlob` 不支持时会退化成 PNG，只看"有没有返回"根本发现不了 ——
必须看返回的 `type`。当前浏览器不支持的格式会被**禁用并说明原因**。

## BMP：两个必须注意的点

### 一、行序是自下而上

```js
for (let y = h - 1; y >= 0; y--) {    // 从最后一行开始
```

BMP 的 `biHeight` 为正表示 **bottom-up**（第一行数据其实是图像的最下面一行）。
弄反的话图像会上下颠倒，而大多数查看器不会报错 —— 只是图是倒的。

### 二、每行要 4 字节对齐

```js
const rowSize = Math.floor((w * 32 + 31) / 32) * 4;   // 4 字节对齐
...
off += rowSize - w * 4;                                // 行补齐
```

32bpp 时每行字节数天然是 4 的倍数，所以补齐量是 0。
但**保留这段逻辑** —— 一旦改成 24bpp（3 字节/像素），
宽度不是 4 的倍数时行就会错位，整张图变成斜的。

### 颜色通道是 BGRA

```js
u8[off]     = src[i + 2];   // B
u8[off + 1] = src[i + 1];   // G
u8[off + 2] = src[i];       // R
u8[off + 3] = src[i + 3];   // A
```

Canvas 给的是 RGBA，BMP 要 BGRA。顺序错了图会偏色（红蓝互换）。

## ICO：内嵌 PNG

ICO 不一定要存 BMP —— **Vista 起支持内嵌 PNG**，macOS / Windows / Linux 通吃。
体积小得多，也省得再写一套调色板逻辑。

```js
const n = Math.min(w, h);
const size = n >= 256 ? 0 : n;      // 256 在字段里记作 0
```

<div class="tip tip-warn">
<b>尺寸超过 256 要缩</b>
<p>ICO 的宽高字段是单字节，256 记作 0。而很多解析器看到超过 256 的图会直接拒绝。
所以大图先缩到 256 再编。</p>
</div>

结构就三段：

```
ICONDIR       6 字节   reserved / type=1 / count=1
ICONDIRENTRY 16 字节   宽高 / 色深 / 数据长度 / 偏移
PNG 数据      从偏移 22 开始
```

```js
view.setUint32(18, 22, true);     // imageOffset = 6 + 16
u8.set(pngBytes, 22);
```

## 透明区转 JPEG 会变白

JPEG 不支持 alpha。Canvas 导出时透明像素的 RGB 通常被写成 0（黑），
直接存就会得到一块黑底。

CoverFit 的做法是**先把透明区填成白色**再编码：

```
实际导出的是 255,255,255
```

这符合直觉 —— 打印、贴到白色背景的文档里，看到的应该是白底。
""",
        'en': """
## Why not just use toBlob everywhere

`canvas.toBlob()` handles PNG / JPEG / WebP, but:

- **BMP** — only some browsers support it (Firefox doesn't)
- **ICO** — **no browser supports it**

Worse: **failure is silent**. The call succeeds, but hands you a PNG wearing an `.ico`
filename — the user downloads something that won't open and has no idea why.

So both formats are encoded here by hand.

## How to tell whether the browser really supports it

Don't sniff the UA (unreliable) — **actually encode once**:

```js
function probe(mime) {
  // encode a 1x1 canvas and check the returned blob.type
}
```

When unsupported, `toBlob` silently degrades to PNG, so checking "did it return
anything" tells you nothing — you must read the returned `type`. Formats the current
browser can't do are **disabled with an explanation**.

## BMP: two things to watch

### 1. Rows go bottom-up

```js
for (let y = h - 1; y >= 0; y--) {    // start from the last row
```

A positive `biHeight` in BMP means **bottom-up** (the first row of data is actually the
bottom row of the image). Get it wrong and the image flips vertically — and most viewers
won't complain, it'll just be upside down.

### 2. Rows must be 4-byte aligned

```js
const rowSize = Math.floor((w * 32 + 31) / 32) * 4;   // 4-byte alignment
...
off += rowSize - w * 4;                                // row padding
```

At 32bpp each row's byte count is naturally a multiple of 4, so padding is zero.
But **keep this logic** — switch to 24bpp (3 bytes/pixel) and any width that isn't a
multiple of 4 shifts the rows, skewing the whole image.

### Channel order is BGRA

```js
u8[off]     = src[i + 2];   // B
u8[off + 1] = src[i + 1];   // G
u8[off + 2] = src[i];       // R
u8[off + 3] = src[i + 3];   // A
```

Canvas gives RGBA; BMP wants BGRA. Get it wrong and colours swap (red↔blue).

## ICO: embed a PNG

ICO doesn't have to store a BMP — **PNG embedding has been supported since Vista** and
works on macOS / Windows / Linux. Far smaller, and it avoids writing palette logic.

```js
const n = Math.min(w, h);
const size = n >= 256 ? 0 : n;      // 256 is recorded as 0
```

<div class="tip tip-warn">
<b>Shrink anything over 256</b>
<p>ICO width/height fields are single bytes, with 256 written as 0. Many parsers reject
anything larger outright. So big images are scaled to 256 first.</p>
</div>

Three sections total:

```
ICONDIR       6 bytes   reserved / type=1 / count=1
ICONDIRENTRY 16 bytes   width/height / bpp / data length / offset
PNG data      from offset 22 onward
```

```js
view.setUint32(18, 22, true);     // imageOffset = 6 + 16
u8.set(pngBytes, 22);
```

## Transparent areas turn white in JPEG

JPEG has no alpha channel. Canvas usually writes transparent pixels as RGB 0 (black),
so saving directly gives you a black background.

CoverFit **fills transparency with white** before encoding:

```
what actually gets written is 255,255,255
```

That matches expectations — printed, or pasted onto a white document, you want white.
""",
        },
    },
]

FACEHUB_TECH = [
    {
        'slug': 'api-cache',
        'title': {'zh': 'API 与缓存', 'en': 'API and caching'},
        'desc': {'zh': 'REST 封装、缓存失效，以及一个只清一半就会出 bug 的地方。',
                 'en': 'REST wrapper, cache invalidation, and one place where clearing half the keys breaks things.'},
        'body': {
            'zh': """
`js/api.js` 封装 GitHub REST，并在 localStorage 上做了一层缓存。

## 为什么要缓存

GitHub 未认证 API 只有 60 次/小时，登录后才 5000 次。
聊天应用要频繁拉消息，不打缓存很快见底。

## 四个缓存 key 必须一起清

这是最容易写错的地方：

```js
// writeFile 末尾
this._ls('fh:etag:' + owner + '/' + repo, null);              // 目录 ETag
this._ls('fh:c:' + owner + '/' + repo + '/' + path, null);    // 内容（文本）
this._ls('fh:c:' + owner + '/' + repo + '/' + path + '|b64', null); // 内容（base64）
this._ls('fh:e:' + owner + '/' + repo + '/' + path, null);    // 文件 ETag
```

<div class="tip tip-bad">
<b>只清第一个会出 bug</b>
<p>写完立刻读，拿到的是<b>旧值</b> —— 因为内容缓存还留着。
表现为"消息发出去了但看不到"，而且没有任何报错。</p>
</div>

四条都清是因为：同一个文件既可能以文本被读、也可能以 base64 被读（图片附件），
两种形态各有一份缓存，加上目录级和文件级的两个 ETag。

## 大文件走 blob API

```js
readLargeFile()   // /git/blobs/{sha}
```

contents API 对单个文件有 **1MB 限制**，超过就读不到。
大附件必须走 blob API。

## 消息是 Issue comment

FaceHub 没有自己的服务器，消息存在 **GitHub Issue 的 comment** 里：

| 方法 | 说明 |
|---|---|
| `messages(owner, repo, issueNumber, since)` | 增量拉，`since` 传时间戳 |
| `sendMessage` | 发一条 |
| `deleteMessage` | 删 comment |
| `clearMessages` | 批量清空（带进度回调） |

`since` 是性能关键 —— 每次只拉新的，不重拉全部历史。

## 密钥存储

```
localStorage
├── fh:id:{login}          身份密钥（丢了全解不开）
└── fh:sk:{login}/{room}   会话密钥（旧式，兼容）
```

导出的是 v2 格式，带版本号：

```jsonc
{
  "v": 2,
  "type": "facehub-keys",
  "identities": { "cool-zimo": { "priv": "...", "pub": "..." } },
  "rooms": { ... },
  "exportedAt": "..."
}
```

<div class="tip tip-warn">
<b>备份是明文的</b>
<p>不加口令加密是刻意的：会引入"忘了口令更惨"这个新问题。
两害相权，宁可让你自己看好文件。界面上有明确提示。</p>
</div>
""",
        'en': """
`js/api.js` wraps the GitHub REST API and adds a localStorage cache layer.

## Why cache at all

Unauthenticated GitHub API allows only 60 requests/hour; 5000 once signed in. A chat app
polls for messages constantly — without caching you burn through that fast.

## Four cache keys must be cleared together

This is the easiest thing to get wrong:

```js
// end of writeFile
this._ls('fh:etag:' + owner + '/' + repo, null);              // directory ETag
this._ls('fh:c:' + owner + '/' + repo + '/' + path, null);    // content (text)
this._ls('fh:c:' + owner + '/' + repo + '/' + path + '|b64', null); // content (base64)
this._ls('fh:e:' + owner + '/' + repo + '/' + path, null);    // file ETag
```

<div class="tip tip-bad">
<b>Clearing only the first one is a bug</b>
<p>Write then immediately read, and you get the <b>stale value</b> — the content cache is
still there. It shows up as "message sent but invisible", with no error at all.</p>
</div>

All four are needed because the same file may be read as text or as base64 (image
attachments) — two separate caches — plus one ETag at directory level and one at file
level.

## Large files go through the blob API

```js
readLargeFile()   // /git/blobs/{sha}
```

The contents API has a **1MB per-file limit**; beyond that reads fail. Large attachments
must use the blob API.

## Messages are issue comments

FaceHub has no server of its own — messages live in **GitHub issue comments**:

| Method | Purpose |
|---|---|
| `messages(owner, repo, issueNumber, since)` | incremental fetch; `since` is a timestamp |
| `sendMessage` | post one |
| `deleteMessage` | delete a comment |
| `clearMessages` | bulk clear (with progress callback) |

`since` is the performance lever — only new messages are fetched, never all history.

## Key storage

```
localStorage
├── fh:id:{login}          identity key (lose it and nothing decrypts)
└── fh:sk:{login}/{room}   session key (legacy, kept for compatibility)
```

Exports use the v2 format, versioned:

```jsonc
{
  "v": 2,
  "type": "facehub-keys",
  "identities": { "cool-zimo": { "priv": "...", "pub": "..." } },
  "rooms": { ... },
  "exportedAt": "..."
}
```

<div class="tip tip-warn">
<b>The backup is plaintext</b>
<p>Not encrypting it with a passphrase is deliberate: it introduces a worse problem —
forgetting the passphrase. Of the two risks, guarding the file is the lesser evil.
The UI says so clearly.</p>
</div>
""",
        },
    },
]
