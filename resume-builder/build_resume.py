#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume-builder — 渲染双栏现代风中文 HTML 简历。

零依赖（仅 Python 标准库）。输入结构化 resume.json，输出可在线编辑的 HTML，
浏览器 Ctrl/Cmd+P 即可"存为 PDF"。

用法:
    python3 build_resume.py --content resume.json --out resume.html
    python3 build_resume.py --content resume.json --out resume.html \
        --name 詹新怡 --role "AI 产品经理" --foot "定制版"

设计要点（见 SKILL.md 关键坑）:
    - 中文渲染: 网页走系统字体栈(PingFang SC/Hiragino/Microsoft YaHei)，无需嵌入字体。
    - 不依赖 Chromium/Playwright: 纯 HTML+CSS，浏览器打印即 PDF。
    - 打印友好: @media print 设定 A4、break-inside:avoid 防分页截断。
"""

import json
import argparse
import html
import sys


def esc(s):
    return html.escape(str(s), quote=True)


# ---------- HTML 模板（双栏现代风，蓝绿渐变侧栏） ----------
# 用 __XXX__ 占位符，避免 str.format 与 CSS 大括号冲突。
HTML_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
  :root{
    --teal:#0f766e; --cyan:#0891b2; --teal-d:#0b5b54;
    --ink:#1f2937; --sub:#475569; --muted:#64748b;
    --line:#e2e8f0; --paper:#ffffff; --grad:linear-gradient(165deg,#0f766e 0%,#0891b2 100%);
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html,body{background:#eef2f6;}
  body{font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Source Han Sans SC",system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);line-height:1.6;font-size:13px;-webkit-font-smoothing:antialiased;}
  .page{width:820px;margin:24px auto;background:var(--paper);display:flex;min-height:1160px;box-shadow:0 10px 40px rgba(15,118,110,.15);border-radius:10px;overflow:hidden;}
  .sidebar{width:280px;flex:0 0 280px;background:var(--grad);color:#ecfeff;padding:34px 26px;position:relative;}
  .sidebar::after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 80% 0,rgba(255,255,255,.12),transparent 55%);}
  .sidebar>*{position:relative;z-index:1;}
  .avatar{width:74px;height:74px;border-radius:50%;background:rgba(255,255,255,.16);border:2px solid rgba(255,255,255,.5);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;letter-spacing:2px;margin-bottom:14px;}
  .sb-name{font-size:22px;font-weight:700;letter-spacing:1px;}
  .sb-role{font-size:13px;color:#cffafe;margin-top:2px;font-weight:500;}
  .sb-tag{display:inline-block;margin-top:10px;font-size:11px;background:rgba(255,255,255,.18);padding:3px 10px;border-radius:20px;color:#ecfeff;}
  .sb-sec{margin-top:26px;}
  .sb-sec h3{font-size:12px;letter-spacing:2px;color:#a5f3fc;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,.22);padding-bottom:6px;margin-bottom:10px;font-weight:600;}
  .sb-contact li{list-style:none;font-size:12px;color:#ecfeff;margin-bottom:7px;display:flex;gap:8px;align-items:flex-start;}
  .sb-contact .ic{width:14px;flex:0 0 14px;opacity:.85;margin-top:2px;}
  .tags{display:flex;flex-wrap:wrap;gap:6px;}
  .tags span{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);color:#ecfeff;font-size:11px;padding:3px 9px;border-radius:6px;}
  .stats{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
  .stat{background:rgba(255,255,255,.12);border-radius:8px;padding:9px 10px;}
  .stat b{display:block;font-size:17px;color:#fff;font-weight:700;}
  .stat small{font-size:10px;color:#cffafe;line-height:1.3;display:block;margin-top:1px;}
  .tools{font-size:11.5px;color:#ecfeff;line-height:1.8;}
  .main{flex:1;padding:36px 38px;}
  .m-head{border-left:4px solid var(--teal);padding-left:14px;margin-bottom:6px;}
  .m-head h1{font-size:27px;font-weight:800;letter-spacing:1px;color:var(--ink);}
  .m-head .role{font-size:14px;color:var(--teal);font-weight:600;margin-top:3px;}
  .m-head .lead{font-size:12.5px;color:var(--muted);margin-top:6px;}
  .sec{margin-top:22px;}
  .sec-h{display:flex;align-items:center;gap:8px;margin-bottom:11px;}
  .sec-h .bar{width:18px;height:3px;background:var(--grad);border-radius:2px;}
  .sec-h h2{font-size:14px;font-weight:700;color:var(--teal-d);letter-spacing:1px;}
  .summary{font-size:12.5px;color:var(--sub);text-align:justify;}
  .job{margin-bottom:14px;}
  .job .jt{font-size:13px;font-weight:700;color:var(--ink);}
  .job .jt .co{color:var(--teal);}
  .job .jt .yr{float:right;font-size:11px;font-weight:500;color:var(--muted);}
  .job ul{margin:6px 0 0;padding-left:16px;}
  .job ul li{font-size:12px;color:var(--sub);margin-bottom:4px;}
  .job ul li::marker{color:var(--cyan);}
  .proj{display:flex;gap:10px;margin-bottom:9px;}
  .proj .dot{flex:0 0 7px;width:7px;height:7px;border-radius:50%;background:var(--teal);margin-top:7px;}
  .proj .pt{font-size:12px;color:var(--sub);}
  .proj .pt b{color:var(--ink);}
  .foot{margin-top:18px;font-size:10.5px;color:#94a3b8;text-align:center;border-top:1px dashed var(--line);padding-top:8px;}
  @media print{
    @page{size:A4;margin:0;}
    html,body{background:#fff;}
    .page{margin:0;box-shadow:none;border-radius:0;width:100%;min-height:100%;}
    .sec,.job,.proj,.stat,.tags span,.sb-sec{break-inside:avoid;}
  }
</style>
</head>
<body>
<div class="page">
  <aside class="sidebar">
    <div class="avatar">__AVATAR__</div>
    <div class="sb-name">__NAME__</div>
    <div class="sb-role">__ROLE__</div>
    <div class="sb-tag">__TAG__</div>

    <div class="sb-sec">
      <h3>联系方式</h3>
      <ul class="sb-contact">
        <li><span class="ic">&#9993;</span><span>__EMAIL__</span></li>
        <li><span class="ic">&#9742;</span><span>__PHONE__</span></li>
        <li><span class="ic">&#9678;</span><span>__TARGET__</span></li>
      </ul>
    </div>

    <div class="sb-sec">
      <h3>核心能力</h3>
      <div class="tags">__SKILLS__</div>
    </div>

    <div class="sb-sec">
      <h3>关键数据</h3>
      <div class="stats">__STATS__</div>
    </div>

    <div class="sb-sec">
      <h3>工具栈</h3>
      <div class="tools">__TOOLS__</div>
    </div>
  </aside>

  <main class="main">
    <div class="m-head">
      <h1>__NAME__</h1>
      <div class="role">__ROLE__</div>
      <div class="lead">__LEAD__</div>
    </div>

    <section class="sec">
      <div class="sec-h"><span class="bar"></span><h2>个人简介</h2></div>
      <p class="summary">__SUMMARY__</p>
    </section>

    <section class="sec">
      <div class="sec-h"><span class="bar"></span><h2>工作经历</h2></div>
      __EXPERIENCE__
    </section>

    <section class="sec">
      <div class="sec-h"><span class="bar"></span><h2>代表项目</h2></div>
      __PROJECTS__
    </section>

    <div class="foot">__FOOT__</div>
  </main>
</div>
</body>
</html>
"""


def render(data: dict) -> str:
    name = esc(data.get("name", ""))
    avatar = esc(data.get("avatar", name[:1]) or name[:1])
    role = esc(data.get("role", ""))
    tag = esc(data.get("tag", ""))
    lead = esc(data.get("lead", ""))
    email = esc(data.get("email", ""))
    phone = esc(data.get("phone", ""))
    target = esc(data.get("target", ""))

    skills = "".join(f'<span>{esc(s)}</span>' for s in data.get("skills", []))
    stats = "".join(
        f'<div class="stat"><b>{esc(s.get("num",""))}</b>'
        f'<small>{esc(s.get("label",""))}</small></div>'
        for s in data.get("stats", [])
    )
    tools = "<br>".join(esc(t) for t in data.get("tools", "").split("\n") if t.strip())

    experience = ""
    for j in data.get("experience", []):
        pts = ""
        for p in j.get("points", []):
            p = str(p)
            if "：" in p:  # 经历小标题（“：”前）自动加粗，避免内容里写 <b> 被转义成字面
                h, _, t = p.partition("：")
                pts += f'<li><b>{esc(h)}：</b>{esc(t)}</li>'
            else:
                pts += f'<li>{esc(p)}</li>'
        experience += (
            f'<div class="job"><div class="jt"><span class="co">{esc(j.get("company",""))}</span>'
            f' · {esc(j.get("title",""))} <span class="yr">{esc(j.get("period",""))}</span></div>'
            f'<ul>{pts}</ul></div>'
        )

    projects = ""
    for p in data.get("projects", []):
        projects += (
            f'<div class="proj"><span class="dot"></span><div class="pt">'
            f'<b>{esc(p.get("name",""))}：</b>{esc(p.get("desc",""))}</div></div>'
        )

    foot = esc(data.get("foot", "本简历为可在线编辑版 · 浏览器打印即可导出 PDF"))

    return (
        HTML_SHELL
        .replace("__TITLE__", f"{name} · {role}")
        .replace("__AVATAR__", avatar)
        .replace("__NAME__", name)
        .replace("__ROLE__", role)
        .replace("__TAG__", tag)
        .replace("__LEAD__", lead)
        .replace("__EMAIL__", email)
        .replace("__PHONE__", phone)
        .replace("__TARGET__", target)
        .replace("__SKILLS__", skills)
        .replace("__STATS__", stats)
        .replace("__TOOLS__", tools)
        .replace("__SUMMARY__", esc(data.get("summary", "")))
        .replace("__EXPERIENCE__", experience)
        .replace("__PROJECTS__", projects)
        .replace("__FOOT__", foot)
    )


def main():
    ap = argparse.ArgumentParser(description="渲染双栏中文 HTML 简历")
    ap.add_argument("--content", required=True, help="结构化简历 JSON 路径")
    ap.add_argument("--out", required=True, help="输出 HTML 路径")
    ap.add_argument("--name", help="覆盖 name（可选）")
    ap.add_argument("--role", help="覆盖 role（可选）")
    ap.add_argument("--foot", help="覆盖页脚说明（可选）")
    args = ap.parse_args()

    with open(args.content, encoding="utf-8") as f:
        data = json.load(f)

    if args.name:
        data["name"] = args.name
    if args.role:
        data["role"] = args.role
    if args.foot:
        data["foot"] = args.foot

    html_out = render(data)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"OK -> {args.out} ({len(html_out)} bytes)")


if __name__ == "__main__":
    main()
