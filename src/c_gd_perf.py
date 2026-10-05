# -*- coding: utf-8 -*-
"""GitHub Drive 传输性能 —— 实测数据与分片算法。
所有数字都是真跑出来的（private 仓库 gd-bench-tmp，随机不可压缩数据）。"""

GD_PERF = [
    {
        'slug': 'transfer-tuning',
        'title': {'zh': '传输性能与分片算法', 'en': 'Transfer tuning'},
        'desc': {'zh': '实测 512KB 到 1GB 的上传速度，以及推导出的分片算法。',
                 'en': 'Measured upload speed from 512KB to 1GB, and the chunking algorithm derived from it.'},
        'body': {
            'zh': """
这一页的数字全部是**真跑出来的**：建一个私有仓库，用 `os.urandom()` 生成
不可压缩的随机数据，实打实传到 GitHub API 上计时。测完仓库已删除。

## 实测结果

采用本文的算法（并发 4）：

| 文件 | 分片 | 片数 | 总耗时 | 吞吐 |
|---|---|---|---|---|
| 512KB | 直传 | 1 | 2.50s | 0.20 MB/s |
| 1MB | 直传 | 1 | 2.82s | 0.35 MB/s |
| 8MB | 2MB | 4 | 11.85s | 0.68 MB/s |
| 128MB | 32MB | 4 | 24.89s | 5.14 MB/s |
| 256MB | 32MB | 8 | 41.06s | 6.23 MB/s |
| 512MB | 32MB | 16 | 66.23s | **7.73 MB/s** |
| 1GB | 32MB | 32 | 136.72s | 7.49 MB/s |

吞吐从 512KB 的 0.2MB/s 涨到 1GB 的 7.5MB/s，差 **37 倍**。

原因很简单：**小文件的耗时几乎全是固定开销** —— 一次 HTTPS 握手、
一次 API 响应，跟传多少数据关系不大。512KB 和 1MB 都是 2.5~2.8 秒，
就是同一笔固定开销。

所以"上传慢"这个体感，在小文件上根本不是带宽问题。

## 三个硬约束（都是实测撞出来的）

### 一、单个 blob 上限约 38MB

```
32MB 原始 → base64 后 42.7MB → ✓
39MB 原始 → base64 后 52.0MB → ✓
40MB 原始 → base64 后 53.3MB → ✗ 422 "your input was too large"
```

限制卡在 **base64 之后的 payload** 大小，不是原始字节。
base64 有 33% 膨胀，所以 32MB 原始 ≈ 42.7MB payload。

算法里取 **32MB** 作上限，留 6MB 余量。

### 二、并发有帮助，但有上限

同一个 16MB，不同并发度：

```
串行（并发1）  45.53s   0.70 MB/s
并发 4         11.51s   2.78 MB/s
```

并发 4 相比串行快 **4 倍**。再往上加（8、16）收益很小 ——
瓶颈已经不在本地的并行度，而在 GitHub 那一侧。

所以并发度定死 **4**。

### 三、commit 是固定约 5.7 秒，与文件数无关

```
4 个文件    tree 5.74s  commit 5.74s
16 个文件   tree 0.90s  commit 5.71s
64 个文件   tree 1.30s  commit 5.68s
```

**commit 那 5.7 秒是付给"一笔提交"的，不管你提交 4 个还是 64 个文件。**

这条决定了算法的方向：**批次数越少越好**。
256MB 那次如果按 128 条一批会变成 2 次 commit，白白多付 5.7 秒。

## 算法

```python
MIN_DIRECT = 1 * 1024 * 1024    # 小于这个直传，不切
MAX_CHUNK  = 32 * 1024 * 1024   # blob 上限留余量
MIN_CHUNK  = 1 * 1024 * 1024
TREE_MAX   = 128                # 单次 tree 条目数（保守）
CONCURRENCY = 4

def plan(size):
    if size <= MIN_DIRECT:
        return size, 1, 1, True          # 直传 contents API
    chunk = size / CONCURRENCY           # 片数 ≈ 并发数
    chunk = max(MIN_CHUNK, min(MAX_CHUNK, chunk))
    n = ceil(size / chunk)
    batches = ceil(n / TREE_MAX)
    return chunk, n, batches, False
```

### 为什么片数 ≈ 并发数，而不是更多

这是我一开始写错的地方。第一版让片数 = 并发数 × 3，想着"多几轮让流水线更饱和"。

实测打脸：

```
16MB，13 片（每片 1.33MB） → 16.68s
16MB，4 片（每片 8MB）     →  8.82s
```

**每片都有 1~2 秒的固定开销，是按片数付的。**

片数只要 ≥ 并发数就能吃满并发，再多无益 —— 只是多付固定开销。

### 为什么不固定一个"最佳分片大小"

因为最佳值随文件大小变。固定 512KB 的话，1GB 会切成 2048 片，
光固定开销就要 2000 多秒。

## 对比旧的 512KB 默认

同一个 16MB 文件，两种策略：

```
旧：512KB 分片，32 片   60.75s   0.26 MB/s
新：4MB 分片，4 片      11.77s   1.36 MB/s
```

**快 5.2 倍。**

而且这还是 16MB 的小文件。1GB 的差距会大得多 —— 512KB 分片要切 2048 片。

<div class="tip tip-warn">
<b>旧文档写的"10MB 才分片"是错的</b>
<p>默认值一直是 512KB，超过 512KB 就切。源码注释里有这条订正，
但代码行为一直没改 —— 直到这次实测才动。</p>
</div>

## 线上实装前后的真实对比

上面是 Python 侧的对照实验。真正改到 `github_drive` 里之后，
又跑了一次**完全真实的前后对比** —— 同一个 8MB 文件，同一台机器：

```
旧实现（512KB 固定分片，串行，每片一次完整提交）
  16 片   88.75s   0.09 MB/s   112 次 API 调用

新实现（动态分片，并发 4，全部挤进一次 tree + commit）
  4 片    15.67s   0.51 MB/s     9 次 API 调用
```

**快 5.7 倍，API 调用减少 12 倍。**

调用数从 112 降到 9 的原因，是旧实现每个分片要跑完整一套提交流程：

```
getRef → getCommit → createBlob → createTree → createCommit → updateRef
                                            → 再 getFileContents 拿 sha
                                              = 每片 7 次请求
```

新实现把后四步从"每片一次"改成"每个仓库一次"，
并直接用 blob 的 sha（已实测它与 contents API 的文件 sha 完全相同），
省掉最后那次查询。

```python
# 200MB 真实上传（并发 4，7 片 × 32MB）
POST blobs ×7 · GET ref ×1 · GET commit ×1 · POST tree ×1 · POST commit ×1 · PATCH ref ×1
= 12 次调用  25.29s  7.91 MB/s  ✓ 回读逐字节一致
```

## 并发到底该开多大：实测拐点

用第二个账号做了一轮**多组重复、取中位数**的测试（单次测量噪声很大，
同一配置能差 2 倍，所以每组跑 3 次取中位数）。

64MB，固定并发 4，只变片数：

```
16MB × 4 片    7.89s   8.11 MB/s   ← 最快
8MB  × 8 片   12.04s   5.31 MB/s
4MB  × 16 片  28.05s   2.28 MB/s   ← 慢 3.5 倍
```

**片数越少越快，即使单片变大。** 这跟"多分片能更好并行"的直觉相反——
因为每片那 1~2 秒固定开销是按片数付的，而单片变大后传输本身几乎不增加耗时
（带宽不是瓶颈）。

并发本身确实有用，看看 4MB × 16 片这组：

```
并发 4    28.05s   2.28 MB/s
并发 8    12.84s   4.98 MB/s
并发 16    8.59s   7.45 MB/s
```

但**再往上会劣化**：单独测过并发 24，从 14.63s 掉到 20.52s。GitHub 那一侧
开始拒绝排队，重试反而拖慢整体。所以并发硬上限定 **16**。

综合两组数据的结论：

```
片数 ≈ 4（尽量少）  →  决定了大部分收益
并发 = 片数，但不超过 16  →  次要收益
```

## 三个参数怎么同时定：内存也是约束

并发数不能只看速度，还得看内存。base64 膨胀 1.34 倍，同时编码 N 个分片
就要 `N × chunkSize × 1.34` 字节。

所以算法分三步：

```python
chunkSize = clamp(size / 4, MIN_CHUNK=1MB, MAX_CHUNK=32MB)
totalChunks = ceil(size / chunkSize)
maxByMemory = floor(MEM_BUDGET / (chunkSize * 1.34))   # 默认预算 512MB
concurrency = min(totalChunks, maxByMemory, HARD_CONC=16)
```

**这三个参数是互相牵制的** —— 单片越大，内存允许的同时编码数就越少：

| 文件 | 单片 | 片数 | 并发 | 批次 | 峰值内存 |
|---|---|---|---|---|---|
| 8MB | 2MB | 4 | 4 | 1 | 11MB |
| 64MB | 16MB | 4 | 4 | 1 | 86MB |
| 256MB | 32MB | 8 | 8 | 1 | 343MB |
| 512MB | 32MB | 16 | **11** | 2 | 472MB |
| 1GB | 32MB | 32 | **11** | 3 | 472MB |
| 4GB | 32MB | 128 | **11** | 12 | 472MB |

512MB 以上，并发被**内存**压到 11 而不是 16 —— 32MB 的片同时编码 16 个
要 672MB，实测会被系统杀掉。这就是为什么并发上限不能写死。

## 自适应前后对比

| 文件 | 旧（512KB 固定） | 新（自适应） | 提升 |
|---|---|---|---|
| 8MB | 88.75s · 112 次 | 15.67s · 9 次 | 5.7× |
| 16MB | 182.09s · 224 次 | 11.53s · 9 次 | **15.8×** |
| 128MB | ~41 分（外推） | **15.74s** · 9 次 | ~156× |
| 512MB | ~1.6 小时（外推） | 66.23s | ~88× |
| 1GB | ~3.2 小时（外推） | 136.72s | ~85× |

128MB 那次 **9 次 API 调用、15.74 秒、8.13 MB/s**，回读逐字节一致。

## 内存：不能一次性全编码

512MB 文件按 32MB 分片是 16 片，每片 base64 后 42MB。
**一次性全编码就是 16 × 42MB = 672MB 的 Python 字符串同时在内存里。**

我第一版就是这么写的，512MB 直接被系统杀掉（没有任何报错，进程没了）。

改成逐批：一次只把 `CONCURRENCY` 片的 base64 放内存，传完立刻释放。

```python
for start in range(0, n, CONCURRENCY):
    batch = [data[i*chunk:(i+1)*chunk] for i in range(start, min(start+CONCURRENCY, n))]
    b64s = [base64.b64encode(p).decode() for p in batch]
    del batch                      # 原始数据立刻释放
    ...并发上传...
    del b64s                       # base64 也立刻释放
```

## 完整性验证

光测速度没用，得确认数据没坏。传完立刻回读比对：

```
源数据   sha256 d19cfccc01fdda93…  16777216 字节
回读数据 sha256 d19cfccc01fdda93…  16777216 字节
结果：✓ 逐字节一致
```

是**下载回来逐字节比对**的，不是只看 API 返回 200。

## 失败重试不能只认 429

大文件传输中会遇到 **500**（不是 502/503），一开始没覆盖：

```python
if e.code in (429, 500, 502, 503):   # 500 也要重试
    time.sleep(5 * (attempt + 1))
```

256MB 那次就是这么挂的 —— 第一次跑直接报 500 失败，加上重试后成功。

## 一句话总结

```
小文件（≤1MB）直传，别切
大文件：片数 = 并发数（4），单片封顶 32MB
并发上传，一次只编码一批
所有分片放进一次 tree + 一次 commit
```

前三条省的是固定开销，最后一条省的是那 5.7 秒。
""",
            'en': """
Every number on this page was **actually measured**: a private repo was created, filled
with incompressible random data from `os.urandom()`, and timed against the real GitHub
API. The repo was deleted afterwards.

## Measured results

Using the algorithm on this page (concurrency 4):

| File | Chunk | Chunks | Total | Throughput |
|---|---|---|---|---|
| 512KB | direct | 1 | 2.50s | 0.20 MB/s |
| 1MB | direct | 1 | 2.82s | 0.35 MB/s |
| 8MB | 2MB | 4 | 11.85s | 0.68 MB/s |
| 128MB | 32MB | 4 | 24.89s | 5.14 MB/s |
| 256MB | 32MB | 8 | 41.06s | 6.23 MB/s |
| 512MB | 32MB | 16 | 66.23s | **7.73 MB/s** |
| 1GB | 32MB | 32 | 136.72s | 7.49 MB/s |

Throughput climbs from 0.2MB/s at 512KB to 7.5MB/s at 1GB — a **37×** spread.

The reason is simple: **for small files the time is almost entirely fixed overhead** —
one TLS handshake, one API round-trip — barely related to payload size. 512KB and 1MB
both take 2.5–2.8s because both pay the same fixed cost.

So "uploading feels slow" on small files is never a bandwidth problem.

## Three hard limits (all found by hitting them)

### 1. A single blob caps out around 38MB

```
32MB raw → 42.7MB base64 → ✓
39MB raw → 52.0MB base64 → ✓
40MB raw → 53.3MB base64 → ✗ 422 "your input was too large"
```

The limit applies to the **post-base64 payload**, not raw bytes. Base64 inflates by 33%,
so 32MB raw ≈ 42.7MB payload.

The algorithm caps chunks at **32MB**, leaving 6MB of headroom.

### 2. Concurrency helps, but plateaus

Same 16MB, different concurrency:

```
serial (conc 1)   45.53s   0.70 MB/s
concurrency 4     11.51s   2.78 MB/s
```

Concurrency 4 is **4× faster than serial**. Beyond that (8, 16) the gain is marginal —
the bottleneck is no longer local parallelism but GitHub's side.

So concurrency is pinned at **4**.

### 3. A commit costs ~5.7s regardless of file count

```
4 files     tree 5.74s  commit 5.74s
16 files    tree 0.90s  commit 5.71s
64 files    tree 1.30s  commit 5.68s
```

**Those 5.7 seconds are paid per commit**, whether you commit 4 files or 64.

That single fact sets the algorithm's direction: **minimise the number of batches**.
A 256MB upload split 128-per-batch would mean 2 commits and 5.7 wasted seconds.

## The algorithm

```python
MIN_DIRECT = 1 * 1024 * 1024    # below this: upload directly, don't chunk
MAX_CHUNK  = 32 * 1024 * 1024   # blob cap with headroom
MIN_CHUNK  = 1 * 1024 * 1024
TREE_MAX   = 128                # tree entries per call (conservative)
CONCURRENCY = 4

def plan(size):
    if size <= MIN_DIRECT:
        return size, 1, 1, True          # direct via contents API
    chunk = size / CONCURRENCY           # chunk count ≈ concurrency
    chunk = max(MIN_CHUNK, min(MAX_CHUNK, chunk))
    n = ceil(size / chunk)
    batches = ceil(n / TREE_MAX)
    return chunk, n, batches, False
```

### Why chunk count ≈ concurrency, not more

This is where I got it wrong first. Version one used `concurrency × 3`, reasoning that
"a few extra rounds keep the pipeline saturated".

Measurement disagreed:

```
16MB, 13 chunks (1.33MB each) → 16.68s
16MB, 4 chunks  (8MB each)    →  8.82s
```

**Every chunk carries 1–2 seconds of fixed overhead, paid per chunk.**

Once chunk count ≥ concurrency the pipeline is saturated; more chunks only add fixed
cost.

### Why not just hard-code one "best" chunk size

Because the optimum moves with file size. A fixed 512KB would cut 1GB into 2048 chunks —
over 2000 seconds of pure fixed overhead.

## Versus the old 512KB default

Same 16MB file, two strategies:

```
old: 512KB chunks, 32 of them   60.75s   0.26 MB/s
new: 4MB chunks, 4 of them      11.77s   1.36 MB/s
```

**5.2× faster.** And that's on a small 16MB file — at 1GB the gap is far wider, since
512KB chunking means 2048 pieces.

<div class="tip tip-warn">
<b>The old docs saying "split at 10MB" were wrong</b>
<p>The default was always 512KB — anything over 512KB got split. The source comment
carried the correction, but the behaviour never changed until these measurements.</p>
</div>

## Real before/after on the actual app

The numbers above come from a Python-side controlled experiment. After porting the
algorithm into `github_drive`, a **fully real before/after** was measured — same 8MB
file, same machine:

```
old implementation (fixed 512KB chunks, serial, one full commit per chunk)
  16 chunks   88.75s   0.09 MB/s   112 API calls

new implementation (dynamic chunks, concurrency 4, everything in one tree + commit)
  4 chunks    15.67s   0.51 MB/s     9 API calls
```

**5.7× faster, 12× fewer API calls.**

Calls dropped from 112 to 9 because the old code ran a full commit sequence per chunk:

```
getRef → getCommit → createBlob → createTree → createCommit → updateRef
                                            → then getFileContents just for the sha
                                              = 7 requests per chunk
```

The new one moves the last four steps from "per chunk" to "per repo", and uses the blob
sha directly (verified identical to the contents API file sha), dropping that final
lookup.

```python
# real 200MB upload (concurrency 4, 7 chunks × 32MB)
POST blobs ×7 · GET ref ×1 · GET commit ×1 · POST tree ×1 · POST commit ×1 · PATCH ref ×1
= 12 calls   25.29s  7.91 MB/s  ✓ readback byte-identical
```

## How much concurrency is right: the measured inflection point

A round of **repeated, median-of-3** tests was run on a second account. Single
measurements are extremely noisy — the same config varies by 2× — so every
configuration was run three times and the median taken.

64MB, concurrency fixed at 4, only chunk count varying:

```
16MB × 4 chunks    7.89s   8.11 MB/s   ← fastest
8MB  × 8 chunks   12.04s   5.31 MB/s
4MB  × 16 chunks  28.05s   2.28 MB/s   ← 3.5× slower
```

**Fewer chunks is faster, even as each chunk grows.** This contradicts the intuition
that "more chunks parallelise better" — because the 1–2s fixed cost is paid per chunk,
while transferring a bigger chunk costs barely more (bandwidth isn't the bottleneck).

Concurrency does help. Same 4MB × 16-chunk group:

```
conc 4    28.05s   2.28 MB/s
conc 8    12.84s   4.98 MB/s
conc 16    8.59s   7.45 MB/s
```

But **pushing further backfires**: concurrency 24 was tested separately and regressed
from 14.63s to 20.52s. GitHub starts shedding queued requests, and the retries slow
everything down. Hence the hard cap of **16**.

Combined conclusion:

```
chunk count ≈ 4 (as few as possible)  →  most of the gain
concurrency = chunk count, capped at 16  →  secondary gain
```

## Three parameters, decided together: memory is a constraint too

Concurrency isn't only about speed. Base64 inflates by 1.34×, so encoding N chunks
simultaneously needs `N × chunkSize × 1.34` bytes resident.

So the algorithm runs in three steps:

```python
chunkSize = clamp(size / 4, MIN_CHUNK=1MB, MAX_CHUNK=32MB)
totalChunks = ceil(size / chunkSize)
maxByMemory = floor(MEM_BUDGET / (chunkSize * 1.34))   # default budget 512MB
concurrency = min(totalChunks, maxByMemory, HARD_CONC=16)
```

**The three parameters constrain each other** — bigger chunks mean fewer can be
encoded at once:

| File | Chunk | Chunks | Conc | Batches | Peak memory |
|---|---|---|---|---|---|
| 8MB | 2MB | 4 | 4 | 1 | 11MB |
| 64MB | 16MB | 4 | 4 | 1 | 86MB |
| 256MB | 32MB | 8 | 8 | 1 | 343MB |
| 512MB | 32MB | 16 | **11** | 2 | 472MB |
| 1GB | 32MB | 32 | **11** | 3 | 472MB |
| 4GB | 32MB | 128 | **11** | 12 | 472MB |

Above 512MB, concurrency is clamped by **memory** to 11 rather than 16 — encoding 16
chunks of 32MB at once needs 672MB and gets OOM-killed. That's why the concurrency cap
can't be a hard-coded number.

## Before/after with adaptive planning

| File | Old (fixed 512KB) | New (adaptive) | Gain |
|---|---|---|---|
| 8MB | 88.75s · 112 calls | 15.67s · 9 calls | 5.7× |
| 16MB | 182.09s · 224 calls | 11.53s · 9 calls | **15.8×** |
| 128MB | ~41 min (extrapolated) | **15.74s** · 9 calls | ~156× |
| 512MB | ~1.6h (extrapolated) | 66.23s | ~88× |
| 1GB | ~3.2h (extrapolated) | 136.72s | ~85× |

That 128MB run: **9 API calls, 15.74 seconds, 8.13 MB/s**, read back byte-identical.

## Memory: never base64 everything at once

512MB in 32MB chunks is 16 chunks, each 42MB after base64.
**Encoding all of them up front means 16 × 42MB = 672MB of Python strings live at once.**

That's exactly what version one did — 512MB got OOM-killed with no error at all; the
process just vanished.

Fix: batch it. Only `CONCURRENCY` chunks of base64 exist at any moment.

```python
for start in range(0, n, CONCURRENCY):
    batch = [data[i*chunk:(i+1)*chunk] for i in range(start, min(start+CONCURRENCY, n))]
    b64s = [base64.b64encode(p).decode() for p in batch]
    del batch                      # release raw immediately
    ...concurrent upload...
    del b64s                       # release base64 too
```

## Integrity verification

Speed is meaningless if the bytes are wrong. Every upload was read back and compared:

```
source  sha256 d19cfccc01fdda93…  16777216 bytes
readback sha256 d19cfccc01fdda93…  16777216 bytes
result: ✓ byte-for-byte identical
```

That's **downloading it back and diffing bytes**, not just checking for HTTP 200.

## Retry must cover 500, not just 429

Large transfers hit **500** (not 502/503), which the first version didn't handle:

```python
if e.code in (429, 500, 502, 503):   # 500 needs retrying too
    time.sleep(5 * (attempt + 1))
```

The 256MB run died on exactly this — failed with a 500 on the first attempt, succeeded
once retry was widened.

## Summary

```
small files (≤1MB): upload directly, don't chunk
large files: chunk count = concurrency (4), chunk capped at 32MB
upload concurrently, encoding only one batch at a time
put every chunk into one tree + one commit
```

The first three save fixed overhead; the last one saves those 5.7 seconds.
""",
        },
    },
]
