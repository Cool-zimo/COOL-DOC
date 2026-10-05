# -*- coding: utf-8 -*-
"""AnyLearn（通学万义）文档内容 —— 中英双语"""

AL = {
    'title': {'zh': 'AnyLearn · 通学万义', 'en': 'AnyLearn'},
    'desc': {'zh': '浏览器里真跑代码的编程教程，会记笔记、按艾宾浩斯曲线安排复习。',
             'en': 'Programming tutorials where code actually runs in your browser — with notes and spaced repetition.'},
    'pages': [
        {
            'slug': 'getting-started',
            'title': {'zh': '快速开始', 'en': 'Getting started'},
            'desc': {'zh': '登录、挑一本书、学完第一课。', 'en': 'Sign in, pick a book, finish your first lesson.'},
            'body': {
                'zh': """
## 1. 登录

打开 [AnyLearn](https://cool-zimo.github.io/al/zh/)，粘贴一个 GitHub Personal Access Token。

- 打开 GitHub → Settings → Developer settings → **Personal access tokens**
- 建议用 **Fine-grained token**，只勾 `Contents: Read and write`，有效期 90 天
- 粘贴回来，点「验证并进入」

> Token 只存在浏览器 localStorage，从不发往本站以外的任何服务器。
> 本站是纯静态页面，没有后端可以接收它。

为什么要登录：不登录也能看官方教材，但**第三方教材要靠你的 token 去 GitHub 搜索**。
未认证 API 只有 60 次/小时，搜几本书就见底；登录后是 5000 次/小时。

## 2. 挑一本书

首页是全部教材的卡片列表。点封面进入。

- 卡片上的标签是难度分级：入门 / 进阶 / 实战 / 复习
- 第三方教材会带一个「第三方」角标
- 顶部搜索框可以在所有教材的**书名和目录**里找关键词

## 3. 学一课

每课的结构是：标题 → 一段引言 → 正文 → 随堂练习 → 测验。

**代码是真的在跑。** 正文里的 Python 代码块可以直接编辑、点「运行」，
由浏览器内的 Pyodide 执行 —— 不是截图，不是模拟器，是真的 CPython 编译的 wasm。

- **随堂练习**：不计入进度，用来确认你读懂了
- **测验（标「计入学完」）**：做完才算这一课学完

## 4. 笔记

右侧栏可以随时记笔记，跟着课文走。

笔记会同步到你自己的**私有仓库** `python-tutorial-notes`，
换设备登录同一个账号就能拉回来。没登录就只存在本地。

## 5. 复习

学完的课会进入艾宾浩斯复习队列：

```
1 天 → 2 天 → 4 天 → 7 天 → 15 天 → 30 天 → 60 天 → 毕业
```

到期的课会出现在侧边栏「今日复习」。这不是提醒你"该学了"，
而是**在遗忘曲线的拐点上把你拉回来**。

## 6. 接下来

- 想给别人写教材 → [怎么写一本书](../write-book/)
- 想查格式细节 → [教材格式规范](../book-format/)
- 有问题 → [常见问题](../faq/)
""",
                'en': """
## 1. Sign in

Open [AnyLearn](https://cool-zimo.github.io/al/en/) and paste a GitHub Personal Access Token.

- GitHub → Settings → Developer settings → **Personal access tokens**
- A **Fine-grained token** with only `Contents: Read and write` for 90 days is enough
- Paste it back and click verify

> The token lives in your browser's localStorage and is never sent anywhere else.
> This site is static — there is no backend that could receive it.

Why sign in: official textbooks are readable without it, but **third-party books are
discovered by searching GitHub with your token**. The unauthenticated API allows only
60 requests/hour, which a handful of searches will exhaust; signed in you get 5,000.

## 2. Pick a book

The home page is a card grid of every textbook. Click a cover to enter.

- The badge shows difficulty: beginner / intermediate / practical / review
- Third-party books carry a "third-party" tag
- The top search box looks through **book titles and tables of contents**

## 3. Take a lesson

Every lesson is: title → a short lead → body → in-lesson practice → quiz.

**The code really runs.** Python blocks in the body are editable and runnable,
executed by Pyodide inside your browser — not a screenshot, not a simulation,
but actual CPython compiled to wasm.

- **In-lesson practice**: does not count toward progress, it just checks you understood
- **Quiz (marked "counts")**: finishing it marks the lesson complete

## 4. Notes

The right-hand panel holds notes, scoped to the lesson you're on.

Notes sync to your own **private repository** `python-tutorial-notes`,
so signing in on another device pulls them back. Without signing in they stay local.

## 5. Review

Completed lessons enter an Ebbinghaus queue:

```
1d → 2d → 4d → 7d → 15d → 30d → 60d → graduated
```

Due lessons show up under "Today's review" in the sidebar. It isn't nagging you to
study — it's pulling you back **at the inflection point of the forgetting curve**.

## 6. Next

- Want to author a textbook → [Write a book](../write-book/)
- Need format details → [Book format spec](../book-format/)
- Something wrong → [FAQ](../faq/)
"""},
        },
        {
            'slug': 'how-it-works',
            'title': {'zh': '学习机制', 'en': 'How learning works'},
            'desc': {'zh': '代码为什么能真跑、进度怎么算、复习怎么排、节奏守护是什么。',
                     'en': 'Why code runs, how progress is counted, how review is scheduled, and what the guardian does.'},
            'body': {
                'zh': """
## 代码是真跑的

正文里的 Python 代码块由 **Pyodide** 执行 —— CPython 编译成 WebAssembly，
跑在你的浏览器里。

这意味着：

- 有完整的标准库，`import` 真的能用
- 报错是真的 Python 报错，不是编造的
- 断网也能跑（Pyodide 加载过一次之后）

代价是首次加载要下载约 10MB 的运行时。之后浏览器会缓存。

## 进度怎么算

一课要**做完标了「计入学完」的题目**才算学完。随堂练习不计。

判定标准来自题目上的 `exam: true` 标记。作者出题时决定哪道算数，
所以一本书里"学完"的严格程度由作者控制。

## 艾宾浩斯复习

学完的课进入复习队列，间隔按这条曲线：

| 第几次复习 | 间隔 |
|---|---|
| 1 | 1 天 |
| 2 | 2 天 |
| 3 | 4 天 |
| 4 | 7 天 |
| 5 | 15 天 |
| 6 | 30 天 |
| 7 | 60 天 |
| 之后 | 毕业 |

答对了推进到下一档，答错退回上一档。**不是**简单的"学完就不管"。

## 节奏守护

连续学习超过一定时长会弹一个休息提醒。

这个设计的出发点很直接：编程教程最容易出现的失败模式不是学不会，
是**一次学太久然后彻底不想打开第二次**。提醒是为了让你明天还愿意回来。

可以在设置里关掉。

## 笔记同步

笔记存在你自己的私有仓库 `python-tutorial-notes`：

```
notes/
  {bookId}/
    {lessonId}.md
```

用 Git Data API 的 `commitTree` 一次提交，要么全成要么全不成，不会留下半截状态。
停止输入几秒后自动同步。
""",
                'en': """
## The code really runs

Python blocks are executed by **Pyodide** — CPython compiled to WebAssembly,
running inside your browser.

That means:

- The full standard library is there, `import` actually works
- Errors are real Python errors, not made up
- It works offline (once Pyodide has been loaded)

The cost is roughly a 10MB runtime download on first load. The browser caches it after that.

## How progress is counted

A lesson is complete when you **finish the questions marked "counts"**.
In-lesson practice doesn't count.

The rule comes from the `exam: true` flag on each question. The author decides which
ones count, so how strict "complete" is depends on the book.

## Ebbinghaus review

Finished lessons enter a review queue with these intervals:

| Review # | Interval |
|---|---|
| 1 | 1 day |
| 2 | 2 days |
| 3 | 4 days |
| 4 | 7 days |
| 5 | 15 days |
| 6 | 30 days |
| 7 | 60 days |
| after | graduated |

A correct answer advances you one step, a wrong one sends you back. This is **not**
a plain "done and forgotten".

## The guardian

Studying too long in one sitting triggers a break reminder.

The reasoning is blunt: the most common failure mode for a programming tutorial isn't
failing to understand it, it's **studying too long once and never opening it again**.
The reminder exists so you'll still want to come back tomorrow.

Turn it off in settings if you like.

## Note syncing

Notes live in your own private repository `python-tutorial-notes`:

```
notes/
  {bookId}/
    {lessonId}.md
```

They're committed with the Git Data API `commitTree` — one commit, all-or-nothing,
so you never end up with a half-written state. Auto-syncs a few seconds after you stop typing.
"""},
        },
        {
            'slug': 'book-format',
            'title': {'zh': '教材格式规范', 'en': 'Book format spec'},
            'desc': {'zh': 'albook.json、toc.json、课文与题目的字段要求。',
                     'en': 'Field requirements for albook.json, toc.json, lessons and questions.'},
            'body': {
                'zh': """
一个 AnyLearn 教材就是一个 GitHub 仓库，目录结构固定：

```
my-book/
  albook.json
  README.md
  content/
    zh/
      toc.json
      lessons/
        01.md
        02.md
        test-01.md
    en/
      toc.json
      lessons/
        01.md
```

## albook.json

必要字段：

| 字段 | 说明 |
|---|---|
| `format` | 必须**精确**等于 `al-book` |
| `id` | 小写字母、数字、连字符，如 `python-office` |
| `title` | 书名 |
| `subtitle` | 副标题 |
| `desc` | 简介 |
| `author` | 对象，至少含 `name` |
| `license` | 如 `CC BY-NC 4.0` |
| `level` | 难度 |
| `langs` | 数组，如 `["zh","en"]` |
| `tags` | 数组 |

可选字段：

| 字段 | 说明 |
|---|---|
| `kind` | `textbook`（默认）/ `novel` / `notes` / `other` |

`kind` 决定**是否强制要求题目数量**。写小说、写笔记就设成 `novel` 或 `notes`，
一道题没有也能发布。但有题就得是能判分的题 —— 合法性照样查。

## toc.json

```json
{
  "chapters": [
    {
      "title": "第 1 章 · 开始",
      "lessons": ["01", "02"],
      "test": "test-01"
    }
  ]
}
```

`lessons` 是文件名（不含 `.md`），`test` 是章测文件名。

## 课文

每篇课文是一个 Markdown 文件。约定：

- 第一个 `#` 是课标题
- 紧接着一段 `>` 引言
- 然后是正文
- 题目用 ```quiz 围栏写在文末

**题目围栏必须闭合** —— 结尾那个 ``` 要独占一行。少一个空行，
围栏就粘在正文后面，整道题读不出来。

## 题目

一个 quiz 块长这样（外层用四个反引号，这样里面的三反引号才能正常显示）：

````
```quiz
type: choice
q: 下面哪个能创建空列表？
options:
  - "[]"
  - "list()"
  - "以上都对"
answer: 2
exam: true
hint: 两种写法都对
explain: [] 和 list() 都创建空列表
```
````

`exam: true` 表示这道题**计入学完**。一课通常 1 道随堂 + 2 道测验。

题型的完整清单和判分机制见 [题型与判分](../quiz-types/)。
""",
                'en': """
An AnyLearn textbook is a GitHub repository with a fixed layout:

```
my-book/
  albook.json
  README.md
  content/
    zh/
      toc.json
      lessons/
        01.md
        02.md
        test-01.md
    en/
      toc.json
      lessons/
        01.md
```

## albook.json

Required fields:

| Field | Notes |
|---|---|
| `format` | must be **exactly** `al-book` |
| `id` | lowercase letters, digits, hyphens — e.g. `python-office` |
| `title` | book title |
| `subtitle` | subtitle |
| `desc` | description |
| `author` | object, at least `name` |
| `license` | e.g. `CC BY-NC 4.0` |
| `level` | difficulty |
| `langs` | array, e.g. `["zh","en"]` |
| `tags` | array |

Optional:

| Field | Notes |
|---|---|
| `kind` | `textbook` (default) / `novel` / `notes` / `other` |

`kind` decides **whether question counts are enforced**. Writing a novel or notes?
Set `novel` or `notes` and you can publish with zero questions. But if you do include
questions, they must be gradeable — validity is still checked.

## toc.json

```json
{
  "chapters": [
    {
      "title": "Chapter 1 · Getting started",
      "lessons": ["01", "02"],
      "test": "test-01"
    }
  ]
}
```

`lessons` holds filenames (without `.md`); `test` is the chapter-test filename.

## Lessons

Each lesson is a Markdown file. Conventions:

- The first `#` is the lesson title
- Followed immediately by a `>` lead paragraph
- Then the body
- Questions go at the end inside a ```quiz fence

**The fence must be closed** — the closing ``` needs its own line. Miss the blank
line and the fence glues itself to the last paragraph, and the whole question fails to parse.

## Questions

A quiz block looks like this (fenced with four backticks so the inner
triple-backtick block renders literally):

````
```quiz
type: choice
q: Which of these creates an empty list?
options:
  - "[]"
  - "list()"
  - "Both of the above"
answer: 2
exam: true
hint: Both forms work
explain: [] and list() both create an empty list
```
````

`exam: true` means the question **counts toward completion**. A lesson usually has
1 practice + 2 graded questions.

Full question types and grading rules: [Question types](../quiz-types/).
"""},
        },
        {
            'slug': 'quiz-types',
            'title': {'zh': '题型与判分', 'en': 'Question types & grading'},
            'desc': {'zh': '九种题型怎么出、怎么判分、以及最容易踩的坑。',
                     'en': 'All nine question types, how each is graded, and the easiest ways to get them wrong.'},
            'body': {
                'zh': """
## 选择题

```
type: choice
q: 题干
options:
  - "A"
  - "B"
answer: 1
```

`answer` 是**下标，从 0 开始**。多选题加 `multi: true`，answer 用逗号分隔：`0, 2`。

> 最常见的错：`answer` 写成 1 表示"第 1 个"。那其实是第二个选项。

## 填空题

```
type: fill
q: Python 里创建空字典用 __？
answer: {}
```

`|` 可以给多个可接受答案：`answer: dict()|{}`。

## 函数题

真调用你的函数、比对返回值。

```
type: func
q: 写一个 add(a, b) 返回两数之和
code: |
  def add(a, b):
      pass
cases: |
  1, 2 -> 3
  5, 7 -> 12
```

<div class="tip tip-bad">
<b>最容易踩的坑</b>
<p><code>cases</code> 的参数<b>必须用逗号分隔</b>。写 <code>1 2 -> 3</code> 会被当成"一个参数"，
调用变成 <code>add("1 2")</code>，报"缺少参数 b"。</p>
</div>

不能改成"空格也切"——那会破坏 `"hello world" -> 5` 这种单参数字符串用例。

## 随机结果题

结果本身是随机的（掷骰子、抽卡），判分只能验范围：

```
type: rand
q: 掷一个六面骰子
code: |
  import random
  def roll():
      return random.randint(1, 6)
cases: |
  *30 -> 1..6
```

`*30` 跑 30 次，`1..6` 是闭区间。

> `random.randrange(1, 6)` 是**开区间**，永远返回不到 6。要 `randrange(1, 7)`。

## 程序题

跑整段程序，对输出做断言：

```
type: code
q: 打印 1 到 5
code: |
  for i in range(1, 6):
      print(i)
checks:
  - __out contains "1"
  - __out contains "5"
```

## 网页三题型（html / css / js）

在沙箱 iframe 里渲染，用 `checks` 断言。

<div class="tip tip-warn">
<b>这几个断言永远不成立，别写</b>
<p>· <code>getComputedStyle(el).height === 'auto'</code> —— 算出来是像素值</p>
<p>· 期待 <code>:hover</code> 生效 —— JS 触发不了伪类</p>
<p>· 期待 <code>&lt;button&gt;</code> 默认字号是 14px —— 实际是 13.333px</p>
</div>

## 本地运行题（local / project）

没法自动判分，给一个清单自评：

```
type: local
q: 在本机跑通一个 Flask 服务
checklist:
  - 能启动
  - 能访问首页
```

## 通用字段

| 字段 | 说明 |
|---|---|
| `hint` | 提示，点一下才展开 |
| `explain` | 做完显示，讲为什么 |
| `exam` | `true` 表示计入学完 |
""",
                'en': """
## Multiple choice

```
type: choice
q: Question text
options:
  - "A"
  - "B"
answer: 1
```

`answer` is a **zero-based index**. For multiple answers add `multi: true` and use
comma-separated indices: `0, 2`.

> The classic mistake: writing `answer: 1` meaning "the first one". That's actually
> the second option.

## Fill in the blank

```
type: fill
q: In Python you create an empty dict with __
answer: {}
```

Use `|` for several acceptable answers: `answer: dict()|{}`.

## Function questions

Your function is actually called and the return value compared.

```
type: func
q: Write add(a, b) returning the sum
code: |
  def add(a, b):
      pass
cases: |
  1, 2 -> 3
  5, 7 -> 12
```

<div class="tip tip-bad">
<b>The easiest trap</b>
<p>Arguments in <code>cases</code> <b>must be comma-separated</b>. Writing
<code>1 2 -> 3</code> is read as a single argument, the call becomes
<code>add("1 2")</code>, and you get "missing argument b".</p>
</div>

"Just split on spaces too" isn't an option — it would break single-argument cases
like `"hello world" -> 5`.

## Random-result questions

When the result is inherently random (dice, card draws), grading can only check a range:

```
type: rand
q: Roll a six-sided die
code: |
  import random
  def roll():
      return random.randint(1, 6)
cases: |
  *30 -> 1..6
```

`*30` runs it 30 times, `1..6` is a closed interval.

> `random.randrange(1, 6)` is **half-open** and will never return 6. Use `randrange(1, 7)`.

## Program questions

Runs the whole program and asserts on the output:

```
type: code
q: Print 1 to 5
code: |
  for i in range(1, 6):
      print(i)
checks:
  - __out contains "1"
  - __out contains "5"
```

## Web questions (html / css / js)

Rendered in a sandboxed iframe, asserted via `checks`.

<div class="tip tip-warn">
<b>These assertions can never pass — don't write them</b>
<p>· <code>getComputedStyle(el).height === 'auto'</code> — resolves to a pixel value</p>
<p>· expecting <code>:hover</code> to apply — JS cannot trigger pseudo-classes</p>
<p>· expecting a <code>&lt;button&gt;</code>'s default font-size to be 14px — it's 13.333px</p>
</div>

## Local / project questions

Can't be auto-graded, so they carry a self-check list:

```
type: local
q: Run a Flask server locally
checklist:
  - It starts
  - The index page loads
```

## Common fields

| Field | Notes |
|---|---|
| `hint` | Shown on demand |
| `explain` | Shown after answering, explains why |
| `exam` | `true` means it counts toward completion |
"""},
        },
        {
            'slug': 'write-book',
            'title': {'zh': '怎么写一本书', 'en': 'Write a book'},
            'desc': {'zh': '三条路径：从文章导入、开发者平台手写、从已有书导入。',
                     'en': 'Three routes: import an article, write in the dev platform, or fork an existing book.'},
            'body': {
                'zh': """
## 路径一：从一篇 Markdown 导入（最快）

你已经有笔记、博客、讲稿？直接变成一本书。

开发者平台 → **「从文章导入」** → 粘贴 Markdown 或直接把 `.md` 拖进去。

拆分规则：

| 文章结构 | 拆成 |
|---|---|
| 有 h1 也有 h2 | h1 是章，h2 是课 |
| 只有 h1 | 每个 h1 一课 |
| 一个标题都没有 | 按 700 字切 |

导入后 `kind` 自动设成 `notes`（不要求题目），因为文章本来就没题。
想做成真教材，在「书籍信息」里改成 `textbook` 再加题。

<div class="tip tip-note">
<b>代码块里的 # 不会被当成标题</b>
<p>Python 注释写 <code># 错误写法</code> 很常见。如果扫标题时不跳过代码块，
一篇带注释的文章会被切成几十个"课"。</p>
</div>

## 路径二：开发者平台手写

开发者平台是三栏编辑器：左边章节树，中间写 Markdown，右边实时预览。

- 自由加章、给章加课，标题点着改
- 输入停 400ms 自动出预览
- **预览里的题目是真能做的** —— 选择题能选，函数题真调函数

预览题带 `__dev__:` 前缀隔离，**不写进学习进度、不触发复习排期**。
否则你试着做一道自己的草稿题，会被当成真实学习行为，污染进度。

### 题目库

顶栏「⊞ 题目库」有 11 个现成片段，点一下插到光标位置。
顶部开关决定插进来的是随堂还是计入学完的测验。

也可以把自己的题存成自定义片段 —— 选中一个 quiz 块点「存成自定义片段」，
存在你的私有草稿仓库 `al-drafts`，换设备能拉回来。

### 草稿存哪

第一次进开发者平台会自动创建 `你的用户名/al-drafts` **私有仓库**。
停止改动 3 秒后自动存云端，换设备点「从云端拉取」。

```
drafts/{id}/meta.json
drafts/{id}/lessons/01.md
drafts/{id}/lessons/test-01.md
```

## 路径三：从已有书导入

开发者平台 → 「从已有书导入」 → 贴 `owner/repo` 或从列表里选。

会生成一本新草稿，随便改。原作者信息保留 —— 按许可证署名。

## 三条路径之后

都要走同一套：[评审与发布](../publish/)。
""",
                'en': """
## Route 1: import a Markdown article (fastest)

Already have notes, a blog post, a talk script? Turn it into a book directly.

Dev platform → **"Import from article"** → paste Markdown or drop a `.md` file.

Splitting rules:

| Article structure | Becomes |
|---|---|
| Both h1 and h2 | h1 = chapter, h2 = lesson |
| Only h1 | each h1 is a lesson |
| No headings at all | chunked every 700 characters |

Imported books default to `kind: notes` (no question requirement), since an article
has none. To make it a real textbook, switch `kind` to `textbook` and add questions.

<div class="tip tip-note">
<b>A # inside a code block is not a heading</b>
<p>Writing <code># wrong way</code> as a Python comment is common. If heading scanning
doesn't skip code fences, one article with comments gets split into dozens of "lessons".</p>
</div>

## Route 2: write by hand in the dev platform

The dev platform is a three-pane editor: chapter tree on the left, Markdown in the
middle, live preview on the right.

- Add chapters and lessons freely, click titles to rename
- Preview refreshes 400ms after you stop typing
- **Questions in the preview actually work** — choices are clickable, functions really run

Preview questions are namespaced with a `__dev__:` prefix so they **don't write to
your progress and don't trigger review scheduling**. Otherwise testing your own draft
question would be recorded as real studying and pollute your progress.

### Snippet library

The "Snippet library" button in the top bar has 11 ready-made question templates;
click to insert at the cursor. A switch decides whether it's inserted as practice or
as a graded question.

You can also save your own questions as snippets — select a quiz block and click
"Save as snippet". They live in your private draft repo `al-drafts`, synced across devices.

### Where drafts live

The first time you open the dev platform it creates `yourname/al-drafts`, a **private
repository**. Auto-saves to the cloud 3 seconds after you stop editing; click "Pull
from cloud" on another device.

```
drafts/{id}/meta.json
drafts/{id}/lessons/01.md
drafts/{id}/lessons/test-01.md
```

## Route 3: import an existing book

Dev platform → "Import existing book" → paste `owner/repo` or pick from the list.

This creates a new draft you can edit freely. Original author info is kept — credit
per the license.

## After any of the three

All of them go through the same [review & publish](../publish/) flow.
"""},
        },
        {
            'slug': 'publish',
            'title': {'zh': '评审与发布', 'en': 'Review & publish'},
            'desc': {'zh': '评审报告怎么读、一键发布做了什么、发布后为什么搜不到。',
                     'en': 'How to read the review report, what publishing does, and why a book might not show up.'},
            'body': {
                'zh': """
## 评审报告

管理面板 → 「评审报告」，会跑一遍完整校验，列出所有错误和警告。

**错误会拦住发布，警告不会。** 但警告通常值得看一眼 —— 比如"课文只有 51 行，
可能是占位内容"，那多半就是真的没写完。

评审检查的东西：

- `albook.json` 的必填字段、`id` 是否合法
- `toc.json` 里声明的文件是否真的存在
- 每课的题目数量（教材要求 1 随堂 + 2 测验）
- 每道题的合法性：选择题下标越界、函数题 cases 格式、围栏是否闭合
- 中英题数是否一致

## 书名查重

发布前会查重，**官方和第三方都算**。比对前去空格、转小写、全角转半角：

| 输入 | 结果 |
|---|---|
| `Python 自动化办公` | 拦下（撞同名） |
| `python自动化办公` | 拦下（去空格后同名） |
| `ＰＹＴＨＯＮ自动化办公` | 拦下（全角转半角后同名） |

中文连写必须拦 —— 否则加个空格就能绕过，查重形同虚设。

## 一键发布做了什么

1. 校验内容
2. 创建仓库（公开或私有）
3. 用 `commitTree` **一次提交**所有文件
4. 打上 `topic: al-book`

<div class="tip tip-bad">
<b>为什么必须用 commitTree</b>
<p>早期版本用 contents API 并发推文件，结果：建仓时 GitHub 已生成 README，
再推就缺 sha 报 422；并发的后续请求基于过期 base 报 409。
<b>而错误被 catch 吞掉了，用户看到的是"发布成功"</b> —— 实际上 15 个文件只推上去 10 个。</p>
<p>改用 commitTree 后是原子提交，同一个场景缺失 0 个。推完还会拉回文件树核对。</p>
</div>

**只有公开的仓库会被收录。** 私有的你自己能看到，别人搜不到。

## 发布后搜不到？

按顺序排查：

1. **校验没过** —— 评审报告有错误的话，机器人不收录
2. **GitHub 搜索索引延迟** —— 新仓库、新 topic 要几分钟才进 `topic:al-book`
   （自己的书会立刻显示，因为发布时记了仓库名，不走搜索）
3. **仓库是私有的**

管理面板有「发布体检」，直接查已发布仓库缺什么文件、topic 在不在。

## 可见性

管理面板可以随时改公开 ↔ 私有。改私有会给它摘掉 `al-book` topic，
避免以后误公开又被扫到。
""",
                'en': """
## The review report

Management panel → "Review report" runs a full validation and lists every error and warning.

**Errors block publishing; warnings don't.** Warnings are still worth a glance —
"lesson is only 51 lines, may be placeholder" usually means it genuinely isn't finished.

What gets checked:

- Required `albook.json` fields, and whether `id` is legal
- Whether files declared in `toc.json` actually exist
- Question counts per lesson (a textbook wants 1 practice + 2 graded)
- Validity of every question: out-of-range choice indices, `cases` format, closed fences
- Whether the zh and en question counts match

## Title dedupe

Publishing checks for duplicate titles against **both official and third-party** books.
Before comparing, spaces are stripped, case folded, and full-width chars normalised:

| Input | Result |
|---|---|
| `Python Office Automation` | blocked (same title) |
| `pythonofficeautomation` | blocked (same after stripping spaces) |
| `ＰＹＴＨＯＮ...` | blocked (same after normalising full-width) |

Stripping spaces is essential — otherwise adding a space would defeat the whole check.

## What "publish" does

1. Validate content
2. Create the repository (public or private)
3. Push every file with `commitTree` — **one single commit**
4. Add the `topic: al-book` label

<div class="tip tip-bad">
<b>Why commitTree is mandatory</b>
<p>An early version pushed files concurrently via the contents API. Result: GitHub had
already created a README at repo creation, so re-pushing lacked a sha and returned 422;
concurrent follow-up requests used a stale base and returned 409.
<b>The errors were swallowed by a catch, so the user saw "published successfully"</b> —
while only 10 of 15 files actually landed.</p>
<p>With commitTree the commit is atomic: zero missing files in the same scenario. It
also re-reads the file tree afterwards to verify.</p>
</div>

**Only public repositories get indexed.** Private ones you can see yourself; nobody
else can find them.

## Can't find your book after publishing?

Check in order:

1. **Validation failed** — if the review report has errors, the bot won't index it
2. **GitHub search index lag** — new repos and new topics take a few minutes to appear
   under `topic:al-book` (your own books show immediately because the repo name is
   remembered at publish time and doesn't go through search)
3. **The repo is private**

The management panel has a "publish health check" that tells you exactly which files
are missing and whether the topic is set.

## Visibility

You can flip public ↔ private any time from the management panel. Switching to private
also removes the `al-book` topic, so it won't get picked up if you later make it public
by accident.
"""},
        },
        {
            'slug': 'faq',
            'title': {'zh': '常见问题', 'en': 'FAQ'},
            'desc': {'zh': '登录、额度、搜索、搜不到书这些高频问题。', 'en': 'Sign-in, rate limits, search, and missing books.'},
            'body': {
                'zh': """
## 一定要登录吗？

看官方教材不用。但**第三方教材要靠你的 token 去 GitHub 搜索**。

未认证 API 是 60 次/小时，搜一次书 + 取几个仓库的 `albook.json` 就快见底了。
登录后 5000 次/小时，而且能走 API 实时版（0.57s），不用等 CDN 缓存。

## Token 安全吗？

只写进浏览器 localStorage，从不外发。本站是纯静态页面，没有后端可以接收它。

建议用 **Fine-grained token**，只勾 `Contents: Read and write`，有效期 90 天。

## 为什么刷新后要卡一下登录页？

旧版本是"先联网验证通过才准进"，每次刷新都等 GitHub 往返。

现在改成：**有本地 token 就立刻进**，用户名头像先用缓存的，验证放后台悄悄做。
真失效了才弹回登录；网络不通只挂个提示条，不踢人。

## 搜索能搜什么？

**书名和目录**（章标题、课标题）。不搜正文。

这是刻意的选择：索引从 1.7MB 瘦到 176KB，打开就有结果，不用后台偷偷拉全文。
代价是只在正文里出现过的冷门词搜不到。

## 我的第三方书发布了却搜不到？

看 [评审与发布](../publish/) 里那一节。最常见的是**校验没过** ——
评审报告有错误的话机器人不收录。

## 一本书能有多少课？

没有硬限制。目录是按章组织的，一章可以有任意多课。

## 能写小说吗？

能。`albook.json` 里设 `"kind": "novel"`，就不要求题目数量了。

但有题就得是能判分的题 —— 合法性照样查。
""",
                'en': """
## Do I have to sign in?

Not for official textbooks. But **third-party books are found by searching GitHub with
your token**.

The unauthenticated API gives 60 requests/hour, which one search plus a few
`albook.json` fetches will nearly exhaust. Signed in: 5,000/hour, plus the real-time
API path (0.57s) instead of waiting on CDN cache.

## Is the token safe?

It's written to browser localStorage and never sent out. This site is static — there's
no backend that could receive it.

Use a **fine-grained token** with only `Contents: Read and write`, 90-day expiry.

## Why did refreshing used to hang on the sign-in page?

The old flow was "verify over the network before letting you in", so every refresh
waited on a round trip to GitHub.

Now: **if a local token exists you go straight in**, username and avatar come from
cache, verification happens quietly in the background. You only get bounced to sign-in
if it's genuinely invalid; if the network is down you just get a banner, not a logout.

## What does search cover?

**Titles and tables of contents** (chapter and lesson titles). Not body text.

That's deliberate: the index shrank from 1.7MB to 176KB, so results are instant with
no background full-text fetch. The cost is that a term appearing only in body text
won't be found.

## My third-party book was published but can't be found?

See the section in [Review & publish](../publish/). The most common cause is **failed
validation** — if the review report has errors, the bot won't index it.

## How many lessons can a book have?

No hard limit. Content is organised by chapter, and a chapter can hold any number.

## Can I write a novel instead?

Yes. Set `"kind": "novel"` in `albook.json` and question counts aren't enforced.

But any question you do include must be gradeable — validity is still checked.
"""},
        },
    ],
}
