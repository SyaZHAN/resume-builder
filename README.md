# resume-builder（WorkBuddy skills）

本仓库包含 2 个 WorkBuddy user-level skill，组成「求职 JD 分析 → 定制简历生成」流水线：

- `jd-matcher/`    —— 分析侧：JD 解析、四维评分、可投性排序、定制话术。
- `resume-builder/` —— 生成侧：结构化 `resume.json` → 双栏 HTML 简历 → 浏览器打印 PDF。

两个 skill 物理独立、靠格式契约对接：
jd-matcher 的「定制话术」→ 转写 `resume.json` → resume-builder 渲染。

安装：把需要的子目录整体复制到 `~/.workbuddy/skills/` 即可。
