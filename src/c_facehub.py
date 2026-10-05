# -*- coding: utf-8 -*-
"""FaceHub 文档 —— 中英双语。
内容取自原 docs 仓库的 facehub.md（对照 js/ 源码写的模块手册）。"""

FACEHUB = {
    'title': {'zh': 'FaceHub', 'en': 'FaceHub'},
    'desc': {'zh': '端到端加密聊天 / 朋友圈 / 小程序，全部跑在 GitHub 上。',
             'en': 'End-to-end encrypted chat, moments and mini-apps — all on top of GitHub.'},
    'pages': [
        {
            'slug': 'getting-started',
            'title': {'zh': '快速开始', 'en': 'Getting started'},
            'desc': {'zh': '登录、加好友、发第一条加密消息。', 'en': 'Sign in, add a friend, send your first encrypted message.'},
            'body': {
                'zh': """
打开 [FaceHub](https://cool-zimo.github.io/FaceHub/)，用 GitHub Token 登录。

## 登录时会发生什么

```
登录 → 生成 P-256 密钥对
     → 把公钥写进 facehub-{你的用户名}/pk.json（公开仓库）
```

**公钥放在公开仓库里，这是刻意的。** 任何人想给你发消息，直接读这个文件就行 ——
**你不需要在线**。

这和 Signal 的 prekey、PGP 的公钥服务器是同一个思路。

## 加好友

- 输入对方 GitHub 用户名
- 应用读对方的 `pk.json` 拿到公钥
- 双方自动建立加密会话

## 发消息

消息在发出前就加密，GitHub 上存的是密文。

```
E2E1.<iv_base64>.<ciphertext_base64>
```

`E2E1` 是版本号前缀。解密时如果不是这个前缀，就**原样返回并标记 plain:true** ——
兼容早期未加密的消息。

**每条消息用随机 IV**，所以同一句话发两次，密文完全不同 ——
不会泄露"这两条消息内容一样"。

## 备份密钥

设置里可以导出密钥备份。

<div class="tip tip-bad">
<b>备份是明文的</b>
<p>谁拿到这个文件，谁就能解密你的全部消息。界面上有提示，
但请务必把它当私钥一样保管。</p>
<p>为什么不加口令加密：会引入"忘了口令更惨"这个新问题。
两害相权，宁可让你自己看好文件。</p>
</div>

身份密钥丢了，**全部历史消息都解不开**。
""",
                'en': """
Open [FaceHub](https://cool-zimo.github.io/FaceHub/) and sign in with a GitHub token.

## What happens on sign-in

```
sign in → generate a P-256 key pair
        → write the public key to facehub-{yourname}/pk.json (a public repo)
```

**Putting the public key in a public repository is deliberate.** Anyone who wants to
message you just reads that file — **you don't need to be online**.

Same idea as Signal's prekeys or a PGP keyserver.

## Adding a friend

- Type their GitHub username
- The app reads their `pk.json` to get their public key
- An encrypted session is set up automatically

## Sending messages

Messages are encrypted before they leave; what's stored on GitHub is ciphertext.

```
E2E1.<iv_base64>.<ciphertext_base64>
```

`E2E1` is a version prefix. If a message doesn't start with it, it's **returned as-is
and flagged `plain:true`** — for compatibility with older unencrypted messages.

**Every message uses a random IV**, so sending the same sentence twice produces
completely different ciphertext — it never leaks "these two messages are identical".

## Backing up keys

Settings lets you export a key backup.

<div class="tip tip-bad">
<b>The backup is plaintext</b>
<p>Anyone who gets that file can decrypt every message you have. The UI says so, but
treat it exactly like a private key.</p>
<p>Why not encrypt it with a passphrase: that introduces a worse problem — forgetting
the passphrase. Of the two risks, guarding the file is the lesser evil.</p>
</div>

Lose your identity key and **every historical message becomes undecryptable**.
"""},
        },
        {
            'slug': 'crypto',
            'title': {'zh': '加密机制', 'en': 'Crypto design'},
            'desc': {'zh': 'ECDH + HKDF + AES-GCM，以及为什么每个环节都不能省。',
                     'en': 'ECDH + HKDF + AES-GCM, and why no step can be skipped.'},
            'body': {
                'zh': """
## 算法选型

| 环节 | 算法 | 参数 |
|---|---|---|
| 密钥协商 | ECDH | 曲线 **P-256** |
| 密钥派生 | HKDF | SHA-256，salt 用双方公钥，info=`'aes'` |
| 消息加密 | AES-GCM | 256 位，IV 12 字节随机 |

<div class="tip tip-warn">
<b>早期文档里写的是 X25519，那是错的</b>
<p>源码用的是 P-256。两者都是 ECDH，但曲线和公钥格式不同，
混用会导致<b>永远协商不出相同密钥</b> —— 而且不报错，只是解不开。</p>
</div>

## 为什么必须 HKDF

ECDH 输出的原始比特**不能直接当 AES 密钥** —— 长度不合规、随机性分布不够均匀。

```
ECDH 原始比特 → importKey('raw', bits, 'HKDF')
             → deriveBits(HKDF, 256)   ← extract + expand
             → importKey('raw', prk, 'AES-GCM')
```

## 为什么用 GCM 而不是 CBC

GCM 是 AEAD：**篡改会直接解密失败**，不会解出一段乱码然后被当真。

CBC 没有完整性校验，攻击者改密文能解出看似合理的内容 —— 这在聊天场景里很危险。

## 指纹诊断

```js
await Crypto.fingerprint(pubB64)   // → 'a1b2c3'
```

**为什么需要这个**：密钥不同步时，两边算出的共享密钥不一样，
表现是"能加密但解密全失败"，**而且没有任何报错**。

打印指纹一比对，立刻知道是不是同一对公钥。这是排查加密问题最省时间的一步。

## 群聊的密钥分发

```
创建者生成群密钥 gk
  → 用「自己私钥 + 自己公钥」wrap 一份，存 gk/{me}.json
  → 给每个成员：读对方身份公钥 → wrap → 存 gk/{member}.json
```

<div class="tip tip-note">
<b>每个 gk/{login}.json 都要带 byPub</b>
<p>解包时必须用<b>分发者的公钥</b>，不能写死成创建者 ——
补发群密钥的可能不是创建者本人。</p>
</div>

### 移除成员的顺序不能乱

```
① 把人写进成员列表      ← 必须在分发之前
② 分发群密钥给 TA
③ 轮换群密钥            ← 被移除者解不开之后的消息
④ 写回成员列表
⑤ 撤掉仓库 collaborator ← 必须放最后
```

第 ⑤ 步提前做的话，对方还没拿到新密钥就被踢了，会留下一个解不开消息的僵尸成员。
""",
                'en': """
## Algorithms

| Stage | Algorithm | Parameters |
|---|---|---|
| Key agreement | ECDH | curve **P-256** |
| Key derivation | HKDF | SHA-256, salt = both public keys, info = `'aes'` |
| Message encryption | AES-GCM | 256-bit, random 12-byte IV |

<div class="tip tip-warn">
<b>Early docs said X25519 — that was wrong</b>
<p>The source uses P-256. Both are ECDH, but the curves and public key formats differ,
and mixing them means you <b>never derive the same shared secret</b> — with no error,
just messages that won't decrypt.</p>
</div>

## Why HKDF is required

The raw bits from ECDH **cannot be used directly as an AES key** — wrong length, and
the randomness isn't uniformly distributed.

```
ECDH raw bits → importKey('raw', bits, 'HKDF')
              → deriveBits(HKDF, 256)   ← extract + expand
              → importKey('raw', prk, 'AES-GCM')
```

## Why GCM and not CBC

GCM is AEAD: **tampering causes decryption to fail outright** rather than yielding
plausible-looking garbage.

CBC has no integrity check, so an attacker can modify ciphertext and produce content
that looks legitimate — dangerous in a chat context.

## Fingerprint diagnosis

```js
await Crypto.fingerprint(pubB64)   // → 'a1b2c3'
```

**Why this exists**: when keys fall out of sync, the two sides derive different shared
secrets, which shows up as "encryption works but every decryption fails" —
**with no error at all**.

Printing and comparing fingerprints tells you instantly whether you're looking at the
same key pair. It's the fastest way to debug an encryption problem.

## Group key distribution

```
creator generates a group key gk
  → wrap one copy with "own private + own public" → gk/{me}.json
  → for each member: read their identity public key → wrap → gk/{member}.json
```

<div class="tip tip-note">
<b>Every gk/{login}.json must carry byPub</b>
<p>Unwrapping requires the <b>distributor's</b> public key — it can't be hard-coded to
the creator, because whoever re-issues the group key may not be the creator.</p>
</div>

### Removing a member: order matters

```
① write them into the member list      ← must come before distribution
② distribute the group key to them
③ rotate the group key                 ← so the removed person can't read later messages
④ write the member list back
⑤ revoke the repo collaborator         ← must be last
```

Do ⑤ early and the person gets kicked before receiving the new key, leaving a zombie
member who can't decrypt anything.
"""},
        },
    ],
}
