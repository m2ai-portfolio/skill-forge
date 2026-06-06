---
name: tufte-charts
description: Generate minimalist, data-dense charts following Tufte's principles — maximum data-to-ink ratio, no chartjunk, strong signal. Use when the user wants to visualize metrics, pipeline output, or any structured data as a clean chart or dashboard.
---

# Tufte Charts

Produces clear, information-rich charts by applying Tufte's core principle: every mark on the page must earn its place by encoding data. Removes decoration, maximizes signal.

## Trigger

Use when the user says "chart this", "visualize", "graph", "plot", "dashboard", "make a chart", "show this as a graph", or provides tabular/structured data and asks to see it visually.

## Phase 1: Understand the Data

Ask (accept brief answers):

1. **Data source** -- paste inline, file path, or describe it
2. **What relationship to show** -- trend over time? comparison? distribution? part-of-whole?
3. **Output target** -- HTML/SVG (for web), terminal ASCII (quick), or image file?

If the user pastes data inline, parse it directly. Do not ask for what you already have.

## Phase 2: Choose the Right Chart Type

| Relationship | Chart type |
|---|---|
| Change over time | Line or area |
| Comparison across categories | Horizontal bar (allows long labels) |
| Distribution | Small-multiple histograms or dot plot |
| Part-of-whole | Stacked bar or waffle (avoid pie) |
| Correlation | Scatterplot with regression line |

Reject pie charts unless the user insists. Explain why if asked.

## Phase 3: Apply Tufte Principles

Before generating, enforce these rules:

1. **Data-to-ink ratio** -- remove grid lines, borders, tick marks that don't separate data zones. Keep only what encodes a number.
2. **No chartjunk** -- no drop shadows, gradients, 3D effects, decorative icons.
3. **Direct labeling** -- label data series directly on the chart instead of a legend where possible.
4. **Small multiples** -- if comparing more than 5 series, break into a grid of small identical charts rather than cluttering one.
5. **Sparklines for dense data** -- for dashboards with many metrics, generate word-sized inline trend lines.
6. **Show the data** -- include a reference data table beneath the chart so numbers are auditable.

## Phase 4: Generate Output

### For HTML/SVG output

Produce a self-contained HTML file using inline SVG or a zero-dependency charting library (prefer vanilla SVG for portability). Include:
- Chart title (concise, descriptive)
- Axis labels with units
- Source attribution line at the bottom
- The raw data table beneath the chart

Do not link external CDN scripts. The output should render offline.

### For terminal ASCII output

Use block characters to draw the chart. Align columns with spaces. Good enough for quick inspection in a shell.

### For multiple metrics (mini-dashboard)

Arrange charts in a 2-column grid. Use a consistent color palette (recommend: single accent color per chart, gray for reference lines).

## Phase 5: Deliver

Output the complete file contents (or ASCII block). If the user asks for revisions, apply Tufte's principles as the acceptance criterion -- "does this change encode more data, or less?"

## Source

Derived from Nate's Newsletter (2026-06-05) -- recommendation to adopt the MIT Tufte charting skill (238 GitHub stars). Tufte principles sourced from _The Visual Display of Quantitative Information_ (Tufte, 1983).
