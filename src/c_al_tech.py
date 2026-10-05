# -*- coding: utf-8 -*-
"""AnyLearn 技术文档 —— 中英双语。
所有描述均对照 js/ 下实际源码，不是凭印象写的。"""

AL_TECH = [
    {
        'slug': 'architecture',
        'title': {'zh': '整体架构', 'en': 'Architecture'},
        'desc': {'zh': '模块划分、启动顺序、数据存在哪。', 'en': 'Modules, boot order, and where data lives.'},
        'body': {
            'zh': """
AnyLearn 是一个**纯静态站点** —— 没有后端、没有数据库、没有一个属于自己的服务器。
所有状态要么在浏览器里，要么在你自己的 GitHub 仓库里。

## 模块划分

```
js/
├── app.js        路由、首页、课文渲染、进度与笔记（约 72KB）
├── dev.js        开发者平台：编辑器、发布、草稿云同步（约 113KB）
├── quiz.js       题型解析与判分（约 31KB）
├── runner.js     Pyodide 封装：真跑 Python（约 14KB）
├── web-runner.js HTML / CSS / JS 题的 iframe 预览与断言
├── bookcheck.js  发布前校验（约 13KB）
├── ide.js        课文里的代码编辑器
├── docs.js       Markdown 渲染
├── search.js     搜索索引与匹配
├── snippets.js   题目库片段
└── i18n/         zh.js / en.js
```

`dev.js` 之所以最大（113KB），是因为"写书"这件事本身比"读书"复杂：
编辑器、章节树、实时预览、评审报告、GitHub 发布、草稿云同步全在里面。

## 启动顺序有一处必须注意

```
docs.js → runner.js → web-runner.js → quiz.js → dev.js
```

`dev.js` 排在 **`quiz.js` 之后**。

这看着理所当然，但它曾经是反的 —— `dev.js` 被插在 `bookshelf.js` 后面，
也就是在 `quiz.js` **之前**。因为运行时才引用 `Quiz`，碰巧没报错。

**这是靠巧合活着的。** 顺序一旦变成"先加载后声明"，某次改动就会突然炸掉，
而且很难联想到是脚本顺序的问题。

## 数据存在哪

| 数据 | 位置 |
|---|---|
| Token、界面偏好 | 浏览器 `localStorage` |
| 学习进度、做题结果 | 你自己的 GitHub **私有仓库** |
| 笔记 | 同上，逐条合并 |
| 书籍草稿 | 私有仓库 `al-drafts` |
| 自定义片段 | `al-drafts/snippets.json` |

进度为什么不放 localStorage？**换台设备就没了。**
放进 GitHub 私有仓库，手机和电脑是同一份进度。

## 事件流

做题完成会广播 `quiz:done`，有两个监听者：

```
quiz:done → exam.js      判定"这一课学完了"
          → guardian.js  学习时长守护（弹休息提醒）
```

<div class="tip tip-warn">
<b>编辑器预览必须隔离</b>
<p>作者在编辑器里试做自己出的草稿题时，id 会带 <code>__dev__:</code> 前缀。
带前缀的题<b>不写进度、不广播事件</b>，但判分、提示、解释照常显示。</p>
<p>不隔离的话，试做一道草稿题就会被当成真实学习行为：污染进度、
污染艾宾浩斯排期，还可能突然弹一个"该休息了"。</p>
</div>

## 正文渲染

课文是 Markdown，走 `docs.js` 渲染。题目写在围栏块里：

````
```quiz
type: choice
q: 下面哪个是列表？
options:
  - [1,2,3]
  - "abc"
answer: 0
```
````

`quiz.js` 的 `extractBlocks()` 先把这些块抠出来解析成题目对象，
剩下的正文才交给 Markdown 渲染器。顺序不能反 ——
否则围栏内容会被当成代码块渲染掉。
""",
            'en': """
AnyLearn is a **purely static site** — no backend, no database, no server of its own.
All state lives either in your browser or in your own GitHub repositories.

## Modules

```
js/
├── app.js        routing, home, lesson rendering, progress & notes (~72KB)
├── dev.js        authoring platform: editor, publish, draft cloud sync (~113KB)
├── quiz.js       question parsing and grading (~31KB)
├── runner.js     Pyodide wrapper: actually running Python (~14KB)
├── web-runner.js iframe preview and assertions for HTML/CSS/JS questions
├── bookcheck.js  pre-publish validation (~13KB)
├── ide.js        the in-lesson code editor
├── docs.js       Markdown rendering
├── search.js     search index and matching
├── snippets.js   question snippet library
└── i18n/         zh.js / en.js
```

`dev.js` is the largest (113KB) because *writing* a book is inherently more complex
than reading one: editor, chapter tree, live preview, review report, GitHub publishing
and draft cloud sync all live there.

## Boot order — one thing to watch

```
docs.js → runner.js → web-runner.js → quiz.js → dev.js
```

`dev.js` comes **after** `quiz.js`.

That looks obvious now, but it used to be the other way around — `dev.js` was inserted
after `bookshelf.js`, i.e. **before** `quiz.js`. Since `Quiz` is only referenced at
runtime, it happened not to throw.

**That was luck, not correctness.** The moment load order became "used before defined",
some unrelated change would blow up — with nothing pointing at script order.

## Where data lives

| Data | Location |
|---|---|
| Token, UI preferences | browser `localStorage` |
| Progress, quiz results | your own GitHub **private repo** |
| Notes | same, merged item by item |
| Book drafts | private repo `al-drafts` |
| Custom snippets | `al-drafts/snippets.json` |

Why not localStorage for progress? **It vanishes on another device.**
In a GitHub private repo, your phone and your laptop share one progress state.

## Event flow

Finishing a question broadcasts `quiz:done`, which has two listeners:

```
quiz:done → exam.js      decides "this lesson is complete"
          → guardian.js  study-time guard (shows a break reminder)
```

<div class="tip tip-warn">
<b>Editor previews must be isolated</b>
<p>When an author tries out a draft question in the editor, its id carries a
<code>__dev__:</code> prefix. Prefixed questions <b>never write progress and never
broadcast events</b> — but grading, hints and explanations still work normally.</p>
<p>Without the isolation, test-solving a draft question counts as real studying: it
pollutes progress, corrupts the Ebbinghaus schedule, and might pop a "time to rest"
dialog out of nowhere.</p>
</div>

## Rendering

Lessons are Markdown, rendered by `docs.js`. Questions live in fenced blocks:

````
```quiz
type: choice
q: Which one is a list?
options:
  - [1,2,3]
  - "abc"
answer: 0
```
````

`quiz.js` `extractBlocks()` pulls these blocks out and parses them into question
objects first; only the remaining text goes to the Markdown renderer. The order can't
be reversed — otherwise the fence contents get rendered away as a plain code block.
"""},
    },
    {
        'slug': 'quiz-engine',
        'title': {'zh': '判分引擎', 'en': 'Grading engine'},
        'desc': {'zh': '题目怎么解析、怎么判分，以及为什么有些坑必须绕。',
                 'en': 'How questions are parsed and graded — and why some traps must be avoided.'},
        'body': {
            'zh': """
判分引擎在 `js/quiz.js`。它的职责是：把围栏块解析成题目对象 → 渲染成可交互的题 →
收集答案 → 判分 → 写进度。

## 参数切分：括号感知

函数题的用例长这样：

```
cases: |
  [1,2,3] -> [2,4,6]
  "a,b" -> "b,a"
```

按逗号切分参数是必然的 —— 但**不能切到括号里面**。

```js
function splitArgs(s) {
  const out = []; let depth = 0, cur = '';
  for (const ch of String(s)) {
    if (ch === '[' || ch === '(' || ch === '{') depth++;
    else if (ch === ']' || ch === ')' || ch === '}') depth--;
    if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; }
    else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}
```

不这样做，`[1,2,3]` 会被切成 `["[1", "2", "3]"]` 三块残片。

## 一个反直觉的决定：只按逗号切，不支持空格

曾经有作者（包括我自己写模板时）顺手写成 `1 2 -> 3`。
结果 `add("1 2")` 被调用，报「缺少参数 b」。

**为什么不改成"空格也切"**：那会破坏 `"hello world" -> 5` 这类单参数字符串用例。
字符串里天然有空格，一刀切下去所有带空格的字符串全废。

这是两害相权。现在的处理是三层：

1. 所有官方模板都用逗号
2. 校验器拦截：cases 里出现「有空格但没逗号、也不是引号或括号包起来」的行 → 报错
3. 编辑器预览当场标黄，不用等发布

## 字面量转换

用例写的是 Python 字面量，要转成 JS 值才能调用：

```js
function literal(s) {
  if (/^-?\\d+$/.test(s)) return parseInt(s, 10);
  if (s === 'True') return true;
  if (s === 'None') return null;
  if (s === 'true') return true;      // JS 题用小写字面量
  if (/^".*"$/.test(s)) return s.slice(1, -1);
  if (/^[[{]/.test(s)) {
    try { return JSON.parse(s.replace(/'/g, '"')); } catch (e) {}
    try { return JSON.parse(s); } catch (e2) {}
  }
  return s;
}
```

两套布尔值都要认 —— Python 题写 `True`，JavaScript 题写 `true`。

## 随机结果题：光判范围不够

掷骰子这类函数每次返回值都不同，没法用精确值比对。所以支持两种语法：

```
*20 -> 1..6       调用 20 次，每次结果都要落在 1~6
```

但**只判范围挡得住越界，挡不住假随机**：

```python
def roll(): return 3      # 每次都在 1~6 里，但它根本不是随机
```

所以区间用例还要检查**结果是否真的出现了多种不同的值**：

```python
__is_int = float(lo).is_integer() and float(hi).is_integer()
__span = int(hi) - int(lo) + 1 if __is_int else 0
if __is_int and 0 < __span <= 10:
    __need = set(range(int(lo), int(hi) + 1))
    __enough = __need.issubset({int(__x) for __x in __vals if __in_range(__x, lo, hi)})
    # 骰子这类：要求每个整数都出现过
else:
    __enough = len(__distinct) >= min(5, repeat)
    # 浮点或很宽的区间：至少 5 个不同值
```

整数且区间宽度 ≤ 10（骰子、硬币这种）要求**每个取值都出现过**；
其它情况（浮点、很宽的区间）至少 5 个不同值。

不这么卡，`return 3` 就能骗过所有测试。

## 程序题：把输出暴露成变量

程序题判的是"打印了什么"，不是"返回了什么"。做法是把 stdout 捕获下来，
塞进一个叫 `__out` 的变量：

```js
try { ns.set('__out', buf); } catch (e) { /* 某些 proxy 不支持 set */ }
```

然后测试就能写：

```python
assert "hello" in __out
```

## 网页题的判分在 iframe 里

HTML / CSS / JS 题走 `web-runner.js`：把用户的代码拼成一个完整文档塞进
`<iframe>`，然后在**隔离环境里**跑检查项。

有几类检查是**永远不成立**的，写题时要避开：

- `:hover` 伪类 —— JS 触发不了真实的鼠标悬停
- `getComputedStyle` 取 `height: auto` —— 算出来是具体像素值，不是 `auto`
- `<button>` 的默认字号 —— 各浏览器不统一（Chrome 是 13.333px）

## local 与 project 是自评

这两种题型**没有自动判分**（浏览器里没法验证"你在本地跑通了没有"）。
它们渲染成一个清单，作者勾完点「完成」。

校验器会把它们算进题数，但**不会去检查清单内容** —— 那本来就是主观的。
""",
            'en': """
The grading engine lives in `js/quiz.js`. Its job: parse a fenced block into a question
object → render it as something interactive → collect the answer → grade → write
progress.

## Argument splitting: bracket-aware

Function question cases look like this:

```
cases: |
  [1,2,3] -> [2,4,6]
  "a,b" -> "b,a"
```

Splitting arguments on commas is unavoidable — but it **must not split inside
brackets**.

```js
function splitArgs(s) {
  const out = []; let depth = 0, cur = '';
  for (const ch of String(s)) {
    if (ch === '[' || ch === '(' || ch === '{') depth++;
    else if (ch === ']' || ch === ')' || ch === '}') depth--;
    if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; }
    else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}
```

Without this, `[1,2,3]` would be cut into `["[1", "2", "3]"]`.

## A counter-intuitive decision: commas only, never spaces

At one point an author (myself, writing a template) casually wrote `1 2 -> 3`.
The result: `add("1 2")` got called and threw "missing argument b".

**Why not just also split on spaces**: that would break `"hello world" -> 5` — a single
string argument containing a space. Every space-containing string would break.

It's a trade-off. Current handling has three layers:

1. Every official template uses commas
2. The validator rejects case lines that contain spaces but no commas and aren't
   wrapped in quotes or brackets
3. The editor preview flags it inline, before publishing

## Literal conversion

Cases are written as Python literals and must become JS values:

```js
function literal(s) {
  if (/^-?\\d+$/.test(s)) return parseInt(s, 10);
  if (s === 'True') return true;
  if (s === 'None') return null;
  if (s === 'true') return true;      // JS questions use lowercase
  if (/^".*"$/.test(s)) return s.slice(1, -1);
  if (/^[[{]/.test(s)) {
    try { return JSON.parse(s.replace(/'/g, '"')); } catch (e) {}
    try { return JSON.parse(s); } catch (e2) {}
  }
  return s;
}
```

Both boolean spellings must be accepted — Python questions write `True`, JavaScript
ones write `true`.

## Random-result questions: range alone isn't enough

A dice-roll function returns something different every call, so exact comparison is
impossible. Two pieces of syntax handle it:

```
*20 -> 1..6       call 20 times, every result must land in 1..6
```

But **range checks stop out-of-bounds, not fake randomness**:

```python
def roll(): return 3      # always in 1..6, but it isn't random at all
```

So range cases also verify that **multiple distinct values actually appeared**:

```python
__is_int = float(lo).is_integer() and float(hi).is_integer()
__span = int(hi) - int(lo) + 1 if __is_int else 0
if __is_int and 0 < __span <= 10:
    __need = set(range(int(lo), int(hi) + 1))
    __enough = __need.issubset({int(__x) for __x in __vals if __in_range(__x, lo, hi)})
    # dice-like: every integer must appear
else:
    __enough = len(__distinct) >= min(5, repeat)
    # floats or wide ranges: at least 5 distinct values
```

Integer ranges with span ≤ 10 (dice, coins) require **every value to appear**; otherwise
(floats, wide ranges) at least 5 distinct values.

Without this, `return 3` passes every test.

## Program questions: expose output as a variable

These grade "what did you print", not "what did you return". stdout is captured and
pushed into a variable named `__out`:

```js
try { ns.set('__out', buf); } catch (e) { /* some proxies don't support set */ }
```

So tests can be written as:

```python
assert "hello" in __out
```

## Web questions grade inside an iframe

HTML / CSS / JS questions go through `web-runner.js`: the user's code is assembled into
a full document, loaded into an `<iframe>`, and checks run in that **isolated context**.

Some checks can **never** pass — avoid them when authoring:

- `:hover` pseudo-class — JS can't trigger a real mouse hover
- `getComputedStyle` reading `height: auto` — resolves to a pixel value, never `auto`
- default font size of `<button>` — inconsistent across browsers (Chrome: 13.333px)

## `local` and `project` are self-assessed

These two types have **no automatic grading** (a browser can't verify "did you actually
run this locally"). They render as a checklist the learner ticks and confirms.

The validator counts them toward question totals but **never inspects the checklist
contents** — that's inherently subjective.
"""},
    },
    {
        'slug': 'code-runner',
        'title': {'zh': '代码执行沙箱', 'en': 'Code execution sandbox'},
        'desc': {'zh': 'Pyodide 怎么加载、命名空间怎么隔离、输出怎么捕获。',
                 'en': 'How Pyodide loads, how namespaces are isolated, how output is captured.'},
        'body': {
            'zh': """
`js/runner.js` 封装 Pyodide，让 Python 真的在浏览器里跑。

## 加载

```js
const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/';
pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
```

Pyodide 本体约 6MB（压缩后），**只在第一次跑 Python 题时才加载**。
纯选择题、填空题的课文不会付这个代价。

标准库开箱可用 —— `import math`、`import json` 随便用。
第三方包要显式声明：

```js
if (want.length) await pyodide.loadPackage(want);
```

## 命名空间隔离

每道题、每课都用一个**全新的 globals dict**：

```js
ns = pyodide.runPython('{}');   // 新建空的 globals dict
```

不隔离会怎样？上一题定义的 `add` 还留在命名空间里，
学生交一个空的答案也能"通过" —— 因为函数还在。

切换课文时也会重建：

```js
if (!pyodide || nsOwner === lessonId) return;
```

## 输出捕获

```js
pyodide.setStdout({ batched: s => { buf += s + '\\n'; } });
pyodide.setStderr({ batched: s => { buf += s + '\\n'; } });
```

`batched` 表示每次收到一段文本就回调一次（而不是等全部结束）。

捕获下来的内容有两个用处：

1. 显示在输出区
2. 塞进 `__out` 变量，供程序题的 assert 使用

## stdin 也要接管

```js
pyodide.setStdin({ ... });
```

不接管的话，`input()` 会挂住 —— 浏览器没有默认的 stdin，
Pyodide 会一直等一个永远不来的输入，**页面看起来就是卡死了**。

## 返回值怎么拿

```js
const result = pyodide.runPython(code, { globals: ns });
...
const rep = pyodide.globals.get('repr')(result);
```

用 `repr()` 而不是 `str()`，因为对字符串来说：

```
str("abc")   → abc
repr("abc")  → 'abc'
```

判分时看得到引号，才能区分 `abc` 和 `'abc'` —— 否则一个返回字符串 `1`
的函数和一个返回整数 `1` 的函数会被判成一样。

超长结果会截断（>60 字符），否则输出区会被一个巨大的列表撑爆。

## 为什么会失败

| 现象 | 原因 |
|---|---|
| 点运行没反应 | Pyodide 首次加载中（6MB），等一下 |
| `ModuleNotFoundError` | 第三方包需要在题里声明 |
| 页面卡住不动 | 代码里有 `input()` 或死循环 |
| 判分说"函数没定义" | 函数名拼错，或 starter 里根本没定义 |

死循环目前没有超时机制 —— 这是已知限制。
Pyodide 跑在主线程，死循环会真的把标签页卡住。
""",
            'en': """
`js/runner.js` wraps Pyodide so Python actually runs in the browser.

## Loading

```js
const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/';
pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
```

Pyodide itself is ~6MB (compressed) and is **loaded lazily** — only when a Python
question is actually run. Lessons with only choice or fill-in questions never pay that
cost.

The standard library works out of the box — `import math`, `import json`, anything.
Third-party packages must be declared explicitly:

```js
if (want.length) await pyodide.loadPackage(want);
```

## Namespace isolation

Every question and every lesson gets a **brand-new globals dict**:

```js
ns = pyodide.runPython('{}');   // fresh empty globals dict
```

What happens without it? The `add` defined in the previous question is still in the
namespace, so a student submitting an empty answer still "passes" — the function is
still there.

It's also rebuilt when switching lessons:

```js
if (!pyodide || nsOwner === lessonId) return;
```

## Capturing output

```js
pyodide.setStdout({ batched: s => { buf += s + '\\n'; } });
pyodide.setStderr({ batched: s => { buf += s + '\\n'; } });
```

`batched` means the callback fires on each chunk of text rather than at the very end.

The captured text serves two purposes:

1. Displayed in the output pane
2. Pushed into the `__out` variable for program-question asserts

## stdin must be handled too

```js
pyodide.setStdin({ ... });
```

Skip this and `input()` hangs — a browser has no default stdin, so Pyodide waits
forever for input that will never arrive. **The page just looks frozen.**

## Getting the return value

```js
const result = pyodide.runPython(code, { globals: ns });
...
const rep = pyodide.globals.get('repr')(result);
```

`repr()` rather than `str()`, because for strings:

```
str("abc")   → abc
repr("abc")  → 'abc'
```

Seeing the quotes is what lets grading distinguish `abc` from `'abc'` — otherwise a
function returning the string `1` and one returning the integer `1` look identical.

Very long results are truncated (>60 chars), otherwise one huge list blows up the
output pane.

## Why things fail

| Symptom | Cause |
|---|---|
| Run button does nothing | Pyodide is loading for the first time (~6MB); wait |
| `ModuleNotFoundError` | A third-party package must be declared in the question |
| Page freezes | Your code has `input()` or an infinite loop |
| "Function not found" | Misspelled name, or the starter never defined it |

Infinite loops currently have no timeout — a known limitation. Pyodide runs on the main
thread, so a real infinite loop genuinely locks up the tab.
"""},
    },
    {
        'slug': 'storage-sync',
        'title': {'zh': '进度与笔记同步', 'en': 'Progress and note sync'},
        'desc': {'zh': '数据存在你的私有仓库里，多设备怎么不互相抹掉。',
                 'en': 'Data lives in your private repo — how multiple devices avoid clobbering each other.'},
        'body': {
            'zh': """
进度和笔记存在**你自己的 GitHub 私有仓库**里，不是本站的数据库（本站没有数据库）。

## 为什么放 GitHub 而不放 localStorage

localStorage 的问题是**换设备就没了**。手机上学完，电脑上打开是空的。

放 GitHub 私有仓库：

- 手机和电脑共享同一份进度
- 数据是你的，本站关了也在
- 本站服务器（其实只有静态文件）看不到你的进度

## 笔记的合并策略：LWW

笔记逐条采用 **Last-Write-Wins**（最后写入者胜）：

```
每条笔记 = { id, text, updatedAt, deleted }
```

同步时按 `id` 合并，同一条取 `updatedAt` 更大的那个。

为什么不做三路合并或 CRDT？笔记是**短文本、低冲突**的。
同一条笔记在两台设备上同时编辑的概率很低，为这个上 CRDT 不划算。

<div class="tip tip-note">
<b>删除是软删除</b>
<p>删笔记写的是 <code>deleted: true</code>，不是真的移除记录。
否则"这边删了、那边没删"的同步会让删掉的内容复活 ——
因为对端不知道它已经被删了。</p>
</div>

## 进度的数据结构

```
Store.K.PROGRESS  每课完成状态
Store.K.QUIZ      每道题的作答结果
Store.K.NOTES     笔记
```

做题结果会触发 `quiz:done`，`exam.js` 据此判定一课是否学完。

## 冲突时的表现

两台设备都离线学完同一课，然后先后联网：

- 后同步的那台**不会覆盖**先同步的
- 完成的课取并集（都算完成）
- 笔记按 `updatedAt` 取新

进度是"学会了就是学会了"，没有回退场景 —— 所以并集是对的。

## 未登录也能用

不登录可以读官方教材、跑代码、做题 —— 只是**不保存进度**（没有仓库可写）。

登录后才往仓库同步。这个设计让"先试试看"没有任何门槛。

## 已知限制

| 限制 | 说明 |
|---|---|
| 离线太久 | 两台设备各自积累的改动，同步时按上面的规则合并，可能丢少量笔记 |
| 仓库权限 | Token 必须有 `Contents: Read and write` |
| 频率 | 每次提交是一笔 API 请求，5000 次/小时的配额够用，但连续刷题会频繁写 |

笔记同步是**写完即推**，不是定时批量 —— 关页面前不用等。
""",
            'en': """
Progress and notes live in **your own GitHub private repository**, not in a database of
ours (there is no database).

## Why GitHub instead of localStorage

The problem with localStorage is that **it disappears on another device**. Study on your
phone, open your laptop, and it's empty.

In a GitHub private repo:

- Phone and laptop share one progress state
- The data is yours — it survives this site disappearing
- Our "server" (static files only) never sees your progress

## Note merge strategy: LWW

Notes are merged item by item using **Last-Write-Wins**:

```
each note = { id, text, updatedAt, deleted }
```

On sync, merge by `id`; for the same id, take the larger `updatedAt`.

Why not three-way merge or a CRDT? Notes are **short, low-conflict text**. The chance of
editing the same note on two devices at once is tiny — a CRDT isn't worth it here.

<div class="tip tip-note">
<b>Deletes are soft</b>
<p>Deleting a note writes <code>deleted: true</code> rather than removing the record.
Otherwise a "deleted here, not there" sync resurrects the content — the other side has no
way to know it was deleted.</p>
</div>

## Progress data structures

```
Store.K.PROGRESS  completion state per lesson
Store.K.QUIZ      answer result per question
Store.K.NOTES     notes
```

Answering a question fires `quiz:done`, which `exam.js` uses to decide whether a lesson
is complete.

## What conflict looks like

Two devices both finish the same lesson offline, then come online one after the other:

- The later sync **does not overwrite** the earlier one
- Completed lessons are unioned (both count as done)
- Notes take whichever `updatedAt` is newer

Progress means "learned is learned" — there's no un-learning, so a union is correct.

## Works without signing in

You can read official textbooks, run code and answer questions while signed out —
progress just isn't saved (there's no repo to write to).

Syncing starts once you sign in. That keeps "try before committing" friction-free.

## Known limitations

| Limitation | Detail |
|---|---|
| Long offline stretches | Changes accumulated on two devices merge per the rules above; a few notes may be lost |
| Repo permission | Token needs `Contents: Read and write` |
| Rate | Every write is an API request; 5000/hour is plenty, but rapid-fire studying writes often |

Note sync is **write-through**, not batched on a timer — no need to wait before closing
the tab.
"""},
    },
]
