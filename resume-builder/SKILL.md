---
name: resume-builder
description: "把中文简历内容（或 jd-matcher 产出的定制话术）渲染成双栏现代风、可在线编辑的 HTML 简历，蓝绿渐变侧栏，浏览器打印即 PDF。解决'PDF 难编辑 + 模板不好看'痛点。触发：生成简历、做简历、漂亮简历模板、HTML 简历、在线编辑简历、导出 PDF 简历、按企业优化简历、简历不好看重做。"
agent_created: true
---

# Resume Builder — 双栏中文 HTML 简历生成器

## Overview

一个**纯前端、零依赖**的中文简历生成器。输入结构化 `resume.json`，输出双栏现代风 HTML 简历：
- 左侧蓝绿渐变侧栏（联系方式 / 核心能力标签 / 关键数据卡片 / 工具栈）
- 右侧主栏（姓名 + 职位 + 一句话定位 → 个人简介 → 工作经历 → 代表项目）

**为什么是 HTML 而不是 PDF**：PDF 是固定版式，天生难编辑。HTML 源可直接在浏览器改文字/配色，`Ctrl/Cmd+P` → 存为 PDF 即任意版本。用户要的就是"能在线编辑、调整格式和内容"。

## When to Trigger

- 用户说"生成/做一份简历"、"要个漂亮的简历模板"、"简历不好看重做"
- 用户要"在线编辑简历"、"导出 PDF 简历"
- 用户已用 `jd-matcher` 出了定制话术，要"按企业优化简历"落地成可投递文件
- 任何需要中文、专业、可打印简历的场景

## Prerequisites

- Python 3（标准库即可，无需 pip 安装任何包）
- 一份结构化 `resume.json`（schema 见下；可由用户直接提供，或由 jd-matcher 定制话术转写）

## resume.json Schema（输入格式）

```json
{
  "name": "詹新怡",
  "avatar": "詹",                 // 可选，侧栏头像首字，默认取 name[0]
  "role": "AI 产品经理 · 宠物零售方向",
  "tag": "3 年 LLM Agent / AIGC 落地经验",
  "lead": "一句话定位，出现在主栏姓名下方",
  "email": "zhan_xy@126.com",
  "phone": "176 8231 7674",
  "target": "AI 产品经理（宠物零售 / 智能客服 / AIGC）",
  "skills": ["LLM Agent", "智能客服", "AIGC 内容", "知识库工程", "推荐算法", "电商 SaaS"],
  "stats": [
    {"num": "70%+", "label": "AI 回复相似度"},
    {"num": "100+", "label": "单次服务客户数"},
    {"num": "100+ 条", "label": "头部 IP 单日口播"},
    {"num": "千万", "label": "5 个月 SaaS GMV"}
  ],
  "tools": "Axure · Figma · 蓝湖 · 禅道\nCoze · Dify\nDeepSeek · GPT · Gemini",
  "summary": "个人简介段落文本……",
  "experience": [
    {
      "company": "湖南获课软件开发有限公司",
      "title": "AI 产品负责人",
      "period": "2025.03 – 2026.04",
      "points": ["要点1（纯文本）", "小标题：要点内容（首个中文冒号前自动加粗）"]
    }
  ],
  "projects": [
    {"name": "AI 客服 Agent（数字孪生）", "desc": "LLM+知识库+意图树+SOP 自动化，企微对接……"}
  ],
  "foot": "可选页脚说明"
}
```

> 注意：所有文本字段（`points` / `desc` / `summary` / `lead` / ...）都会经 `html.escape` 转义防 XSS，**内容里不要写任何 HTML 标签**（`<b>` 等会被当成字面文字直接显示出来）。经历条目（`experience[].points`）若含中文冒号"："，则**冒号前部分自动加粗为小标题**（如 `"AI 客服 Agent：从 0 到 1 搭建..."` → 渲染为加粗的"AI 客服 Agent："）。

## Usage（用法）

```bash
# 1) 渲染（默认生成双栏 HTML）
python3 build_resume.py --content resume.json --out resume.html

# 2) 覆盖姓名/职位（如批量生成不同企业变体时）
python3 build_resume.py --content resume-它来宠物.json \
    --out resume-它来宠物.html --role "AI 产品经理 · 宠物零售方向"

# 3) 浏览器打开 → Cmd/Ctrl+P → 目标：另存为 PDF / 纸张 A4
```

输出即 `resume.html`，双击在浏览器打开即可在线编辑（直接改文字/CSS 变量 `--teal` 等换配色），打印存 PDF。

## 关键坑（不要踩）

1. **中文渲染**：本方案用系统字体栈 `"PingFang SC","Hiragino Sans GB","Microsoft YaHei",...`，**网页端无需嵌入字体**，Mac/Win 都能正常显示。不要尝试给 HTML 嵌 reportlab 的 `.ttc` —— 那是 minimax-pdf PDF 路线才需要的（见下）。
2. **不要依赖 Chromium/Playwright**：纯 HTML+CSS，浏览器原生打印即可，规避沙箱装不上浏览器的坑。
3. **打印样式**：`@media print` 已设 A4 + `break-inside:avoid` 防经历/项目被分页截断。改模板时保持这两个。
4. **配色**：强调色用蓝绿渐变 `--grad:linear-gradient(165deg,#0f766e,#0891b2)`，贴合用户品牌色；改色只动 `:root` 里的 CSS 变量。

## 与 jd-matcher 的衔接（契约）

两个 skill **物理独立**，靠格式对接，不互相调用：

```
jd-matcher (分析侧)
  └─ Step 5 产出「定制话术」(markdown: 重写的 summary / 经历改写 / 项目)
        │  （人工或脚本把定制话术转写为结构化 resume.json）
        ▼
resume-builder (生成侧)
  └─ build_resume.py --content resume.json --out resume-企业名.html
```

- jd-matcher 的"重写 summary" → `resume.json.lead` / `summary`
- jd-matcher 的"经历改写" → `resume.json.experience[].points`（纯文本；用"小标题："格式让关键词自动加粗，**不要写 HTML 标签**）
- jd-matcher 的"Requirement→Selling Point 映射" → 提炼为 `skills` 标签 + `stats` 关键数据
- **写法原则**：正文不硬写企业名，用"XX 方向"意图 + 重排经历表达匹配（更专业、更可复用到同类岗）；企业名留给 cover letter / 打招呼语。

## 与 minimax-pdf 的关系

- `minimax-pdf`（marketplace 通用 PDF skill）模板朴素、封面依赖 Chromium，用户已反馈"不好看"。
- 本 skill 走 HTML 路线，**不依赖 minimax-pdf**。minimax-pdf 保留作通用 PDF 工具即可，resume-builder 主线不用它。

## 输出质量

1. 视觉：双栏层次清晰、留白舒适、蓝绿强调色，明显优于单栏朴素模板。
2. 可编辑：HTML 源文本化，用户可自助改字改色，不依赖 Agent 重跑。
3. 打印：A4 + 防截断，浏览器打印即高质量 PDF。
4. 不造假：经历只重组/重述真实事实，与 jd-matcher 的诚实底线一致。
