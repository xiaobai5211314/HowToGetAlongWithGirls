#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《如何与女生相处》Claude 官方 UI 主题的纯净单页检索站与静态资产。
Domain: love.21212121.xyz
Design: Claude Official UI Theme (Warm Paper / Terracotta)
"""

import os
import re
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / 'book'

def parse_book():
    chapters = []
    entries = []
    
    stages_set = set()
    scenes_set = set()
    topics_set = set()
    
    files = sorted(BOOK_DIR.glob('[0-9][0-9]-*.md'))
    for file in files:
        content = file.read_text(encoding='utf-8')
        lines = content.splitlines()
        if not lines:
            continue
        chapter_raw = lines[0].removeprefix('# ').strip()
        m_chap = re.match(r'^(\d+)\.\s*(.+)$', chapter_raw)
        if m_chap:
            chap_num = int(m_chap.group(1))
            chap_title = m_chap.group(2).strip()
        else:
            chap_num = int(file.name[:2])
            chap_title = chapter_raw
        
        chap_entries = []
        parts = re.split(r'^### (\d+)\. (.+)$', content, flags=re.M)
        for i in range(1, len(parts), 3):
            item_num = int(parts[i])
            item_title = parts[i + 1].strip()
            item_body = parts[i + 2].strip()
            
            # 提取标签 <!-- 标签: 阶段=... 场景=... 主题=... -->
            tags = {'stage': [], 'scene': [], 'topic': []}
            tag_match = re.search(r'<!--\s*标签:\s*(.+?)\s*-->', item_body)
            if tag_match:
                tag_str = tag_match.group(1)
                for kv in tag_str.split():
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        vals = [x.strip() for x in re.split(r'[,，]', v) if x.strip()]
                        if k == '阶段':
                            tags['stage'] = vals
                            stages_set.update(vals)
                        elif k == '场景':
                            tags['scene'] = vals
                            scenes_set.update(vals)
                        elif k == '主题':
                            tags['topic'] = vals
                            topics_set.update(vals)
            
            # 提取键值对
            pairs = re.findall(r'^- ([^：\n]+)：([^\n]+(?:\n[ \t]+[^\n]+)*)', item_body, re.M)
            fields = {}
            branches = []
            for k, v in pairs:
                k = k.strip()
                v = re.sub(r'\n[ \t]+', '\n', v).strip()
                if k.startswith('如果') or k.startswith('若'):
                    branches.append({'label': k, 'text': v})
                else:
                    fields[k] = v
            
            entry = {
                'id': f"{chap_num}.{item_num}",
                'sec': chap_num,
                'n': item_num,
                'title': item_title,
                'tags': tags,
                'situation': fields.get('遇到的情况', ''),
                'judgment': fields.get('判断关键', ''),
                'preparation': fields.get('行动前准备', ''),
                'action': fields.get('先做什么', ''),
                'say': fields.get('可以怎么说', ''),
                'contexts': fields.get('分情境处理', ''),
                'cost': fields.get('花掉什么', ''),
                'gain': fields.get('可能换回什么', ''),
                'change': fields.get('何时换办法', ''),
                'exception': fields.get('例外与代价', ''),
                'basis': fields.get('依据', ''),
                'related': fields.get('相关条目', ''),
                'branches': branches
            }
            
            hay_parts = [
                f"{chap_num}.{item_num}",
                item_title,
                entry['situation'],
                entry['judgment'],
                entry['preparation'],
                entry['action'],
                entry['say'],
                entry['contexts'],
                entry['cost'],
                entry['gain'],
                entry['change'],
                entry['exception'],
                entry['basis'],
                entry['related'],
                ' '.join(tags['stage']),
                ' '.join(tags['scene']),
                ' '.join(tags['topic'])
            ] + [f"{b['label']} {b['text']}" for b in branches]
            entry['hay'] = ' '.join(hay_parts).lower()
            
            chap_entries.append(entry)
            entries.append(entry)
            
        chapters.append({
            'sec': chap_num,
            'title': chap_title,
            'file': file.name,
            'count': len(chap_entries),
            'items': [{'id': e['id'], 'n': e['n'], 'title': e['title']} for e in chap_entries]
        })
        
    return chapters, entries, sorted(stages_set), sorted(scenes_set), sorted(topics_set)


def render_html(chapters, entries, stages, scenes, topics):
    corpus_json = json.dumps({'chapters': chapters, 'entries': entries}, ensure_ascii=False)
    
    html_template = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>如何与女生相处 · 两性交往沟通与情感进阶指南</title>
<meta name="description" content="面向男生的两性相处与恋爱教练实战指南：涵盖吸引、平淡、暧昧、恋爱到长期相处全周期。讲清怎么做、怎么说，提供可直接复制的高情商对话台词、信号识别算法与智能止损模型。">
<meta name="keywords" content="如何与女生相处,恋爱指南,聊天技巧,两性心理,高情商聊天,约会安排,肢体升级,表白时机,废物测试,止损模型,DatingCoach">
<meta name="author" content="如何与女生相处指南">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#f5f4ed" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141413" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="https://love.21212121.xyz/">
<link rel="icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="如何与女生相处指南">
<meta property="og:locale" content="zh_CN">
<meta property="og:url" content="https://love.21212121.xyz/">
<meta property="og:title" content="如何与女生相处 · 两性交往沟通与情感进阶指南">
<meta property="og:description" content="全周期两性恋爱与相处指南：讲清怎么做、可以怎么说，附带可复制台词与体面止损方案。">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="如何与女生相处指南">
<meta name="twitter:description" content="全周期两性相处与高情商沟通指南，拒绝套路，重塑真诚与从容自尊。">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "如何与女生相处指南",
  "url": "https://love.21212121.xyz/",
  "description": "面向男生的两性交往与恋爱进阶指南：10 个章节系统拆解聊天、约会、升级、相处与止损。",
  "inLanguage": "zh-CN"
}}
</script>

<script>
(function(){{
  try {{
    var s = localStorage.getItem('theme');
    var d = s ? s === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    if (d) document.documentElement.classList.add('dark');
  }} catch(e) {{}}
}})();
</script>

<style>
/* Claude 官方 UI 调色板与排版体系 */
:root {{
  --bg: #f5f4ed;
  --bg-alt: #edebe1;
  --bg-soft: #faf9f5;
  --bg-mute: #e8e6dc;
  --bg-elv: #faf9f5;
  --divider: #e0ddcf;
  --gutter: #e8e6dc;
  --t1: #141413;
  --t2: #5e5d59;
  --t3: #87867f;
  --brand-1: #c96442;
  --brand-2: #b4573a;
  --brand-3: #d97757;
  --brand-soft: rgba(201, 100, 66, 0.10);
  --brand-border: rgba(201, 100, 66, 0.28);
  --green-1: #4d7c5f;
  --green-soft: rgba(77, 124, 95, 0.12);
  --blue-1: #35678f;
  --blue-soft: rgba(53, 103, 143, 0.11);
  --yellow-1: #96602e;
  --yellow-soft: rgba(201, 140, 80, 0.14);
  --mark: rgba(217, 119, 87, 0.25);
  --shadow: 0 1px 3px rgba(40, 35, 25, 0.05), 0 4px 20px rgba(40, 35, 25, 0.05);
  --font: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  --font-serif: "Noto Serif SC", "Source Han Serif SC", "Songti SC", Georgia, serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --nav-h: 64px;
  --side-w: 290px;
  color-scheme: light;
}}

html.dark {{
  --bg: #141413;
  --bg-alt: #1a1a17;
  --bg-soft: #1f1f1b;
  --bg-mute: #2b2b27;
  --bg-elv: #232320;
  --divider: #30302e;
  --gutter: #000000;
  --t1: #faf9f5;
  --t2: #b0aea5;
  --t3: #87867f;
  --brand-1: #d97757;
  --brand-2: #e08a6d;
  --brand-3: #c96442;
  --brand-soft: rgba(217, 119, 87, 0.15);
  --brand-border: rgba(217, 119, 87, 0.32);
  --green-1: #8fbf9d;
  --green-soft: rgba(143, 191, 157, 0.14);
  --blue-1: #7aaedb;
  --blue-soft: rgba(122, 174, 219, 0.14);
  --yellow-1: #d9a066;
  --yellow-soft: rgba(217, 160, 102, 0.15);
  --mark: rgba(217, 119, 87, 0.32);
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
  color-scheme: dark;
}}

* {{ box-sizing: border-box; }}
html {{ scroll-padding-top: calc(var(--nav-h) + 16px); scrollbar-gutter: stable; }}
body {{ margin: 0; background: var(--bg); color: var(--t1); font: 14.5px/1.7 var(--font); -webkit-font-smoothing: antialiased; }}
a {{ color: var(--brand-1); text-decoration: none; transition: color .2s; }}
a:hover {{ color: var(--brand-2); text-decoration: underline; text-underline-offset: 2px; }}
button {{ font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }}
:focus-visible {{ outline: 2px solid var(--brand-1); outline-offset: 2px; border-radius: 4px; }}
::selection {{ background: var(--mark); }}
mark {{ background: var(--mark); color: inherit; border-radius: 2px; padding: 0 2px; }}

/* 顶部导航 */
.nav {{ position: fixed; top: 0; left: 0; right: 0; height: var(--nav-h); z-index: 40; background: var(--bg); border-bottom: 1px solid var(--divider); }}
.nav-in {{ height: 100%; display: flex; align-items: center; gap: 14px; padding: 0 24px; }}
.title {{ display: flex; align-items: center; gap: 10px; font-family: var(--font-serif); font-weight: 600; font-size: 17.5px; color: var(--t1); white-space: nowrap; }}
.title:hover {{ text-decoration: none; color: var(--t1); }}
.logo {{ width: 28px; height: 28px; border-radius: 8px; background: var(--brand-1); display: grid; place-items: center; color: #fff; }}
.logo svg {{ width: 17px; height: 17px; }}
.nav-badge {{ font-size: 11px; padding: 2px 7px; border-radius: 999px; background: var(--brand-soft); color: var(--brand-1); font-weight: 600; font-family: var(--font); letter-spacing: 0.04em; }}

.search {{ flex: 1; max-width: 480px; margin-left: auto; position: relative; }}
.search input {{ width: 100%; height: 38px; padding: 0 42px 0 38px; border-radius: 10px; border: 1px solid transparent; background: var(--bg-mute); color: var(--t1); font: inherit; font-size: 14px; transition: border-color .2s, background .2s, box-shadow .2s; }}
.search input:hover {{ border-color: var(--divider); }}
.search input:focus {{ outline: 0; border-color: var(--brand-1); background: var(--bg-elv); box-shadow: 0 0 0 3px var(--brand-soft); }}
.search input::placeholder {{ color: var(--t3); }}
.search svg {{ position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; fill: none; stroke: var(--t3); stroke-width: 2; pointer-events: none; }}
.search kbd {{ position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font: 500 11px/1 var(--mono); color: var(--t3); border: 1px solid var(--divider); border-radius: 4px; padding: 3px 5px; background: var(--bg-elv); pointer-events: none; }}

.nav-actions {{ display: flex; align-items: center; gap: 10px; }}
.icon-btn {{ width: 36px; height: 36px; border-radius: 8px; display: grid; place-items: center; color: var(--t2); transition: background .2s, color .2s; }}
.icon-btn:hover {{ background: var(--bg-mute); color: var(--t1); }}
.icon-btn svg {{ width: 19px; height: 19px; fill: currentColor; }}

.mobile-menu-btn {{ display: none; }}
@media (max-width: 860px) {{
  .mobile-menu-btn {{ display: grid; }}
  .search kbd {{ display: none; }}
}}

/* 兄弟站点导航条（置顶微型胶囊） */
.sister-bar {{ background: var(--bg-alt); border-bottom: 1px solid var(--divider); font-size: 12.5px; color: var(--t2); padding: 6px 24px; display: flex; align-items: center; gap: 16px; overflow-x: auto; white-space: nowrap; margin-top: var(--nav-h); }}
.sister-bar span {{ color: var(--t3); }}
.sister-bar a {{ color: var(--t2); display: inline-flex; align-items: center; gap: 4px; font-weight: 500; }}
.sister-bar a:hover {{ color: var(--brand-1); text-decoration: none; }}
.sister-bar .cur {{ color: var(--brand-1); font-weight: 600; }}

/* 页面主体两栏布局 */
.layout {{ display: flex; min-height: calc(100vh - var(--nav-h) - 34px); max-width: 1440px; margin: 0 auto; }}

/* 侧边筛选栏 */
.sidebar {{ width: var(--side-w); flex-shrink: 0; background: var(--bg); border-right: 1px solid var(--divider); padding: 20px; position: sticky; top: calc(var(--nav-h) + 34px); height: calc(100vh - var(--nav-h) - 34px); overflow-y: auto; }}
.side-sec {{ margin-bottom: 22px; }}
.side-title {{ font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--t3); margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; }}
.side-title .badge {{ background: var(--bg-mute); color: var(--t2); padding: 1px 6px; border-radius: 999px; font-size: 11px; }}

.filter-chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.chip {{ font-size: 12.5px; padding: 4px 10px; border-radius: 6px; background: var(--bg-mute); color: var(--t2); transition: all .18s; cursor: pointer; user-select: none; border: 1px solid transparent; }}
.chip:hover {{ background: var(--divider); color: var(--t1); }}
.chip.active {{ background: var(--brand-soft); color: var(--brand-1); border-color: var(--brand-border); font-weight: 600; }}

.chap-list {{ list-style: none; margin: 0; padding: 0; }}
.chap-item {{ padding: 6px 10px; border-radius: 6px; font-size: 13px; color: var(--t2); cursor: pointer; transition: all .18s; display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px; }}
.chap-item:hover {{ background: var(--bg-mute); color: var(--t1); }}
.chap-item.active {{ background: var(--brand-soft); color: var(--brand-1); font-weight: 600; }}
.chap-item .count {{ font-size: 11px; color: var(--t3); }}

.reset-btn {{ font-size: 12px; color: var(--brand-1); padding: 4px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px; margin-top: 10px; }}
.reset-btn:hover {{ background: var(--brand-soft); }}

/* 主内容流 */
.main {{ flex: 1; padding: 32px 40px; min-width: 0; }}
@media (max-width: 860px) {{
  .sidebar {{ position: fixed; top: 0; left: 0; bottom: 0; z-index: 50; width: 300px; height: 100vh; transform: translateX(-100%); transition: transform .25s ease; box-shadow: var(--shadow); }}
  .sidebar.open {{ transform: translateX(0); }}
  .sidebar-backdrop {{ position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 45; opacity: 0; pointer-events: none; transition: opacity .25s ease; }}
  .sidebar-backdrop.show {{ opacity: 1; pointer-events: auto; }}
  .main {{ padding: 20px 16px; }}
}}

/* 结果状态条 */
.status-bar {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid var(--divider); font-size: 13px; color: var(--t3); }}
.status-bar b {{ color: var(--t1); font-weight: 600; }}
.view-mode-btn {{ display: inline-flex; align-items: center; gap: 4px; color: var(--t2); font-size: 12.5px; padding: 4px 8px; border-radius: 6px; background: var(--bg-mute); }}
.view-mode-btn:hover {{ color: var(--t1); background: var(--divider); }}

/* 章节大标题锚点 */
.sec-heading {{ margin: 40px 0 20px; font-family: var(--font-serif); font-size: 21px; font-weight: 600; color: var(--t1); display: flex; align-items: center; gap: 10px; scroll-margin-top: calc(var(--nav-h) + 50px); }}
.sec-heading::before {{ content: ""; display: inline-block; width: 4px; height: 20px; background: var(--brand-1); border-radius: 2px; }}

/* 条目卡片 (Claude 卡片风) */
.card-list {{ display: flex; flex-direction: column; gap: 20px; }}
.card {{ background: var(--bg-soft); border: 1px solid var(--divider); border-radius: 12px; padding: 22px 24px; transition: border-color .2s, box-shadow .2s; position: relative; scroll-margin-top: calc(var(--nav-h) + 50px); }}
.card:hover {{ border-color: var(--brand-border); box-shadow: var(--shadow); }}

.card-top {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 12px; }}
.card-title-wrap {{ display: flex; align-items: baseline; gap: 10px; flex: 1; }}
.card-num {{ font-family: var(--mono); font-size: 13px; font-weight: 600; color: var(--brand-1); background: var(--brand-soft); padding: 2px 7px; border-radius: 6px; text-decoration: none !important; }}
.card-num:hover {{ background: var(--brand-1); color: #fff; }}
.card-title {{ font-size: 17px; font-weight: 600; color: var(--t1); margin: 0; font-family: var(--font-serif); line-height: 1.4; }}

.card-tags {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; }}
.tag-badge {{ font-size: 11px; padding: 2px 7px; border-radius: 4px; font-weight: 500; }}
.tag-stage {{ background: var(--brand-soft); color: var(--brand-1); }}
.tag-scene {{ background: var(--blue-soft); color: var(--blue-1); }}
.tag-topic {{ background: var(--yellow-soft); color: var(--yellow-1); }}

.card-field {{ margin-bottom: 10px; font-size: 14px; line-height: 1.65; }}
.card-field b {{ color: var(--t1); font-weight: 600; }}

/* 核心台词突出展示框 (最核心亮点，支持一键复制) */
.field-say {{ margin: 16px 0; background: var(--bg-elv); border: 1px solid var(--brand-border); border-left: 4px solid var(--brand-1); border-radius: 8px; padding: 14px 16px; position: relative; }}
.say-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
.say-label {{ font-size: 12px; font-weight: 600; color: var(--brand-1); display: flex; align-items: center; gap: 6px; letter-spacing: 0.02em; }}
.say-copy-btn {{ font-size: 12px; color: var(--t2); padding: 3px 8px; border-radius: 4px; background: var(--bg-mute); display: inline-flex; align-items: center; gap: 4px; transition: all .18s; }}
.say-copy-btn:hover {{ background: var(--brand-1); color: #fff; }}
.say-copy-btn svg {{ width: 13px; height: 13px; fill: currentColor; }}
.say-text {{ margin: 0; font-family: var(--font-serif); font-size: 15px; color: var(--t1); line-height: 1.6; white-space: pre-wrap; }}

/* 展开细节折叠面板 */
.card-details {{ margin-top: 14px; border-top: 1px dashed var(--divider); padding-top: 12px; }}
.card-details summary {{ font-size: 12.5px; color: var(--t3); cursor: pointer; user-select: none; display: inline-flex; align-items: center; gap: 6px; padding: 4px 0; transition: color .2s; }}
.card-details summary:hover {{ color: var(--brand-1); }}
.details-body {{ padding-top: 12px; display: flex; flex-direction: column; gap: 10px; font-size: 13.5px; color: var(--t2); }}
.details-body b {{ color: var(--t1); }}

.branch-box {{ background: var(--bg-mute); border-radius: 6px; padding: 8px 12px; margin-top: 4px; font-size: 13px; }}

/* 底部 Footer */
.footer {{ border-top: 1px solid var(--divider); padding: 36px 24px; text-align: center; font-size: 13px; color: var(--t3); margin-top: 60px; background: var(--bg); }}
.footer-links {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 16px; margin-bottom: 12px; }}
.footer a {{ color: var(--t2); }}
.footer a:hover {{ color: var(--brand-1); }}

/* Toast 提示浮窗 */
.toast {{ position: fixed; bottom: 24px; right: 24px; z-index: 100; background: var(--t1); color: var(--bg); padding: 10px 18px; border-radius: 8px; font-size: 13.5px; font-weight: 500; box-shadow: 0 4px 16px rgba(0,0,0,0.2); transform: translateY(100px); opacity: 0; transition: transform .25s ease, opacity .25s ease; pointer-events: none; display: flex; align-items: center; gap: 8px; }}
.toast.show {{ transform: translateY(0); opacity: 1; }}

/* 交叉引用预览浮窗 */
.xref-popover {{ position: absolute; z-index: 60; background: var(--bg-elv); border: 1px solid var(--divider); box-shadow: var(--shadow); border-radius: 8px; padding: 14px 16px; max-width: 440px; font-size: 13px; line-height: 1.6; display: none; }}
.xref-popover .xp-head {{ font-weight: 600; color: var(--brand-1); margin-bottom: 6px; font-family: var(--font-serif); }}
.xref-popover .xp-say {{ background: var(--brand-soft); border-left: 3px solid var(--brand-1); padding: 6px 10px; border-radius: 4px; margin-top: 6px; font-size: 12.5px; }}

/* 动画高亮 */
@keyframes flashBorder {{
  0% {{ border-color: var(--brand-1); box-shadow: 0 0 0 4px var(--brand-soft); }}
  100% {{ border-color: var(--divider); box-shadow: none; }}
}}
.card.flash {{ animation: flashBorder 2s ease; }}
</style>
</head>
<body>

<!-- 顶部导航 -->
<header class="nav">
  <div class="nav-in">
    <button class="icon-btn mobile-menu-btn" id="mobile-toggle" aria-label="打开目录">
      <svg viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
    </button>

    <a href="/" class="title">
      <span class="logo">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
      </span>
      如何与女生相处
    </a>
    <span class="nav-badge">两性社交与恋爱指南</span>

    <div class="search">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <input type="text" id="search-input" placeholder="搜索情境、台词、废测、约会、冷场..." autocomplete="off">
      <kbd>/</kbd>
    </div>

    <div class="nav-actions">
      <a href="阅读全文.html" class="icon-btn" title="连续阅读长文版" style="width:auto; padding:0 8px; font-size:13px; font-weight:500;">
        全文
      </a>
      <a href="https://github.com/xiaobai5211314/HowToGetAlongWithGirls" target="_blank" rel="noopener" class="icon-btn" title="GitHub 开源仓库">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
      </a>
      <button class="icon-btn" id="theme-toggle" aria-label="切换浅色/深色主题" title="切换主题">
        <svg class="sun" viewBox="0 0 24 24" style="display:none;"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>
        <svg class="moon" viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/></svg>
      </button>
    </div>
  </div>
</header>

<!-- 兄弟站点快捷导航条 -->
<div class="sister-bar">
  <span>三部曲联动导航：</span>
  <a href="https://rensheng.21212121.xyz/" target="_blank">📚 《高性价比人生指南》</a>
  <span>·</span>
  <a href="https://renqing.21212121.xyz/" target="_blank">🤝 《人情世故指南》</a>
  <span>·</span>
  <span class="cur">❤️ 《如何与女生相处》</span>
  <span>·</span>
  <a href="/tree/" target="_blank" style="margin-left:auto;">🌸 恋爱时光纪念馆 (爱心树) ↗</a>
</div>

<div class="sidebar-backdrop" id="sidebar-backdrop"></div>

<div class="layout">
  <!-- 侧边筛选栏 -->
  <aside class="sidebar" id="sidebar">
    <div class="side-sec">
      <div class="side-title">
        <span>阶段筛选</span>
        <span class="badge" id="stage-count">{len(stages)}</span>
      </div>
      <div class="filter-chips" id="stage-chips"></div>
    </div>

    <div class="side-sec">
      <div class="side-title">
        <span>高频场景</span>
        <span class="badge" id="scene-count">{len(scenes)}</span>
      </div>
      <div class="filter-chips" id="scene-chips"></div>
    </div>

    <div class="side-sec">
      <div class="side-title">
        <span>章节导航</span>
        <span class="badge">{len(chapters)}</span>
      </div>
      <ul class="chap-list" id="chap-list"></ul>
    </div>

    <button class="reset-btn" id="reset-all" type="button">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
      重置全部筛选条件
    </button>
  </aside>

  <!-- 主内容展示区 -->
  <main class="main">
    <div class="status-bar">
      <span id="result-summary">正在展示全部建议</span>
      <div style="display:flex; gap:10px;">
        <button class="view-mode-btn" id="expand-all-details" type="button">展开全部细节</button>
      </div>
    </div>

    <div class="card-list" id="cards-container"></div>

    <div id="empty-state" style="display:none; text-align:center; padding:60px 20px; color:var(--t3);">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <div style="font-size:16px; font-weight:600; color:var(--t2);">未找到匹配的情境或台词</div>
      <p style="font-size:13px; margin-top:6px;">建议换用更简短的关键词，或点击左侧“重置全部筛选条件”</p>
    </div>

    <!-- 底部版权与免责声明 -->
    <footer class="footer">
      <div class="footer-links">
        <a href="阅读全文.html">阅读全文长文版</a>
        <span>·</span>
        <a href="/tree/">爱心树纪念馆</a>
        <span>·</span>
        <a href="https://github.com/xiaobai5211314/HowToGetAlongWithGirls" target="_blank" rel="noopener">GitHub 仓库</a>
        <span>·</span>
        <a href="https://rensheng.21212121.xyz/" target="_blank">高性价比人生指南</a>
        <span>·</span>
        <a href="https://renqing.21212121.xyz/" target="_blank">人情世故指南</a>
      </div>
      <div>基于开源社区实践与两性社交心理学精编 · 坚决拒绝欺骗、操控与物化女性 · 真诚与自我成长永远是第一吸引力</div>
      <div style="margin-top:6px; font-size:12px; color:var(--t3);">© 2026 如何与女生相处指南 · love.21212121.xyz</div>
    </footer>
  </main>
</div>

<!-- Toast 提示 -->
<div class="toast" id="toast">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
  <span id="toast-text">已复制到剪贴板</span>
</div>

<!-- 交叉引用浮窗 -->
<div class="xref-popover" id="xref-pop">
  <div class="xp-head"><span class="xp-id"></span> <span class="xp-title"></span></div>
  <div class="xp-action"></div>
  <div class="xp-say"></div>
</div>

<script>
const CORPUS = {corpus_json};

(function(){{
  const chapters = CORPUS.chapters;
  const entries = CORPUS.entries;

  const ID_MAP = new Map(entries.map(e => [e.id, e]));

  // DOM 节点
  const qInput = document.getElementById('search-input');
  const stageChips = document.getElementById('stage-chips');
  const sceneChips = document.getElementById('scene-chips');
  const chapList = document.getElementById('chap-list');
  const resetBtn = document.getElementById('reset-all');
  const cardsContainer = document.getElementById('cards-container');
  const resultSummary = document.getElementById('result-summary');
  const emptyState = document.getElementById('empty-state');
  const expandAllBtn = document.getElementById('expand-all-details');
  const toast = document.getElementById('toast');
  const toastText = document.getElementById('toast-text');
  const xrefPop = document.getElementById('xref-pop');
  const themeToggle = document.getElementById('theme-toggle');
  const mobileToggle = document.getElementById('mobile-toggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');

  // 状态维护
  const state = {{
    q: '',
    sec: null,
    stages: new Set(),
    scenes: new Set(),
    expandedAll: false
  }};

  function showToast(msg) {{
    toastText.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2000);
  }}

  // 主题切换
  function updateThemeIcons() {{
    const isDark = document.documentElement.classList.contains('dark');
    themeToggle.querySelector('.sun').style.display = isDark ? 'block' : 'none';
    themeToggle.querySelector('.moon').style.display = isDark ? 'none' : 'block';
  }}
  updateThemeIcons();

  themeToggle.addEventListener('click', () => {{
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcons();
  }});

  // 移动端抽屉
  mobileToggle.addEventListener('click', () => {{
    sidebar.classList.add('open');
    sidebarBackdrop.classList.add('show');
  }});
  sidebarBackdrop.addEventListener('click', () => {{
    sidebar.classList.remove('open');
    sidebarBackdrop.classList.remove('show');
  }});

  // 侧边栏构建
  function renderSidebar() {{
    // 阶段 Chips
    const stagesAll = {json.dumps(stages, ensure_ascii=False)};
    stageChips.innerHTML = stagesAll.map(s => `
      <div class="chip" data-type="stage" data-val="${{s}}">${{s}}</div>
    `).join('');

    // 场景 Chips
    const scenesAll = {json.dumps(scenes, ensure_ascii=False)};
    sceneChips.innerHTML = scenesAll.map(s => `
      <div class="chip" data-type="scene" data-val="${{s}}">${{s}}</div>
    `).join('');

    // 章节列表
    chapList.innerHTML = chapters.map(c => `
      <li class="chap-item" data-sec="${{c.sec}}">
        <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${{c.sec}}. ${{c.title}}</span>
        <span class="count">${{c.count}}</span>
      </li>
    `).join('');
  }}

  function escapeHtml(str) {{
    return (str || '').replace(/[&<>"']/g, m => ({{
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }}[m]));
  }}

  function formatXrefs(text) {{
    if (!text) return '';
    return escapeHtml(text).replace(/(?:见|参考|详见)\s*([0-9]+\.[0-9]+)/g, (match, id) => {{
      return `<a href="#entry-${{id}}" class="xref" data-ref="${{id}}">${{match}}</a>`;
    }});
  }}

  // 构建全部卡片 DOM
  function buildCards() {{
    const cards = [];
    let curSec = null;

    for (const e of entries) {{
      if (e.sec !== curSec) {{
        curSec = e.sec;
        const chapObj = chapters.find(c => c.sec === curSec);
        cards.push(`
          <div class="sec-heading" id="sec-head-${{curSec}}">
            第 ${{curSec}} 章 · ${{chapObj ? chapObj.title : ''}}
          </div>
        `);
      }}

      // 提取分支
      let branchesHtml = '';
      if (e.branches && e.branches.length > 0) {{
        branchesHtml = e.branches.map(b => `
          <div class="branch-box">
            <b>${{escapeHtml(b.label)}}：</b>${{formatXrefs(b.text)}}
          </div>
        `).join('');
      }}

      cards.push(`
        <article class="card" id="entry-${{e.id}}" data-id="${{e.id}}">
          <div class="card-top">
            <div class="card-title-wrap">
              <a href="#entry-${{e.id}}" class="card-num" title="点击复制直链">${{e.id}}</a>
              <h3 class="card-title">${{escapeHtml(e.title)}}</h3>
            </div>
          </div>

          <div class="card-tags">
            ${{e.tags.stage.map(s => `<span class="tag-badge tag-stage">${{escapeHtml(s)}}</span>`).join('')}}
            ${{e.tags.scene.map(s => `<span class="tag-badge tag-scene">${{escapeHtml(s)}}</span>`).join('')}}
            ${{e.tags.topic.map(t => `<span class="tag-badge tag-topic">${{escapeHtml(t)}}</span>`).join('')}}
          </div>

          ${{e.situation ? `<div class="card-field"><b>遇到情况：</b>${{formatXrefs(e.situation)}}</div>` : ''}}
          ${{e.judgment ? `<div class="card-field"><b>判断关键：</b>${{formatXrefs(e.judgment)}}</div>` : ''}}

          ${{e.say ? `
            <div class="field-say">
              <div class="say-header">
                <span class="say-label">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"/></svg>
                  可以怎么说（参考表达）
                </span>
                <button class="say-copy-btn" type="button" data-copy="${{escapeHtml(e.say)}}">
                  <svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                  复制表达
                </button>
              </div>
              <p class="say-text">${{escapeHtml(e.say)}}</p>
            </div>
          ` : ''}}

          ${{e.action ? `<div class="card-field"><b>先做什么：</b>${{formatXrefs(e.action)}}</div>` : ''}}

          <details class="card-details">
            <summary>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
              查看准备、不同情境、分支应对与代价
            </summary>
            <div class="details-body">
              ${{e.preparation ? `<div><b>行动前准备：</b>${{formatXrefs(e.preparation)}}</div>` : ''}}
              ${{e.contexts ? `<div><b>分情境处理：</b>${{formatXrefs(e.contexts)}}</div>` : ''}}
              ${{e.cost ? `<div><b>花掉什么：</b>${{formatXrefs(e.cost)}}</div>` : ''}}
              ${{e.gain ? `<div><b>可能换回什么：</b>${{formatXrefs(e.gain)}}</div>` : ''}}
              ${{branchesHtml}}
              ${{e.change ? `<div><b>何时换办法：</b>${{formatXrefs(e.change)}}</div>` : ''}}
              ${{e.exception ? `<div><b>例外与代价：</b>${{formatXrefs(e.exception)}}</div>` : ''}}
              ${{e.basis ? `<div style="font-size:12px; color:var(--t3);"><b>依据：</b>${{escapeHtml(e.basis)}}</div>` : ''}}
              ${{e.related ? `<div style="font-size:12px; color:var(--brand-1);"><b>相关条目：</b>${{formatXrefs(e.related)}}</div>` : ''}}
            </div>
          </details>
        </article>
      `);
    }}

    cardsContainer.innerHTML = cards.join('');
  }}

  // 筛选核心
  function applyFilter() {{
    const q = state.q.toLowerCase().trim();
    const sec = state.sec;
    const stages = state.stages;
    const scenes = state.scenes;

    const tokens = q ? q.split(/\s+/).filter(Boolean) : [];
    let matchCount = 0;

    const cards = cardsContainer.querySelectorAll('.card');
    const headings = cardsContainer.querySelectorAll('.sec-heading');
    const secVisibleMap = new Map();

    for (const card of cards) {{
      const id = card.dataset.id;
      const entry = ID_MAP.get(id);
      if (!entry) continue;

      let ok = true;

      // 章节
      if (sec && String(entry.sec) !== String(sec)) {{
        ok = false;
      }}

      // 阶段
      if (ok && stages.size > 0) {{
        let hit = false;
        for (const s of stages) {{
          if (entry.tags.stage.includes(s)) {{ hit = true; break; }}
        }}
        if (!hit) ok = false;
      }}

      // 场景
      if (ok && scenes.size > 0) {{
        let hit = false;
        for (const s of scenes) {{
          if (entry.tags.scene.includes(s)) {{ hit = true; break; }}
        }}
        if (!hit) ok = false;
      }}

      // 关键词
      if (ok && tokens.length > 0) {{
        for (const t of tokens) {{
          if (!entry.hay.includes(t)) {{ ok = false; break; }}
        }}
      }}

      card.hidden = !ok;
      if (ok) {{
        matchCount++;
        secVisibleMap.set(entry.sec, (secVisibleMap.get(entry.sec) || 0) + 1);
      }}
    }}

    // 控制章节大标题显隐
    for (const h of headings) {{
      const secNum = parseInt(h.id.replace('sec-head-', ''));
      h.hidden = !secVisibleMap.has(secNum);
    }}

    // 更新状态栏
    resultSummary.textContent = tokens.length || sec || stages.size || scenes.size
      ? `筛选匹配结果：共 ${{matchCount}} 条实战指导`
      : `正在展示全部 ${{matchCount}} 条实战指导`;

    emptyState.style.display = matchCount === 0 ? 'block' : 'none';

    syncUrl();
  }}

  function syncUrl() {{
    const params = new URLSearchParams();
    if (state.q) params.set('q', state.q);
    if (state.sec) params.set('sec', state.sec);
    if (state.stages.size) params.set('stages', Array.from(state.stages).join(','));
    if (state.scenes.size) params.set('scenes', Array.from(state.scenes).join(','));
    const str = params.toString();
    const newUrl = location.pathname + (str ? '?' + str : '') + location.hash;
    history.replaceState(null, '', newUrl);
  }}

  function readUrl() {{
    const params = new URLSearchParams(location.search);
    if (params.has('q')) {{
      state.q = params.get('q');
      qInput.value = state.q;
    }}
    if (params.has('sec')) {{
      state.sec = params.get('sec');
    }}
    if (params.has('stages')) {{
      params.get('stages').split(',').filter(Boolean).forEach(s => state.stages.add(s));
    }}
    if (params.has('scenes')) {{
      params.get('scenes').split(',').filter(Boolean).forEach(s => state.scenes.add(s));
    }}
    updateChipsUI();
  }}

  function updateChipsUI() {{
    document.querySelectorAll('#stage-chips .chip').forEach(c => {{
      c.classList.toggle('active', state.stages.has(c.dataset.val));
    }});
    document.querySelectorAll('#scene-chips .chip').forEach(c => {{
      c.classList.toggle('active', state.scenes.has(c.dataset.val));
    }});
    document.querySelectorAll('#chap-list .chap-item').forEach(ci => {{
      ci.classList.toggle('active', String(state.sec) === ci.dataset.sec);
    }});
  }}

  function bindEvents() {{
    // 搜索框输入
    let debounceTimer;
    qInput.addEventListener('input', () => {{
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {{
        state.q = qInput.value;
        applyFilter();
      }}, 150);
    }});

    // 快捷键 /
    window.addEventListener('keydown', (e) => {{
      if (e.key === '/' && document.activeElement !== qInput) {{
        e.preventDefault();
        qInput.focus();
        qInput.select();
      }}
    }});

    // 点击 Chips
    document.addEventListener('click', (e) => {{
      const chip = e.target.closest('.chip');
      if (chip) {{
        const type = chip.dataset.type;
        const val = chip.dataset.val;
        const set = type === 'stage' ? state.stages : state.scenes;
        if (set.has(val)) {{
          set.delete(val);
        }} else {{
          set.add(val);
        }}
        updateChipsUI();
        applyFilter();
        return;
      }}

      // 点击章节
      const ci = e.target.closest('.chap-item');
      if (ci) {{
        const sec = ci.dataset.sec;
        state.sec = state.sec === sec ? null : sec;
        updateChipsUI();
        applyFilter();
        if (window.innerWidth <= 860) {{
          sidebar.classList.remove('open');
          sidebarBackdrop.classList.remove('show');
        }}
        return;
      }}
    }});

    // 重置按钮
    resetBtn.addEventListener('click', () => {{
      state.q = '';
      state.sec = null;
      state.stages.clear();
      state.scenes.clear();
      qInput.value = '';
      updateChipsUI();
      applyFilter();
    }});

    // 展开/收起全部细节
    expandAllBtn.addEventListener('click', () => {{
      state.expandedAll = !state.expandedAll;
      document.querySelectorAll('.card-details').forEach(d => {{
        d.open = state.expandedAll;
      }});
      expandAllBtn.textContent = state.expandedAll ? '收起全部细节' : '展开全部细节';
    }});

    // 一键复制台词
    document.addEventListener('click', async (e) => {{
      const copyBtn = e.target.closest('.say-copy-btn');
      if (copyBtn) {{
        e.preventDefault();
        const text = copyBtn.dataset.copy;
        try {{
          await navigator.clipboard.writeText(text);
          showToast('已复制高情商台词 ✨');
        }} catch(err) {{
          showToast('复制失败，请手动长按复制');
        }}
      }}
    }});

    // 点击条号复制直链
    document.addEventListener('click', async (e) => {{
      const numLink = e.target.closest('.card-num');
      if (numLink) {{
        e.preventDefault();
        const hash = numLink.getAttribute('href');
        const fullUrl = location.origin + location.pathname + hash;
        try {{
          await navigator.clipboard.writeText(fullUrl);
          showToast('已复制条目直链 🔗');
          location.hash = hash;
        }} catch(err) {{
          location.hash = hash;
        }}
      }}
    }});

    // 交叉引用悬停与点击浮窗
    document.addEventListener('click', (e) => {{
      const xr = e.target.closest('.xref');
      if (xr) {{
        const refId = xr.dataset.ref;
        const target = ID_MAP.get(refId);
        if (!target) return;

        const rect = xr.getBoundingClientRect();
        xrefPop.querySelector('.xp-id').textContent = target.id;
        xrefPop.querySelector('.xp-title').textContent = target.title;
        xrefPop.querySelector('.xp-action').textContent = target.action || target.judgment || '';
        xrefPop.querySelector('.xp-say').textContent = target.say || '';
        xrefPop.querySelector('.xp-say').style.display = target.say ? 'block' : 'none';

        xrefPop.style.display = 'block';
        const popW = Math.min(440, window.innerWidth - 28);
        let left = rect.left + window.scrollX;
        if (left + popW > window.innerWidth - 14) {{
          left = window.innerWidth - popW - 14;
        }}
        xrefPop.style.left = Math.max(14, left) + 'px';
        xrefPop.style.top = (rect.bottom + window.scrollY + 6) + 'px';
      }} else if (!e.target.closest('#xref-pop')) {{
        xrefPop.style.display = 'none';
      }}
    }});

    // 初始锚点定位
    if (location.hash) {{
      setTimeout(() => {{
        const target = document.querySelector(location.hash);
        if (target) {{
          target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
          target.classList.add('flash');
        }}
      }}, 150);
    }}
  }}

  // 初始化
  renderSidebar();
  buildCards();
  readUrl();
  bindEvents();
  applyFilter();
}})();
</script>
</body>
</html>
'''
    return html_template


def render_full_reading(chapters, entries):
    """生成沉浸式连续阅读版 HTML 页面"""
    toc_items = []
    for c in chapters:
        toc_items.append(f'<li><a href="#chap-{c["sec"]}">{c["sec"]}. {html.escape(c["title"])}</a></li>')
    toc_html = "\n".join(toc_items)
    
    sections = []
    for c in chapters:
        c_entries = [e for e in entries if e['sec'] == c['sec']]
        e_htmls = []
        for e in c_entries:
            e_htmls.append(f'''
            <article class="read-entry" id="entry-{e['id']}">
              <div class="read-head">
                <span class="read-num">{e['id']}</span>
                <h3 class="read-title">{html.escape(e['title'])}</h3>
              </div>
              <div class="read-field"><b>遇到的情况：</b>{html.escape(e['situation'])}</div>
              <div class="read-field"><b>判断关键：</b>{html.escape(e['judgment'])}</div>
              {f'<div class="read-say"><b>可以怎么说：</b><div class="say-box">{html.escape(e["say"])}</div></div>' if e["say"] else ''}
              <div class="read-field"><b>先做什么：</b>{html.escape(e['action'])}</div>
              {f'<div class="read-field"><b>分情境处理：</b>{html.escape(e["contexts"])}</div>' if e["contexts"] else ''}
              {f'<div class="read-field"><b>何时换办法：</b>{html.escape(e["change"])}</div>' if e["change"] else ''}
              {f'<div class="read-field"><b>例外与代价：</b>{html.escape(e["exception"])}</div>' if e["exception"] else ''}
            </article>
            ''')
        sections.append(f'''
        <section class="read-chap" id="chap-{c['sec']}">
          <h2>第 {c['sec']} 章 · {html.escape(c['title'])}</h2>
          {"".join(e_htmls)}
        </section>
        ''')
    
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>如何与女生相处 · 连续阅读全书版</title>
<meta name="description" content="《如何与女生相处》完整沉浸阅读版，10个章节连续排版，支持离线阅读与全书浏览。">
<link rel="canonical" href="https://love.21212121.xyz/阅读全文.html">
<link rel="icon" href="/favicon.ico">
<style>
:root {{
  --bg: #f5f4ed; --t1: #141413; --t2: #5e5d59; --t3: #87867f;
  --brand: #c96442; --brand-soft: rgba(201, 100, 66, 0.10);
  --divider: #e0ddcf; --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-serif: "Noto Serif SC", Georgia, serif;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #141413; --t1: #faf9f5; --t2: #b0aea5; --t3: #87867f;
    --brand: #d97757; --brand-soft: rgba(217, 119, 87, 0.15);
    --divider: #30302e;
  }}
}}
body {{ margin: 0; padding: 40px 20px; background: var(--bg); color: var(--t1); font: 15px/1.8 var(--font); }}
.wrap {{ max-width: 820px; margin: 0 auto; }}
.top-nav {{ margin-bottom: 40px; border-bottom: 1px solid var(--divider); padding-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }}
.top-nav a {{ color: var(--brand); text-decoration: none; font-weight: 500; }}
h1 {{ font-family: var(--font-serif); font-size: 28px; margin: 0 0 10px; }}
.toc {{ background: var(--brand-soft); border-radius: 12px; padding: 20px 24px; margin-bottom: 40px; }}
.toc h3 {{ margin: 0 0 12px; font-size: 15px; color: var(--brand); }}
.toc ul {{ margin: 0; padding-left: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 8px; }}
.toc a {{ color: var(--t1); text-decoration: none; }}
.toc a:hover {{ color: var(--brand); text-decoration: underline; }}
.read-chap {{ margin-top: 50px; padding-top: 30px; border-top: 2px solid var(--divider); }}
.read-chap h2 {{ font-family: var(--font-serif); font-size: 22px; color: var(--brand); }}
.read-entry {{ margin-bottom: 30px; padding-bottom: 24px; border-bottom: 1px dashed var(--divider); }}
.read-head {{ display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }}
.read-num {{ font-family: monospace; font-size: 13px; color: var(--brand); font-weight: bold; }}
.read-title {{ font-size: 17px; margin: 0; font-family: var(--font-serif); }}
.read-field {{ margin-bottom: 8px; font-size: 14.5px; }}
.read-field b {{ color: var(--t1); }}
.read-say {{ margin: 12px 0; }}
.say-box {{ background: var(--brand-soft); border-left: 4px solid var(--brand); padding: 10px 14px; border-radius: 6px; font-family: var(--font-serif); margin-top: 6px; white-space: pre-wrap; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="top-nav">
    <a href="/">← 返回主站即时检索</a>
    <span style="color:var(--t3); font-size:13px;">如何与女生相处 · 连续阅读版</span>
  </div>
  <h1>如何与女生相处</h1>
  <div style="color:var(--t3); margin-bottom:30px;">两性交往沟通与情感进阶全书 · 纯净无广告沉浸版</div>
  
  <div class="toc">
    <h3>全书目录索引</h3>
    <ul>
      {toc_html}
    </ul>
  </div>

  {"".join(sections)}
</div>
</body>
</html>
'''

def generate_sitemap(entries):
    urls = [
        '<url><loc>https://love.21212121.xyz/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>',
        '<url><loc>https://love.21212121.xyz/阅读全文.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>',
        '<url><loc>https://love.21212121.xyz/tree/</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>'
    ]
    for e in entries:
        urls.append(f'<url><loc>https://love.21212121.xyz/#entry-{e["id"]}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>')
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"\n".join(urls)}
</urlset>
'''

def generate_combined_markdown(chapters):
    md_parts = ["# 如何与女生相处 · 完整指南\n\n> 两性交往沟通与情感进阶指南，全周期方法论与实战台词库。\n"]
    for c in chapters:
        c_file = BOOK_DIR / c['file']
        if c_file.exists():
            md_parts.append(c_file.read_text(encoding='utf-8'))
            md_parts.append("\n---\n")
    return "\n".join(md_parts)


def main():
    print("开始解析《如何与女生相处》正文...")
    chapters, entries, stages, scenes, topics = parse_book()
    print(f"成功解析 {len(chapters)} 个章节，{len(entries)} 个实战条目！")
    print(f"提取阶段: {len(stages)} 个，场景: {len(scenes)} 个，主题: {len(topics)} 个。")
    
    # 1. index.html (Claude 官方主题检索主页)
    html_content = render_html(chapters, entries, stages, scenes, topics)
    (ROOT / 'index.html').write_text(html_content, encoding='utf-8')
    print(f"成功生成主检索页: index.html ({len(html_content)} 字节)")

    # 2. 阅读全文.html (连续长文版)
    full_html = render_full_reading(chapters, entries)
    (ROOT / '阅读全文.html').write_text(full_html, encoding='utf-8')
    print(f"成功生成连续阅读页: 阅读全文.html ({len(full_html)} 字节)")

    # 3. 完整指南.md
    combined_md = generate_combined_markdown(chapters)
    (ROOT / '完整指南.md').write_text(combined_md, encoding='utf-8')
    print(f"成功生成合并正文: 完整指南.md ({len(combined_md)} 字节)")

    # 4. sitemap.xml
    sitemap_content = generate_sitemap(entries)
    (ROOT / 'sitemap.xml').write_text(sitemap_content, encoding='utf-8')
    print(f"成功生成站点地图: sitemap.xml")

    # 5. robots.txt
    robots_content = "User-agent: *\nAllow: /\nSitemap: https://love.21212121.xyz/sitemap.xml\n"
    (ROOT / 'robots.txt').write_text(robots_content, encoding='utf-8')
    print(f"成功生成爬虫规范: robots.txt")

if __name__ == '__main__':
    main()
