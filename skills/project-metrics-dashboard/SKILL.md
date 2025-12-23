---
name: project-metrics-dashboard
description: Design concise, professional dashboards for software projects that surface usage, uptime, and status metrics without a “generative UI” look. Use this skill when a user asks for a modern dashboard, product/engineering health view, or status overview for a SaaS or software system.
metadata:
  author: marcus-vorwaller
  version: "1.0"
---

# Project Metrics Dashboard Design

You are designing a **single, focused dashboard**, not a full BI tool.

The goal: present the **smallest set of widgets** that lets a product or engineering lead answer, in under 10 seconds:

- “Is the product healthy?”
- “Are customers using it as expected?”
- “Is anything on fire right now?”

Avoid anything that feels decorative, chatty, or “AI-generated.” Favor a restrained, product-like UI.

---

## When to use this skill

Use this skill when the user asks for:

- Dashboards summarizing **software or SaaS product health**
- Views of **usage, reliability, performance, or status** (e.g., uptime, incidents, error rates)
- Executive/IC dashboards for **product managers, engineering managers, SREs, or support leaders**

Do **not** use this skill for:

- Marketing/financial dashboards
- Highly exploratory data-science notebooks
- Pixel-perfect visual design mockups (this skill focuses on **structure and content**, not exact CSS)

---

## Inputs you should gather (from the user or context)

Before proposing a dashboard, infer or ask (only if needed):

1. **Audience & role**
   - Product leadership, team leads, engineers, SRE/ops, support, or executives.
2. **Primary decision(s)**
   - Examples: “Ship more features?”, “Improve reliability?”, “Grow active users?”, “Reduce incidents?”
3. **Key entities**
   - What are we measuring? (tenants, users, environments, regions, services, teams, releases, etc.)
4. **Available metrics**
   - Usage: signups, DAU/WAU/MAU, active accounts, feature usage.
   - Reliability: uptime %, incidents, error rates, latency, failed jobs.
   - Status: deployment state, incident state, backlog/queues, SLA/SLOs.
5. **Default time range**
   - Common defaults: last 7 days, last 30 days, or current release window.
6. **Constraints**
   - Screen size (desktop vs embedded panel), theming requirements, data refresh cadence.

Document assumptions clearly if data or definitions are missing.

---

## Output expectations

When this skill is active, you should produce:

- A **clear description** of the dashboard’s structure:
  - Sections, widget list, and their order.
  - For each widget: type, fields, key metric, and interaction.
- **Exact, concise labels** for:
  - Dashboard title
  - Section titles
  - Widget titles, axes, filters
- Any **SQL/metrics definitions or pseudo-schema** you can infer (if requested).
- A short note on **how someone would use** the dashboard to answer core questions.

Do **not** output visual fluff, emoji, or long narrative text. Keep it product-spec level.

---

## Design principles

### 1. Focus on decisions, not data

- Start from 2–4 **primary questions** the dashboard must answer.
- For each question, define **1–3 metrics** that directly answer it.
- Exclude metrics that are merely “nice to have” or loosely related.
- If a metric doesn’t drive a realistic action, **omit it or move it to a secondary view**.

### 2. Information hierarchy & layout

Design assuming a typical desktop viewport (e.g., ~1280–1440px wide):

1. **Top row – Health KPIs (always visible)**
   - 3–6 compact KPI tiles with single numbers and tiny trends, e.g.:
     - Uptime % (last 30 days)
     - Active users / orgs (last 7 or 30 days)
     - Error rate or failed requests %
     - P95 latency
     - Open incidents / current severity
   - Each tile: short title, main value, small trend indicator (sparkline or delta).

2. **Middle row – Trends & comparisons**
   - 2–3 charts showing how key metrics evolve over time:
     - Usage over time (line/area chart).
     - Reliability trend (incidents, error rate, latency).
     - Optional comparison by environment/region/plan.

3. **Bottom row – Detailed status**
   - Tables or lists for:
     - Current incidents or alerts (service, severity, status, owner, started_at).
     - Service-level status (service name, uptime, last deploy, error rate).
     - Optional queue/backlog metrics (jobs pending, age, SLA risk).

General layout rules:

- **Left-to-right, top-to-bottom**: most important at top-left.
- Avoid more than **8–10 widgets** on a single view; merge or remove if you exceed this.
- Group related widgets into **clear sections** with short, neutral headers (e.g., “Usage”, “Reliability”, “Incidents”), not playful or marketing-style language.

### 3. Widgets & visualizations

For each widget, you must specify:

- **Type**: KPI tile, line chart, bar chart, table, or status list.
- **Primary metric**: one main number or trend.
- **Context**: comparison period or target (e.g., vs previous 7 days, vs SLO).
- **Interaction**: what filters/drill-downs apply.

Chart guidelines:

- Use **line/area charts** for time-series (usage, latency, errors).
- Use **bar charts** for categorical comparisons (by region, plan, environment, team).
- Use **tables** for detailed status, incidents, and drill-down data.
- Use **single KPIs** for uptime, error rates, or counts that should be scanned quickly.

Avoid:

- Pie/donut charts for more than 3–4 categories.
- 3D charts, heavy gradients, and non-standard visual encodings.
- Overlapping multiple measures in a way that makes reading trends difficult.

### 4. Filters & interactions (modern, but restrained)

Design filters for **common, high-signal pivots** only:

- **Global filters** (top of dashboard):
  - Time range (e.g., Last 24h, 7d, 30d, 90d).
  - Environment (prod, staging, sandbox).
  - Region or customer segment (e.g., NA/EU/APAC, plan tier).
- **Local filters** (per chart, only as needed):
  - Service name, feature, team, release version.

Guidelines:

- Keep the number of global filters **small** (2–4 maximum).
- Prefer **simple dropdowns, pill toggles, or segmented controls**.
- Ensure filters are **consistent across widgets**: same time range applies to all KPIs and charts by default.
- When describing drill-downs, be explicit:
  - Example: “Clicking a bar in ‘Errors by Service’ filters the incident table below to that service and time range.”

### 5. Copy & labeling

Use **short, neutral, product-like text**:

- Titles: `API uptime (last 30 days)` instead of `How stable has our API been recently?`
- Axes: `Requests per minute`, `Active orgs`, `P95 latency (ms)`.

Do **not**:

- Use emoji or playful language in titles, labels, or tooltips.
- Add helper text like “Here are some insights you might find useful.”
- Repeat the same sub-header above each visualization (“Overview”, “Summary”, etc.).

Do:

- Use consistent naming for the same metric across widgets.
- Indicate units and aggregation explicitly (`per minute`, `per day`, `%`, `ms`).
- Explain non-obvious metrics in **one concise sentence** near the widget, if needed.

### 6. Visual style

The skill should steer design toward:

- **High data-ink ratio**: minimal borders, gridlines, and non-data decoration.
- **Limited color palette**: neutrals for baseline, one accent color for alerts/status.
- Color encodes **meaning**, not decoration:
  - Green: healthy/on-track, Red: error/critical, Amber: warning.
- **Consistent spacing**: even padding and alignment between widgets.
- **Minimal chrome**: avoid drop shadows, gradients, neumorphism, and skeuomorphic dials.
- **No colored left borders on cards**: the `border-left: 3px solid <color>` pattern on cards/alerts is a telltale sign of AI-generated UI. Use subtle background tints, inline status badges, or icons instead.

If theming is requested (e.g., light/dark mode), treat it as a **separate concern** from content and structure.

---

## Metrics menu for software projects

Use this as a menu to construct dashboards. Do not include everything; choose what best fits the user’s goals.

### Product usage

Consider:

- **Active users / orgs**
  - Daily/weekly/monthly active users.
  - % of accounts active in the last N days.
- **Feature usage**
  - Top features by usage.
  - Adoption of new or key features.
- **Engagement**
  - Sessions per user, events per user, time in app.
  - Funnel completion rates for key flows (e.g., setup, integration, configuration).

### Reliability & performance

Consider:

- **Uptime and availability**
  - Uptime % by service over 7/30/90 days.
  - SLO/SLA breaches.
- **Errors**
  - Error rate (% of requests failing).
  - Errors by endpoint/service, errors by region.
- **Latency**
  - P50/P95/P99 latency for critical endpoints.
  - Latency by region, plan, or environment.
- **Incidents**
  - Count of incidents by severity.
  - Mean time to detect (MTTD), mean time to resolve (MTTR).

### Delivery, status, and operations

Consider:

- **Deployments**
  - Deploys per day/week.
  - Current deployed version per service.
  - Rollbacks in the period.
- **Operational queues**
  - Jobs queued vs processed.
  - Long-running or stuck jobs.
- **Support & tickets (if relevant)**
  - Open tickets by severity.
  - Time to first response, time to resolution.

For each metric, decide whether it belongs as:

- A **top-level KPI** (high-level health).
- A **trend chart** (monitor movement over time).
- A **detail table** (investigation and follow-up).

---

## Avoiding the “generative UI” look

When generating dashboard specs or markup, **explicitly avoid**:

- Emoji, ASCII art, or whimsical icons in titles, labels, or legends.
- Phrases like “Here’s a neat chart I made for you” or “Let’s explore your data.”
- Redundant subheadings such as:
  - “Section 1: Overview” immediately followed by a card titled “Overview.”
- Over-nesting:
  - More than **two levels** of tabs or accordions.
  - Multiple carousels of charts.
- Overly verbose descriptions of each widget.
  - Keep annotations 1–2 sentences max, only where truly needed.
- Auto-generated-feeling “insights paragraphs” unless the user specifically asks for written insights.

Instead, favor:

- Plain, professional labels and section titles.
- A small set of clearly explained widgets.
- Straightforward, actionable annotations (e.g., “Error rate exceeded SLO on 3 of the last 7 days.”).

---

## Step-by-step workflow for the agent

When asked to design or refine a project dashboard:

1. **Clarify the core questions and audience.**
   - Infer from context or ask for 2–4 core questions.
2. **List candidate metrics** grouped into usage, reliability, and status.
3. **Select and prioritize**:
   - Choose at most 6 KPIs, 3 charts, and 1–2 tables for the first version.
4. **Define layout and hierarchy**:
   - Arrange in the 3-layer structure: Health KPIs → Trends → Detailed status.
5. **Specify widgets precisely**:
   - For each widget, specify:
     - Type (KPI, line chart, bar chart, table).
     - Query/fields.
     - Time range and filters.
     - Exact title and labels.
6. **Check for noise and redundancy**:
   - Remove or merge low-value or overlapping widgets.
   - Simplify labels and ensure consistent naming.
7. **Describe how to use the dashboard**:
   - 3–5 bullet points explaining typical workflows (e.g., morning health check, incident review, release validation).

Always optimize for **clarity, scan-ability, and decision support** over decoration.