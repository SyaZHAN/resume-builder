---
name: jd-matcher
description: "Analyzes job descriptions (JD) against a user's resume to produce a ranked match comparison table and customized resume talking points. Triggers on phrases like 'analyze this JD', 'compare my resume', '帮助分析岗位', '匹配度分析', '求职JD分析', '批量分析岗位', importing JD JSON from browser extensions, or any systematic JD-to-resume matching request."
agent_created: true
---

# JD Matcher — Job Description Analysis & Resume Matching

## Overview

A systematic "resume → JD → match score → comparison table" workflow that transforms unstructured job postings into a ranked, actionable application plan. Built around a four-dimensional competency framework and weighted scoring.

## When to Trigger

Activate this skill when the user mentions any of the following:

- **Explicit**: "analyze JD", "compare resume", "岗位匹配", "分析岗位", "匹配度", "求职分析", "帮我看看这个JD"
- **Implicit**: providing a job description with scoring expectations, pasting a batch of JD JSON from a browser extension, asking "should I apply for this"
- **Context**: the user is in a job search context and has shared their resume or is about to

## Prerequisites Check

At the start of every session, check and establish the following. Ask when missing, skip when already known:

1. **Resume source** — Does a resume file exist? Has it been structured into a baseline library? (Accept: `.md`, `.docx`, `.pdf`, pasted text, or structured baseline file)
2. **Target role** — What position/industry is the user targeting? (e.g. "AI Product Manager", "Frontend Engineer")
3. **Experience level** — Junior / Mid / Senior / Lead? (Affects how JD requirements are weighted)
4. **Salary anchor** — What is their current/previous salary? (Critical for "should I apply" decisions)
5. **Target city & location flexibility** — Which city are they job-hunting in, and are remote jobs or other cities acceptable? (Feeds the Step 2.5 location filter)
6. **Target companies** — Big tech, growth-stage, startups, or all? (Affects matching criteria strictness)

**Key rule**: Users may not know their exact level or target — treat "uncertain" as valid and help calibrate through actual JD analysis.

## The Four-Dimensional Framework

Every JD and every resume is decomposed into these four dimensions:

| Dimension | Weight (default) | What it covers |
|---|---|---|
| **Hard Skills** | 35% | Technical tools, languages, frameworks, certifications, methodologies |
| **Soft Skills** | 20% | Communication, leadership, teamwork, ownership, adaptability |
| **Domain Experience** | 25% | Industry knowledge, business context, relevant past roles/companies |
| **Project Outcomes** | 20% | Quantifiable achievements (GMV, DAU, revenue, users, efficiency gains) |

**Weight adjustment rules**:

- For **junior roles**: increase Hard Skills to 40%, decrease Domain to 20%
- For **senior/lead roles**: increase Domain to 30%, decrease Hard Skills to 30%
- For **highly specialized roles** (e.g. WMS expert): increase Domain to 40%
- For **AI/research roles** emphasizing novelty: increase Hard Skills to 40%

Inform the user of the final weights used and allow adjustment.

## Complete Workflow

### Step 0: Resume Bootstrap — Guided Interview for First-Time Resume Writers

When the user has no resume or only vague fragments, run a structured interview to build one from scratch. This takes 5–10 minutes and produces a baseline good enough for JD matching.

**Trigger**: User says "I don't have a resume", "never written one", "not sure what to include", provides only a job title and education, or otherwise indicates they need help building their resume.

**Process**: Ask questions in four rounds, one round at a time. Keep each question short; allow the user to skip or say "not applicable". When a category yields nothing, mark it as a gap rather than guessing.

**Round 1 — Personal Snapshot** (1 question each)
1. Highest education level and major? Graduation year?
2. Total years of work experience? Current employment status?
3. What role/industry are you targeting? Any dream companies?

**Round 2 — Work History** (iterate for each past job)
For each position the user has held, ask:
- Company name and your title? Duration (start–end)?
- What were your 2–3 main responsibilities? (Prompt: "What did you do on a typical day?")
- What was the biggest problem you solved there?
- Any numbers you remember? (Revenue, users, team size, efficiency gains — rough estimates OK)
- Why did you leave? (Helps flag employment gaps)

**Round 3 — Projects & Skills**
- Any side projects, open source contributions, freelance work, or personal apps? (This is where career changers and juniors often shine)
- What tools, languages, or software are you comfortable with? (Prompt with categories: design tools, coding languages, office software, AI tools, domain-specific tools)
- Any certifications, courses, or training worth mentioning?

**Round 4 — Soft Skills & Achievements**
- Have you ever led a team, mentored someone, or managed a project end-to-end?
- Describe a time you dealt with a difficult stakeholder or resolved a conflict.
- What's the accomplishment you're most proud of, professional or personal?
- Anything else you think an employer should know? (Last chance for unstructured input)

**After the interview**, synthesize all answers into a structured resume baseline using the four-dimensional framework from Step 1. Be explicit about which parts are "confirmed" vs "estimated" vs "gaps to clarify." Inform the user they can refine any part.

Then proceed to Step 1 as normal — the interview output serves as the source material for baseline creation.

### Step 1: Establish the Resume Baseline Library

If no baseline exists, create one from the user's resume. The baseline serves as the single source of truth for all subsequent JD matching.

**Process**:
1. Read the resume (markdown, docx, pdf, or pasted text)
2. Decompose into the four dimensions, listing every demonstrable skill/experience with supporting evidence from the resume
3. Extract all quantifiable achievements as a separate evidence catalog
4. Identify and document potential gaps/weaknesses (e.g., "no big-company experience", "AI experience is applied, not algorithmic")
5. Distill a one-sentence positioning statement

**Output**: Save as `jd-matcher/resume-baseline.md` in the working directory. Include:

- Four-dimensional table with evidence citations
- Quantified achievements catalog
- Gap analysis
- Positioning statement
- Ranked selling points (top 5 for interview context)

**After creation**, inform the user and proceed to JD analysis.

### Step 2: JD Decomposition

For each JD (whether pasted individually or batch-imported from JSON), decompose it using the same four-dimensional framework.

**Process**:
1. Extract company name, job title, salary, location, experience/education requirements
2. **Parse salary into a numeric range** for comparability: `"10-15K"` → min=10, max=15 (K/month); handle `K`/`k`/`千`/`万` units and `·13薪`/`·14薪` annual-package suffixes (record separately); `"面议"` or unparseable → null (never guessed). Parsed values power all sorting and filtering; the original string is always preserved for display
3. Parse all "responsibilities" and "requirements" sections into bullet points
4. Map each bullet point to one of the four dimensions
5. Assign a requirement strength: **Must Have** / **Nice to Have** / **Plus**

**For batch JSON input** (from a browser extension) — use every captured field, not just the core four:

| Field | How it's used |
|---|---|
| `url` + `platform` | Carried through to the comparison table so a "投" decision is one click away; identifies which site to return to |
| `workLocation` / `address` | Feeds the location hard filter in Step 2.5 |
| `limitText` | Parse experience/education hard thresholds from the tag line |
| `jobId` / `fingerprint` | Cross-batch dedup: records already analyzed in an earlier batch are skipped, reported as "N 条重复已去除" |

- Full analysis requires `jobName`, `company`, `salary`, `fullText`
- Records with empty `fullText` or `complete: false` (e.g. 智联 list-page metadata captures) are **NOT discarded**: route them to a **"待补全清单"** shown to the user — "N 条仅元数据，进入详情页重新抓取即可补全分析"（dedup by `jobId`）
- Flag records where `company` is "未知公司" as incomplete

### Step 2.5: Hard-Threshold Pre-Filter (cheap filter)

Before deep four-dimension scoring, eliminate obviously unqualified JDs at near-zero cost. A JD is filtered out — **with a reason, never silently** — if ANY:

1. **Location mismatch** — work city is outside the user's target city (skip this rule for remote roles or if the user declared location flexibility)
2. **Salary ceiling below anchor** — parsed salary max < user's anchor → reason "降薪" (even the best case is a pay cut)
3. **Experience floor out of reach** — required minimum years exceeds the user's actual years by 2+ → reason "经验门槛"

Education requirement above the user's degree is **flagged, not dropped** (sales and many other roles commonly negotiate on this).

Filtered-out JDs appear in a compact "已筛除" list (`公司 · 岗位 · 薪资 · 一行原因`) so the user can rescue any entry (e.g. willing to take a pay cut). Only JDs passing the filter proceed to Step 3.

### Step 3: Weighted Scoring

For each JD, score the resume against each dimension on a 0–5 scale:

| Score | Meaning |
|---|---|
| 5 | Fully meets or exceeds — equivalent experience directly matches |
| 4 | Strong match — transferable experience with minor adaptation needed |
| 3 | Partial match — some relevant background but noticeable gaps |
| 2 | Weak match — only tangential or very limited relevant experience |
| 1 | Minimal match — requires significant new learning |
| 0 | No match — completely different domain or skill set |

**Weighted total**: `(Hard×0.35 + Soft×0.20 + Domain×0.25 + Outcome×0.20) / 5 × 100%`

**Additional context factors** (adjust ±2-5%):
- Salary within range → +2%
- Salary midpoint below anchor but max still reaches it (not caught by the Step 2.5 ceiling filter) → -5% and flag
- Experience requirement matches → neutral
- User's experience exceeds the requirement by 2+ years (over-qualify risk) → flag but don't penalize score
- "Plus" requirements met → +2% each
- "Plus" requirements not met → no penalty
- "Must Have" requirements missed → automatic score ceiling at 60%

### Step 4: Generate Comparison Table

Produce a summary comparison table with these columns:
- Priority (⭐ = top picks)
- Company name
- Job title
- Platform + job URL (from the capture record — a "投" decision is one click away)
- Salary (original string + parsed range; `面议` displayed as-is and sorted last)
- Match score
- Key hits (top 2-3 aligned skills)
- Key gaps / risks
- Recommendation (重点投递 / 保底 / 可投 / 不投)

Sort by: match score descending, then parsed salary max descending (numeric values only — never the raw string), then salary min.

Render the table as both:
1. An inline HTML widget (for immediate viewing)
2. A CSV file saved to the working directory (`jd-matcher/comparison-{date}.csv`) encoded in UTF-8 with BOM for Excel compatibility

**Aggregate gap analysis** (when ≥5 JDs are analyzed): after the table, summarize across the whole batch:
- Top 5 most-demanded requirements with frequency (e.g. "私域/微信运营 78%"), split into what the user already covers vs. misses
- The user's 2 biggest recurring gaps + the single highest-ROI skill to build next
- Salary benchmark: median and range of the batch vs. the user's anchor

**Hand-off to Step 5**: end the analysis with a proactive offer — "要对 Top 3 分别生成定制话术吗？" (one confirmation, then batch-generate).

### Step 5: Customized Resume Talking Points (On Request)

When the user wants to apply for a specific JD, generate a tailored "resume lens" that reframes their existing experience in the JD's language. **Never fabricate experience** — only reorganize and re-contextualize real facts.

Output includes:
- Requirement → Selling Point mapping table
- Rewritten summary for resume header
- Experience descriptions rewritten in JD language
- BOSS Zhipin / LinkedIn greeting message (≤120 chars)
- Interview Q&A preparation:
  - Employment gap explanation
  - Cross-industry pivot justification
  - Salary expectation response
- Honesty boundary note: which statements are re-framed vs. which might need interview nuance

## Special Handling

### Salary Calibration

- **Always** ask for the user's current/previous salary as an anchor
- Flag any JD below their anchor as "降薪" (pay cut) regardless of match score
- For first-time job seekers or career switchers: use market research for the target role in their city instead

### Employment Gap

If the user has an employment gap (over 2 months):
- Do NOT assume the gap is a liability
- Ask what they did during the gap — frame it as "active learning / independent projects"
- Integrate gap explanation into customized talking points when requested

### Cross-Industry Applications

When matching a candidate to a JD in a different industry:
- Focus transferable skills (AI capabilities, SaaS experience, product methodology) over industry-specific knowledge
- Mark industry knowledge gap honestly in the comparison table
- In talking points: position cross-industry perspective as a strength (fresh thinking, method transfer)

### Browser Extension Integration

This skill is designed to work alongside a companion browser extension that scrapes JDs from **BOSS直聘 and 智联招聘** (detail pages on both platforms; list pages produce metadata-only records). When the user provides a batch JSON file:

- Parse and validate all records; dedup across batches by `jobId`/`fingerprint`
- Present a one-sentence summary: "M 条中 N 条可分析，X 条待补全（列表元数据），Y 条重复已去除"
- Metadata-only records route to the pending list (Step 2), not the trash
- Proceed with analysis for all fully-captured records
- Note any scraping issues (e.g. missing company names, encoded salary icons) and suggest fixes

## Output Quality Standards

1. **Honesty first**: Never inflate match scores or fabricate experience. The tool's value is in accurate filtering, not wishful thinking.
2. **Actionable**: Every recommendation must have a concrete action (apply, skip, prepare talking points, research industry).
3. **Context-aware**: Factor in salary, city, commute, employment gap, and industry fit — matching is more than skills alone.
4. **Batch efficient**: When processing more than 5 JDs, use batch evaluation with an HTML widget for rapid visual comparison, followed by CSV export.
5. **Calibration feedback**: After initial analysis, invite the user to question scores or adjustments — real hiring decisions need human judgment.
