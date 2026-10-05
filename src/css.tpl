:root{
  --v:#7c5cff; --v2:#a78bfa; --c:#22d3ee;
  --bg:#0a0b12; --panel:#14161f; --panel2:#1a1d29; --panel3:#20242f;
  --line:#262a38; --line2:#333949;
  --ink:#eaecf4; --dim:#9aa3b8; --dim2:#7b8499;
  --green:#34d399; --amber:#fbbf24; --red:#fb7185;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--bg); color:var(--ink);
  font:15px/1.8 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}
a{color:var(--v2);text-decoration:none}
a:hover{text-decoration:underline}

/* ---------- 顶栏 ---------- */
.top{
  position:sticky;top:0;z-index:50;height:56px;
  display:flex;align-items:center;gap:12px;padding:0 16px;
  background:rgba(10,11,18,.86);backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid var(--line);
}
.brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px;color:var(--ink);white-space:nowrap}
.brand:hover{text-decoration:none}
.brand .lg{
  width:26px;height:26px;border-radius:8px;display:grid;place-items:center;font-size:14px;
  background:linear-gradient(135deg,var(--v),var(--c));
}
.brand small{font-weight:500;color:var(--dim2);font-size:11.5px}
.top-sp{flex:1}
.lang{
  display:flex;align-items:center;gap:2px;background:var(--panel2);
  border:1px solid var(--line);border-radius:8px;padding:2px;
}
.lang a{
  padding:3px 10px;border-radius:6px;font-size:12px;color:var(--dim);font-weight:600;
}
.lang a.on{background:var(--v);color:#fff}
.lang a:hover{text-decoration:none}
.menu-btn{
  display:none;background:none;border:1px solid var(--line);border-radius:8px;
  width:34px;height:32px;color:var(--dim);cursor:pointer;font-size:15px;flex:none;
}
/* 顶栏挤不下时优先牺牲 tagline —— 390px 下不藏的话语言切换会被顶出屏幕 */
.top{overflow:hidden}
.lang{flex:none}

/* ---------- 布局 ---------- */
.wrap{display:flex;max-width:1240px;margin:0 auto;align-items:flex-start}
.side{
  width:250px;flex:none;position:sticky;top:56px;height:calc(100vh - 56px);
  overflow-y:auto;padding:22px 14px 40px 20px;border-right:1px solid var(--line);
}
.side::-webkit-scrollbar{width:6px}
.side::-webkit-scrollbar-thumb{background:var(--line2);border-radius:3px}
.app-t{
  font-size:11px;font-weight:700;color:var(--dim2);letter-spacing:.06em;
  margin:16px 0 7px;padding-left:10px;
}
.app-t:first-child{margin-top:0}
.side a{
  display:block;padding:6px 10px;border-radius:8px;font-size:13.5px;color:var(--dim);
  margin-bottom:1px;transition:.15s;
}
.side a:hover{background:var(--panel2);color:var(--ink);text-decoration:none}
.side a.on{background:rgba(124,92,255,.15);color:var(--v2);font-weight:600}
.side a.home{font-weight:650;color:var(--ink);margin-bottom:6px}

.main{flex:1;min-width:0;padding:34px 34px 80px}
.crumb{font-size:12.5px;color:var(--dim2);margin-bottom:10px}
.crumb a{color:var(--dim)}
.crumb span{margin:0 6px;opacity:.5}

/* ---------- 正文 ---------- */
.doc h1{font-size:29px;font-weight:750;letter-spacing:-.02em;margin-bottom:8px;line-height:1.35}
.doc .lead{font-size:15px;color:var(--dim);margin-bottom:26px;padding-bottom:20px;border-bottom:1px solid var(--line)}
.doc h2{
  font-size:20px;font-weight:700;margin:34px 0 14px;padding-bottom:8px;
  border-bottom:1px solid var(--line);scroll-margin-top:70px;
}
.doc h3{font-size:16.5px;font-weight:650;margin:24px 0 10px;scroll-margin-top:70px}
.doc h2:hover .anchor,.doc h3:hover .anchor{opacity:1}
.doc p{margin:12px 0;color:#cfd5e4}
.doc ul,.doc ol{margin:12px 0 12px 24px;color:#cfd5e4}
.doc li{margin:5px 0}
.doc li::marker{color:var(--dim2)}
.doc strong{color:#fff;font-weight:650}
.doc code{
  background:var(--panel2);border:1px solid var(--line);border-radius:5px;
  padding:1.5px 6px;font-size:13px;font-family:var(--mono);color:#e5c9ff;
}
.doc pre{
  background:var(--panel);border:1px solid var(--line);border-radius:11px;
  padding:15px 17px;margin:15px 0;line-height:1.65;
  max-width:100%;overflow-x:auto;
}
.doc pre code{background:none;border:none;padding:0;color:#d7dceb;font-size:13px;white-space:pre}
.doc table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px;display:block;max-width:100%;overflow-x:auto}
.doc th,.doc td{border:1px solid var(--line);padding:9px 12px;text-align:left}
.doc th{background:var(--panel2);font-weight:650;white-space:nowrap}
.doc td code{font-size:12px}
.doc blockquote{
  border-left:3px solid var(--v);background:rgba(124,92,255,.07);
  margin:15px 0;padding:12px 17px;border-radius:0 9px 9px 0;color:#c3cadb;
}
.doc blockquote p{margin:4px 0}
.doc hr{border:none;border-top:1px solid var(--line);margin:30px 0}
.doc img{max-width:100%;border-radius:9px}
.doc h2 a,.doc h3 a{color:inherit}

/* 提示块 */
.tip{border-radius:11px;padding:13px 17px;margin:16px 0;font-size:14px;line-height:1.7}
.tip p{margin:5px 0}
.tip-note{background:rgba(34,211,238,.09);border:1px solid rgba(34,211,238,.28)}
.tip-warn{background:rgba(251,191,36,.09);border:1px solid rgba(251,191,36,.3)}
.tip-bad{background:rgba(251,113,133,.09);border:1px solid rgba(251,113,133,.3)}
.tip-ok{background:rgba(52,211,153,.09);border:1px solid rgba(52,211,153,.28)}
.tip b{display:block;margin-bottom:4px;font-size:13px}

/* 卡片网格 */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:13px;margin:22px 0}
.card{
  display:block;padding:17px 19px;border-radius:13px;
  background:var(--panel);border:1px solid var(--line);
  transition:.2s cubic-bezier(.22,.9,.3,1);
}
.card:hover{
  transform:translateY(-3px);border-color:var(--line2);
  box-shadow:0 14px 30px -16px rgba(0,0,0,.8);text-decoration:none;
}
.card b{display:block;font-size:15px;color:var(--ink);font-weight:650;margin-bottom:4px}
.card span{font-size:13px;color:var(--dim);line-height:1.6}
.card .go{display:inline-block;margin-top:9px;font-size:12px;color:var(--v2);font-weight:600}

/* 上下页 */
.pager{
  display:flex;gap:12px;margin-top:48px;padding-top:22px;border-top:1px solid var(--line);
}
.pager a{
  flex:1;padding:14px 17px;border-radius:12px;background:var(--panel);
  border:1px solid var(--line);transition:.2s;
}
.pager a:hover{transform:translateY(-2px);border-color:var(--line2);text-decoration:none}
.pager a.next{text-align:right}
.pager small{display:block;font-size:11.5px;color:var(--dim2);margin-bottom:3px}
.pager b{font-size:14px;color:var(--ink);font-weight:600}

/* 页脚 */
footer{
  border-top:1px solid var(--line);padding:22px 34px;text-align:center;
  font-size:12.5px;color:var(--dim2);
}
footer a{color:var(--dim)}

.scrim{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:40;
}
.scrim.on{display:block}

@media(max-width:900px){
  .brand small{display:none}
  .side{
    position:fixed;left:0;top:56px;bottom:0;z-index:45;background:var(--bg);
    transform:translateX(-100%);transition:.25s;border-right:1px solid var(--line);
  }
  .side.on{transform:none}
  .menu-btn{display:block}
  .main{padding:26px 18px 60px}
  .doc h1{font-size:24px}
  footer{padding:22px 18px}
}
