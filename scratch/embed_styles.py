import os

css_path = os.path.join("static", "styles.css")
html_path = os.path.join("static", "index.html")

with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Anti-cache meta tags
cache_meta = """    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">"""

style_block = f"""    <!-- Guaranteed Embedded Off-White Porcelain Stylesheet (Bypasses Browser Caches) -->
    <style id="offwhite-theme-styles">
{css_content}
    </style>"""

if '<meta http-equiv="Cache-Control"' not in html_content:
    html_content = html_content.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + cache_meta
    )

target_link = '<link rel="stylesheet" href="/static/styles.css?v=20261015_offwhite">'
if target_link in html_content:
    html_content = html_content.replace(target_link, target_link + "\n" + style_block)
elif '<link rel="stylesheet" href="/static/styles.css">' in html_content:
    html_content = html_content.replace('<link rel="stylesheet" href="/static/styles.css">', target_link + "\n" + style_block)

theme_badge = """            <div class="nav-actions">
                <div class="theme-badge" style="display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.35rem 0.85rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; font-size: 0.82rem; font-weight: 600; color: #0f172a; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-right: 0.5rem;">
                    <i class="fa-solid fa-sun" style="color: #f59e0b;"></i> Off-White Porcelain
                </div>"""

if '<div class="theme-badge"' not in html_content and '<div class="nav-actions">' in html_content:
    html_content = html_content.replace('<div class="nav-actions">', theme_badge, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully updated {html_path}! New size: {len(html_content)} bytes")
