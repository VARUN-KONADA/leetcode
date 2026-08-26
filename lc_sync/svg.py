"""Generates a small, dependency-free SVG bar chart of monthly activity.

Deliberately not using matplotlib/plotly/etc: one static bar chart does not
justify a heavy plotting dependency in a CI environment. Raw SVG is
GitHub-friendly (renders inline in README.md) and has zero runtime cost.
"""

from __future__ import annotations

from datetime import date


def monthly_activity_svg(month_counts: dict[str, int], months_to_show: int = 12) -> str:
    """month_counts: {'YYYY-MM': count}. Renders the most recent `months_to_show`."""
    # Build the last N calendar months ending this month, so gaps (months with
    # zero solves) show as empty bars instead of being skipped.
    today = date.today()
    months: list[str] = []
    y, m = today.year, today.month
    for _ in range(months_to_show):
        months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months.reverse()

    values = [month_counts.get(mo, 0) for mo in months]
    max_val = max(values) if any(values) else 1

    width = 640
    height = 180
    padding_left = 30
    padding_bottom = 30
    padding_top = 15
    chart_w = width - padding_left - 10
    chart_h = height - padding_top - padding_bottom
    n = len(months)
    bar_gap = 6
    bar_w = (chart_w - bar_gap * (n - 1)) / n

    bars = []
    labels = []
    for i, (mo, val) in enumerate(zip(months, values)):
        bar_h = (val / max_val) * chart_h if max_val else 0
        x = padding_left + i * (bar_w + bar_gap)
        y_bar = padding_top + (chart_h - bar_h)
        bars.append(
            f'<rect x="{x:.1f}" y="{y_bar:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'rx="2" fill="var(--bar-color, #2f81f7)"><title>{mo}: {val}</title></rect>'
        )
        if val:
            bars.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y_bar - 4:.1f}" font-size="9" '
                f'text-anchor="middle" fill="var(--text-color, #57606a)">{val}</text>'
            )
        if i % 2 == 0 or n <= 6:
            short_label = mo[5:]  # MM
            labels.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{height - padding_bottom + 14:.1f}" '
                f'font-size="9" text-anchor="middle" fill="var(--text-color, #57606a)">{short_label}</text>'
            )

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Monthly problems solved">
<style>
  text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}
</style>
<line x1="{padding_left}" y1="{padding_top + chart_h}" x2="{width - 10}" y2="{padding_top + chart_h}" stroke="var(--text-color, #57606a)" stroke-width="1" opacity="0.4" />
{''.join(bars)}
{''.join(labels)}
</svg>'''
    return svg
