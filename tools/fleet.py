#!/usr/bin/env python3
"""Fleet dashboard generator for the GitHub profile.

Regenerates assets/fleet.svg from live GitHub API data and refreshes the
"currently cooking" block in README.md.

- In GitHub Actions: set GITHUB_TOKEN (and optionally GITHUB_USER).
- Locally: set FLEET_DATA_FILE to a JSON file like
    {"repos": [{"name": ..., "html_url": ..., "description": ...,
                "language": ..., "stargazers_count": ..., "pushed_at": ...,
                "fork": false}, ...],
     "user": {"public_repos": N, "followers": N}}
  captured from the public API (no token needed for public data).
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GITHUB_USER", "NagaSatyaPhanindraVallabhaneni")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Verified 2026-09-20: pytest suites across the portfolio
# (log-anomaly-detector 19, streaming-feature-store 59, loki-self-improving-agent 53,
#  jarvis-ai-assistant 42, timeseries-forecasting-engine 32,
#  tiny-recursive-model 28, diffusion-image-generator 34).
# Bump this when new suites land.
TESTS_PASSING = 267

CYAN = "#00D4FF"
MONO = "'JetBrains Mono',Consolas,monospace"


def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "profile-fleet-dashboard",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def load_data():
    data_file = os.environ.get("FLEET_DATA_FILE")
    if data_file:
        with open(data_file) as f:
            d = json.load(f)
        return d["repos"], d["user"]
    repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
    user = api(f"/users/{USER}")
    return repos, user


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_date(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso


def render_svg(repos, user, now):
    repos = [r for r in repos if not r.get("fork")]
    n_repos = user.get("public_repos", len(repos))
    stars = sum(r.get("stargazers_count", 0) or 0 for r in repos)
    followers = user.get("followers", 0)

    langs = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    top_langs = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:5]
    max_lang = max((c for _, c in top_langs), default=1)

    W, H = 1200, 280
    L = []
    A = L.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A('''<defs>
    <linearGradient id="fbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#11161d"/><stop offset="1" stop-color="#0d1117"/>
    </linearGradient>
    <linearGradient id="fbar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#7fe7ff"/>
    </linearGradient>
  </defs>''')
    A(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14" fill="url(#fbg)" '
      f'stroke="{CYAN}" stroke-opacity="0.35" stroke-width="1.5"/>')
    A(f'<text x="36" y="42" font-family="{MONO}" font-size="15" letter-spacing="3" '
      f'fill="{CYAN}">MISSION CONTROL // FLEET STATUS</text>')
    A(f'<text x="{W - 36}" y="42" text-anchor="end" font-family="{MONO}" '
      f'font-size="12" letter-spacing="2" fill="#8b949e">AUTO-REFRESH · DAILY</text>')

    modules = [
        ("#7ee787", "PUBLIC REPOS", str(n_repos)),
        ("#ffd479", "TOTAL STARS", str(stars)),
        ("#bc8cff", "FOLLOWERS", str(followers)),
        (CYAN, "TESTS PASSING", str(TESTS_PASSING)),
    ]
    for i, (color, label, value) in enumerate(modules):
        cx = 150 + i * 300
        A(f'<text x="{cx}" y="88" text-anchor="middle" font-family="{MONO}" '
          f'font-size="12" letter-spacing="2" fill="#8b949e">{label}</text>')
        A(f'<text x="{cx}" y="130" text-anchor="middle" font-family="{MONO}" '
          f'font-size="36" font-weight="700" fill="{color}">{value}</text>')
        if i < 3:
            x = 300 * (i + 1)
            A(f'<line x1="{x}" y1="70" x2="{x}" y2="140" stroke="{CYAN}" '
              f'stroke-opacity="0.15"/>')

    A(f'<line x1="36" y1="158" x2="{W - 36}" y2="158" stroke="{CYAN}" stroke-opacity="0.15"/>')
    A(f'<text x="36" y="184" font-family="{MONO}" font-size="12" letter-spacing="2" '
      f'fill="#8b949e">TOP LANGUAGES</text>')
    for i, (lang, count) in enumerate(top_langs):
        cx = 150 + i * 225
        bar_w = 150 * (count / max_lang)
        A(f'<text x="{cx}" y="208" text-anchor="middle" font-family="{MONO}" '
          f'font-size="13" fill="#e6edf3">{esc(lang)}</text>')
        A(f'<rect x="{cx - 75}" y="218" width="150" height="6" rx="3" fill="#21262d"/>')
        A(f'<rect x="{cx - 75}" y="218" width="{bar_w:.1f}" height="6" rx="3" fill="url(#fbar)"/>')
        A(f'<text x="{cx}" y="242" text-anchor="middle" font-family="{MONO}" '
          f'font-size="12" fill="{CYAN}">×{count}</text>')

    A(f'<text x="{W - 36}" y="{H - 16}" text-anchor="end" font-family="{MONO}" '
      f'font-size="11" letter-spacing="1.5" fill="#6e7681">'
      f'UPDATED {now.strftime("%Y-%m-%d")} UTC · SOURCE: GITHUB API</text>')
    A('</svg>')
    return "\n".join(L)


def cooking_block(repos):
    mine = [r for r in repos if not r.get("fork")]
    if not mine:
        return "🔥 <b>Currently cooking:</b> something new — check back soon"
    latest = max(mine, key=lambda r: r.get("pushed_at") or "")
    name = latest["name"]
    url = latest.get("html_url", f"https://github.com/{USER}/{name}")
    lang = latest.get("language")
    when = fmt_date(latest.get("pushed_at", ""))
    if name == USER:
        return (f'🔥 <b>Currently cooking:</b> <a href="{url}">this profile</a> '
                f'— the mothership · pushed {when}')
    desc = esc((latest.get("description") or "no description yet").split("\n")[0].strip())
    lang_bit = f" · <code>{esc(lang)}</code>" if lang else ""
    return (f'🔥 <b>Currently cooking:</b> <a href="{url}">{esc(name)}</a> — '
            f'{desc}{lang_bit} · pushed {when}')


def main():
    repos, user = load_data()
    now = datetime.now(timezone.utc)
    svg = render_svg(repos, user, now)
    with open(os.path.join(ROOT, "assets", "fleet.svg"), "w") as f:
        f.write(svg + "\n")
    print("wrote assets/fleet.svg")

    readme = os.path.join(ROOT, "README.md")
    with open(readme) as f:
        content = f.read()
    block = cooking_block(repos)
    new_content, n = re.subn(
        r"<!-- COOKING:START -->.*?<!-- COOKING:END -->",
        f"<!-- COOKING:START -->\n{block}\n<!-- COOKING:END -->",
        content,
        flags=re.S,
    )
    if n:
        with open(readme, "w") as f:
            f.write(new_content)
        print("updated README cooking block")
    else:
        print("WARNING: no COOKING markers in README")


if __name__ == "__main__":
    import sys
    main()
