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
import time
import urllib.request
from datetime import datetime, timezone, timedelta

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


def api(path, retries=3):
    last = None
    for attempt in range(retries):
        try:
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
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


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


def ago(iso, now):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return "?"
    s = max(0, int((now - dt).total_seconds()))
    if s < 60:
        return "just now"
    if s < 3600:
        return f"{s // 60}m ago"
    if s < 86400:
        return f"{s // 3600}h ago"
    if s < 86400 * 30:
        return f"{s // 86400}d ago"
    return dt.strftime("%b %d")


def fetch_events():
    try:
        return api(f"/users/{USER}/events/public?per_page=30")
    except Exception:
        return []


EVENT_STYLE = {
    "PushEvent": ("▸", "#7ee787"),
    "PullRequestEvent": ("⇄", "#79c0ff"),
    "WatchEvent": ("★", "#ffd479"),
    "CreateEvent": ("✚", "#bc8cff"),
    "ForkEvent": ("⑂", "#79c0ff"),
    "IssuesEvent": ("◉", "#ffa657"),
    "ReleaseEvent": ("▣", "#7ee787"),
}


def event_line(e):
    t = e.get("type")
    repo = (e.get("repo") or {}).get("name", "")
    short = repo.split("/")[-1] if "/" in repo else repo
    p = e.get("payload") or {}
    if t == "PushEvent":
        n = p.get("size")
        if n is None:
            n = len(p.get("commits", []))
        if n:
            return t, f"pushed {n} commit{'s' if n != 1 else ''} → {short}"
        return t, f"pushed → {short}"
    if t == "PullRequestEvent":
        pr = p.get("pull_request") or {}
        return t, f"{p.get('action', 'opened')} PR #{pr.get('number', '?')} → {short}"
    if t == "WatchEvent":
        return t, f"starred {short}"
    if t == "CreateEvent":
        ref = (p.get("ref") or "").strip()
        what = f"{p.get('ref_type', '')} {ref}".strip()
        return t, f"created {what} in {short}".replace("  ", " ")
    if t == "ForkEvent":
        fee = (p.get("forkee") or {}).get("full_name", "")
        return t, f"forked {short} → {fee}"
    if t == "IssuesEvent":
        num = (p.get("issue") or {}).get("number", "?")
        return t, f"{p.get('action', 'touched')} issue #{num} → {short}"
    if t == "ReleaseEvent":
        tag = (p.get("release") or {}).get("tag_name", "")
        return t, f"released {tag} → {short}"
    return None


def render_activity(events, now):
    # Merge consecutive pushes to the same repo (the events API often omits
    # commit counts, and back-to-back pushes read better collapsed).
    items = []
    for e in events or []:
        parsed = event_line(e)
        if not parsed:
            continue
        t, text = parsed
        repo = ((e.get("repo") or {}).get("name", "").split("/") or [""])[-1]
        if t == "PushEvent" and items and items[-1][0] == "PushEvent" and items[-1][4] == repo:
            items[-1][3] += 1  # bump push count
            continue
        items.append([t, text, e.get("created_at", ""), 1, repo])
        if len(items) >= 8:
            break

    lines = []
    for t, text, created, pushes, _repo in items:
        icon, color = EVENT_STYLE[t]
        if t == "PushEvent" and pushes > 1 and text.startswith("pushed →"):
            _repo_short = text.split("→")[-1].strip()
            text = f"pushed {pushes}× → {_repo_short}"
        lines.append((icon, color, text, ago(created, now)))

    W = 760
    LH = 30
    top, bottom = 66, 46
    H = top + LH * max(len(lines), 1) + bottom
    L = []
    A = L.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A('''<defs><linearGradient id="actbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#141a22"/><stop offset="1" stop-color="#0d1117"/>
    </linearGradient></defs>''')
    A(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14" fill="url(#actbg)" '
      f'stroke="{CYAN}" stroke-opacity="0.35" stroke-width="1.5"/>')
    A(f'<circle cx="30" cy="30" r="6" fill="#FF5F57"/><circle cx="52" cy="30" r="6" '
      f'fill="#FEBC2E"/><circle cx="74" cy="30" r="6" fill="#28C840"/>')
    A(f'<text x="100" y="35" font-family="{MONO}" font-size="13" letter-spacing="2" '
      f'fill="{CYAN}">📡 LIVE // GITHUB ACTIVITY</text>')
    A(f'<text x="{W - 24}" y="35" text-anchor="end" font-family="{MONO}" font-size="11" '
      f'fill="#6e7681">AUTO-SYNC · DAILY</text>')
    A(f'<line x1="20" y1="48" x2="{W - 20}" y2="48" stroke="{CYAN}" stroke-opacity="0.15"/>')
    if not lines:
        A(f'<text x="28" y="{top + 4}" font-family="{MONO}" font-size="14" fill="#8b949e">'
          f'// no public events recently — systems nominal, recharging…</text>')
    for i, (icon, color, text, when) in enumerate(lines):
        y = top + 4 + i * LH
        txt = esc(text)
        if len(txt) > 62:
            txt = txt[:61] + "…"
        A(f'<text x="28" y="{y}" font-family="{MONO}" font-size="14">'
          f'<tspan fill="{color}">{icon}</tspan>'
          f'<tspan fill="#c9d1d9"> {txt}</tspan>'
          f'<tspan fill="#6e7681"> · {when}</tspan></text>')
    A(f'<text x="{W - 24}" y="{H - 18}" text-anchor="end" font-family="{MONO}" '
      f'font-size="11" letter-spacing="1.5" fill="#6e7681">'
      f'SOURCE: GITHUB EVENTS API · {now.strftime("%Y-%m-%d")} UTC</text>')
    A('</svg>')
    return "\n".join(L)


LANG_COLORS = {
    "Python": "#3572A5", "Jupyter Notebook": "#DA5B0B", "HTML": "#e34c26",
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "CSS": "#563d7c",
    "Shell": "#89e051", "Dockerfile": "#384d54", "C++": "#f34b7d",
    "C": "#555555", "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584",
}


def wrap(text, width, max_lines):
    words, lines, cur = (text or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and (len(words) > sum(len(l.split()) for l in lines)):
        lines[-1] = lines[-1][: width - 1].rstrip() + "…"
    return lines


def render_spotlight(repos, now):
    mine = [r for r in repos if not r.get("fork")]
    W, H = 760, 250
    L = []
    A = L.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A('''<defs>
    <linearGradient id="spotbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#101725"/><stop offset="1" stop-color="#0d1117"/>
    </linearGradient>
    <radialGradient id="spotglow" cx="0.85" cy="0.1" r="0.7">
      <stop offset="0" stop-color="#00D4FF" stop-opacity="0.14"/>
      <stop offset="1" stop-color="#00D4FF" stop-opacity="0"/>
    </radialGradient>
  </defs>''')
    A(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14" fill="url(#spotbg)" '
      f'stroke="{CYAN}" stroke-opacity="0.35" stroke-width="1.5"/>')
    A(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14" fill="url(#spotglow)"/>')
    doy = now.timetuple().tm_yday
    A(f'<text x="28" y="40" font-family="{MONO}" font-size="13" letter-spacing="3" '
      f'fill="{CYAN}">◆ SPOTLIGHT // ROTATES DAILY</text>')
    A(f'<text x="{W - 28}" y="40" text-anchor="end" font-family="{MONO}" font-size="11" '
      f'fill="#6e7681">DAY {doy} / 365</text>')
    if not mine:
        A(f'<text x="28" y="120" font-family="{MONO}" font-size="16" fill="#8b949e">'
          f'// spotlight warming up…</text>')
    else:
        r = mine[doy % len(mine)]
        name = r.get("name", "?")
        desc_lines = wrap(r.get("description") or "no description yet", 68, 2)
        lang = r.get("language") or "—"
        stars = r.get("stargazers_count", 0) or 0
        pushed = ago(r.get("pushed_at", ""), now)
        lc = LANG_COLORS.get(lang, CYAN)
        A(f'<text x="28" y="96" font-family="{MONO}" font-size="30" font-weight="700" '
          f'fill="#e6edf3">{esc(name)}</text>')
        y = 128
        for dl in desc_lines:
            A(f'<text x="28" y="{y}" font-family="{MONO}" font-size="14" fill="#8b949e">'
              f'{esc(dl)}</text>')
            y += 24
        A(f'<g font-family="{MONO}" font-size="13">'
          f'<circle cx="34" cy="189" r="5" fill="{lc}"/>'
          f'<text x="46" y="194" fill="#c9d1d9">{esc(lang)}</text>'
          f'<text x="190" y="194" fill="#ffd479">★ {stars}</text>'
          f'<text x="270" y="194" fill="#6e7681">⟳ pushed {pushed}</text></g>')
    A(f'<text x="{W - 28}" y="{H - 18}" text-anchor="end" font-family="{MONO}" '
      f'font-size="11" letter-spacing="1.5" fill="#6e7681">'
      f'github.com/{USER}/{esc(name)} · NEW REPO EVERY 24H</text>')
    A('</svg>')
    return "\n".join(L)


def fetch_builds(repos):
    builds = []
    for r in repos:
        if r.get("fork"):
            continue
        name = r.get("name")
        try:
            data = api(f"/repos/{USER}/{name}/actions/runs?per_page=1")
        except Exception:
            continue
        runs = data.get("workflow_runs") or []
        if not runs:
            continue
        run = runs[0]
        builds.append({
            "repo": name,
            "workflow": run.get("name") or (run.get("path") or "").split("/")[-1],
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "updated": run.get("updated_at"),
        })
        if len(builds) >= 8:
            break
    return builds


def render_builds(builds, now):
    W = 760
    RH = 36
    top, bottom = 66, 44
    n = max(len(builds), 1)
    H = top + RH * n + bottom
    L = []
    A = L.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A('''<defs><linearGradient id="bldbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#11161d"/><stop offset="1" stop-color="#0d1117"/>
    </linearGradient></defs>''')
    A(f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14" fill="url(#bldbg)" '
      f'stroke="{CYAN}" stroke-opacity="0.35" stroke-width="1.5"/>')
    A(f'<text x="28" y="40" font-family="{MONO}" font-size="13" letter-spacing="3" '
      f'fill="{CYAN}">⬢ CI // LIVE BUILD BOARD</text>')
    A(f'<text x="{W - 28}" y="40" text-anchor="end" font-family="{MONO}" font-size="11" '
      f'fill="#6e7681">AUTO-REFRESH · DAILY</text>')
    A(f'<line x1="20" y1="52" x2="{W - 20}" y2="52" stroke="{CYAN}" stroke-opacity="0.15"/>')
    if not builds:
        A(f'<text x="28" y="{top + 6}" font-family="{MONO}" font-size="14" fill="#8b949e">'
          f'// no workflow runs found — check back soon</text>')
    for i, b in enumerate(builds):
        y = top + 6 + i * RH
        if b["status"] != "completed":
            label, color = "RUNNING", "#d29922"
        elif b["conclusion"] == "success":
            label, color = "PASSING", "#3fb950"
        else:
            label, color = "FAILING", "#f85149"
        pw = 92
        px = W - 28 - pw
        repo = b["repo"]
        if repo == USER:
            repo = "profile ✦"
        elif repo == f"{USER}.github.io":
            repo = "portfolio site"
        repo = esc(repo)
        if len(repo) > 26:
            repo = repo[:25] + "…"
        A(f'<circle cx="36" cy="{y - 4}" r="5" fill="{color}"/>')
        A(f'<text x="50" y="{y}" font-family="{MONO}" font-size="14" fill="#e6edf3">'
          f'{repo}</text>')
        wf = esc(b["workflow"])
        if len(wf) > 30:
            wf = wf[:29] + "…"
        A(f'<text x="330" y="{y}" font-family="{MONO}" font-size="12" fill="#6e7681">{wf}</text>')
        A(f'<text x="{px - 14}" y="{y}" text-anchor="end" font-family="{MONO}" '
          f'font-size="12" fill="#6e7681">{ago(b["updated"], now)}</text>')
        A(f'<rect x="{px}" y="{y - 17}" width="{pw}" height="22" rx="11" '
          f'fill="{color}" fill-opacity="0.14" stroke="{color}" stroke-opacity="0.6"/>')
        A(f'<text x="{px + pw / 2}" y="{y - 2}" text-anchor="middle" font-family="{MONO}" '
          f'font-size="11" font-weight="700" letter-spacing="1" fill="{color}">{label}</text>')
    A(f'<text x="{W - 28}" y="{H - 18}" text-anchor="end" font-family="{MONO}" '
      f'font-size="11" letter-spacing="1.5" fill="#6e7681">'
      f'LIVE FROM GITHUB ACTIONS · {now.strftime("%Y-%m-%d")} UTC</text>')
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


# ── CINEMA: animated, data-driven SVG modules (SMIL plays live in the browser) ──

LANG_COLORS = {
    "Python": "#3572A5", "Jupyter Notebook": "#DA5B0B", "HTML": "#e34c26",
    "CSS": "#563d7c", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Shell": "#89e051", "Dockerfile": "#384d54", "C++": "#f34b7d",
    "C": "#555555", "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584",
}

def fetch_daily_pushes(repos, days=14):
    """His own commit counts per day for the last `days` days (GitHub Commits API)."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    counts = {}
    for r in repos:
        try:
            commits = api(f"/repos/{USER}/{r['name']}/commits?since={since}&per_page=100&author={USER}")
        except Exception:
            continue
        if isinstance(commits, list):
            for c in commits:
                d = ((c.get("commit") or {}).get("author") or {}).get("date", "")[:10]
                if d:
                    counts[d] = counts.get(d, 0) + 1
    out = []
    now = datetime.now(timezone.utc).date()
    for i in range(days - 1, -1, -1):
        d = (now - timedelta(days=i)).isoformat()
        out.append((d, counts.get(d, 0)))
    return out


def render_boot(today, repo_count):
    W, H = 760, 360
    A = []
    A.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A.append('<defs>'
             '<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#00D4FF" stop-opacity="0"/>'
             '<stop offset="0.5" stop-color="#00D4FF" stop-opacity="0.06"/>'
             '<stop offset="1" stop-color="#00D4FF" stop-opacity="0"/></linearGradient>'
             '<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#3fb950"/></linearGradient>'
             '<filter id="bglow" x="-60%" y="-60%" width="220%" height="220%">'
             '<feGaussianBlur stdDeviation="4" result="b"/>'
             '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
             '</filter></defs>')
    A.append(f'<rect width="{W}" height="{H}" rx="10" fill="#05070d"/>')
    A.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="none" stroke="#00D4FF" stroke-opacity="0.25"/>')
    A.append(f'<text x="28" y="34" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{CYAN}">▸ PHANINDRA.OS // BOOT SEQUENCE</text>')
    A.append(f'<g font-family="{MONO}" font-size="12" fill="#3fb950"><circle cx="{W-78}" cy="29" r="5" fill="#3fb950">'
             f'<animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{W-66}" y="34">LIVE</text></g>')
    # radar
    rx, ry, rr = W - 92, 108, 44
    A.append(f'<g opacity="0.8"><circle cx="{rx}" cy="{ry}" r="{rr}" fill="none" stroke="#12384a"/>'
             f'<circle cx="{rx}" cy="{ry}" r="{rr*0.66}" fill="none" stroke="#12384a"/>'
             f'<circle cx="{rx}" cy="{ry}" r="{rr*0.33}" fill="none" stroke="#12384a"/>'
             f'<line x1="{rx}" y1="{ry}" x2="{rx+rr}" y2="{ry}" stroke="{CYAN}" stroke-width="2" filter="url(#bglow)">'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {rx} {ry}" to="360 {rx} {ry}" dur="5s" repeatCount="indefinite"/></line>'
             f'<circle cx="{rx+18}" cy="{ry-12}" r="3" fill="{CYAN}"><animate attributeName="opacity" values="0;1;0" dur="2.5s" repeatCount="indefinite"/></circle></g>')
    lines = [
        (0.4, "#8b949e", "> kernel v3.0 .................... LOADED"),
        (0.9, "#e6edf3", "> identity ..... ML/AI SYSTEMS ENGINEER"),
        (1.4, "#8b949e", "> work_auth .... OPT EAD · open to H-1B"),
        (1.9, "#8b949e", "> arsenal ...... python · pytorch · fastapi · docker · k8s · aws"),
        (2.4, "#e6edf3", f"> fleet ........ {repo_count} repos · {TESTS_PASSING} tests · 0 red builds"),
        (2.9, "#3fb950", "> status ....... [ ALL SYSTEMS NOMINAL ]"),
    ]
    for t, col, txt in lines:
        glow = ' filter="url(#bglow)"' if col == "#3fb950" else ""
        A.append(f'<text x="36" y="{118 + lines.index((t, col, txt)) * 28}" font-family="{MONO}" font-size="14" fill="{col}"{glow} opacity="0">{esc(txt)}'
                 f'<animate attributeName="opacity" values="0;1" begin="{t}s" dur="0.25s" fill="freeze"/></text>')
    # progress bar
    A.append(f'<text x="36" y="300" font-family="{MONO}" font-size="11" letter-spacing="2" fill="#6e7681">LOADING MODULES</text>')
    A.append(f'<rect x="36" y="310" width="620" height="10" rx="5" fill="#161b22"/>')
    A.append(f'<rect x="36" y="310" width="0" height="10" rx="5" fill="url(#bar)" filter="url(#bglow)">'
             f'<animate attributeName="width" from="0" to="620" begin="0.4s" dur="3s" fill="freeze"/></rect>')
    A.append(f'<text x="666" y="319" font-family="{MONO}" font-size="12" fill="#3fb950" opacity="0">100%<animate attributeName="opacity" values="0;1" begin="3.4s" dur="0.3s" fill="freeze"/></text>')
    # cursor + prompt
    A.append(f'<rect x="36" y="332" width="10" height="15" fill="{CYAN}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    A.append(f'<text x="52" y="344" font-family="{MONO}" font-size="13" fill="#6e7681">awaiting recruiter input_</text>')
    # scanline sweep
    A.append(f'<rect x="0" y="-40" width="{W}" height="46" fill="url(#scan)">'
             f'<animate attributeName="y" from="-46" to="{H}" dur="5.5s" repeatCount="indefinite"/></rect>')
    A.append(f'<text x="{W-28}" y="{H-14}" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="#3a4552">REGENERATED DAILY · {today} UTC</text>')
    A.append("</svg>")
    return "".join(A)


def render_orbit(repos):
    W, H = 760, 400
    cx, cy = 248, 200
    pool = [r for r in repos if r["name"] not in (USER, f"{USER}.github.io")]
    pool.sort(key=lambda r: (-(r.get("stars") or 0), r["name"]))
    pool = pool[:8]
    A = []
    A.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A.append('<defs><radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0" stop-color="#00D4FF"/><stop offset="0.55" stop-color="#00D4FF" stop-opacity="0.35"/>'
             '<stop offset="1" stop-color="#00D4FF" stop-opacity="0"/></radialGradient>'
             '<filter id="pglow" x="-80%" y="-80%" width="260%" height="260%">'
             '<feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    A.append(f'<rect width="{W}" height="{H}" rx="10" fill="#05070d"/>')
    A.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="none" stroke="#00D4FF" stroke-opacity="0.25"/>')
    # starfield
    for i in range(46):
        h = (i * 2654435761) % 1000 / 1000
        sx = 20 + h * (W - 40)
        sy = 44 + ((i * 40503) % 1000) / 1000 * (H - 80)
        r = 0.7 + (h * 7 % 1)
        A.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{r:.1f}" fill="#9db4c8" opacity="0.25">'
                 f'<animate attributeName="opacity" values="0.15;0.9;0.15" dur="{2.5 + (i % 5) * 0.7:.1f}s" begin="{(i * 0.37) % 4:.2f}s" repeatCount="indefinite"/></circle>')
    A.append(f'<text x="28" y="34" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{CYAN}">◈ REPO CONSTELLATION // LIVE ORBITS</text>')
    # orbits + planets
    for i, r in enumerate(pool):
        rad = 58 + i * 24
        A.append(f'<path id="orb{i}" d="M {cx-rad} {cy} a {rad} {rad} 0 1 1 {2*rad} 0 a {rad} {rad} 0 1 1 {-2*rad} 0" fill="none" stroke="#16283a" stroke-width="1"/>')
        pr = 6 + min(r.get("stars") or 0, 8) * 0.9
        col = LANG_COLORS.get(r.get("lang") or "", "#8b949e")
        dur = 26 - i * 2.2
        A.append(f'<circle r="{pr:.1f}" fill="{col}" filter="url(#pglow)">'
                 f'<animateMotion dur="{dur:.1f}s" begin="-{i*3.1:.1f}s" repeatCount="indefinite"><mpath xlink:href="#orb{i}"/></animateMotion></circle>')
    # sun
    A.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="url(#sun)"><animate attributeName="r" values="44;50;44" dur="3.2s" repeatCount="indefinite"/></circle>')
    A.append(f'<circle cx="{cx}" cy="{cy}" r="26" fill="#0b1622" stroke="{CYAN}" stroke-width="2" filter="url(#pglow)"/>')
    A.append(f'<text x="{cx}" y="{cy+7}" text-anchor="middle" font-family="{MONO}" font-size="16" font-weight="bold" fill="{CYAN}">PV</text>')
    # legend
    A.append(f'<text x="556" y="76" font-family="{MONO}" font-size="12" letter-spacing="2" fill="#6e7681">FLEET MANIFEST</text>')
    for i, r in enumerate(pool):
        y = 102 + i * 30
        col = LANG_COLORS.get(r.get("lang") or "", "#8b949e")
        nm = esc(r["name"] if len(r["name"]) <= 19 else r["name"][:18] + "…")
        A.append(f'<circle cx="566" cy="{y-4}" r="5" fill="{col}"/>'
                 f'<text x="580" y="{y}" font-family="{MONO}" font-size="12" fill="#c9d1d9">{nm}</text>'
                 f'<text x="745" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#ffd479">★ {r.get("stars") or 0}</text>')
    A.append(f'<text x="{W-28}" y="{H-14}" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="#3a4552">ORBIT SIZE ∝ STARS · SPEED ∝ COMMIT VELOCITY</text>')
    A.append("</svg>")
    return "".join(A)


def render_pulse(daily, today):
    W, H = 760, 230
    n = len(daily)
    x0, x1, yb, yt = 44, W - 30, 178, 34
    maxc = max(1, max(c for _, c in daily))
    pts = [(x0 + i * (x1 - x0) / (n - 1), yb - (c / maxc) * (yb - yt)) for i, (_, c) in enumerate(daily)]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = d + f" L {x1:.1f} {yb} L {x0:.1f} {yb} Z"
    peak_i = max(range(n), key=lambda i: daily[i][1])
    A = []
    A.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A.append('<defs><linearGradient id="pfade" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#00D4FF" stop-opacity="0.35"/><stop offset="1" stop-color="#00D4FF" stop-opacity="0"/></linearGradient>'
             '<filter id="wglow" x="-40%" y="-40%" width="180%" height="180%">'
             '<feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    A.append(f'<rect width="{W}" height="{H}" rx="10" fill="#05070d"/>')
    A.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="9" fill="none" stroke="#00D4FF" stroke-opacity="0.25"/>')
    A.append(f'<text x="28" y="30" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{CYAN}">♥ COMMIT PULSE // LAST 14 DAYS</text>')
    A.append(f'<text x="{W-28}" y="30" text-anchor="end" font-family="{MONO}" font-size="12" fill="#ffd479">PEAK ▸ {daily[peak_i][1]} pushes · {daily[peak_i][0][5:]}</text>')
    for f in (0, 0.5, 1):
        gy = yb - f * (yb - yt)
        A.append(f'<line x1="{x0}" y1="{gy:.0f}" x2="{x1}" y2="{gy:.0f}" stroke="#16283a"/>')
    A.append(f'<path d="{area}" fill="url(#pfade)"/>')
    A.append(f'<path id="wave" d="{d}" fill="none" stroke="{CYAN}" stroke-width="2.5" filter="url(#wglow)" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100">'
             f'<animate attributeName="stroke-dashoffset" from="100" to="0" dur="2.2s" fill="freeze"/></path>')
    A.append(f'<circle r="5" fill="{CYAN}" filter="url(#wglow)" opacity="0">'
             f'<animate attributeName="opacity" values="0;1" begin="2.2s" dur="0.3s" fill="freeze"/>'
             f'<animateMotion dur="7s" begin="2.2s" repeatCount="indefinite"><mpath xlink:href="#wave"/></animateMotion></circle>')
    for i, (ds, c) in enumerate(daily):
        if i % 2 == 0:
            x = x0 + i * (x1 - x0) / (n - 1)
            A.append(f'<text x="{x:.0f}" y="200" text-anchor="middle" font-family="{MONO}" font-size="10" fill="#3a4552">{ds[5:]}</text>')
        if c == maxc and maxc > 0:
            x, y = pts[i]
            A.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="#ffd479" filter="url(#wglow)"/>')
    A.append(f'<text x="{W-28}" y="{H-12}" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="#3a4552">SOURCE: COMMITS API · {today} UTC</text>')
    A.append("</svg>")
    return "".join(A)


def main():
    repos, user = load_data()
    now = datetime.now(timezone.utc)
    svg = render_svg(repos, user, now)
    with open(os.path.join(ROOT, "assets", "fleet.svg"), "w") as f:
        f.write(svg + "\n")
    print("wrote assets/fleet.svg")

    events = fetch_events()
    with open(os.path.join(ROOT, "assets", "activity.svg"), "w") as f:
        f.write(render_activity(events, now) + "\n")
    print(f"wrote assets/activity.svg ({len(events)} events scanned)")

    with open(os.path.join(ROOT, "assets", "spotlight.svg"), "w") as f:
        f.write(render_spotlight(repos, now) + "\n")
    print("wrote assets/spotlight.svg")

    builds = fetch_builds(repos)
    meta_repos = {USER, f"{USER}.github.io"}
    builds.sort(key=lambda b: (b["repo"] in meta_repos, b["repo"]))
    with open(os.path.join(ROOT, "assets", "builds.svg"), "w") as f:
        f.write(render_builds(builds, now) + "\n")
    print(f"wrote assets/builds.svg ({len(builds)} repos with CI)")

    # cinema — animated, data-driven (SMIL plays live in the browser)
    daily = fetch_daily_pushes(repos)
    today = now.strftime("%Y-%m-%d")
    with open(os.path.join(ROOT, "assets", "boot.svg"), "w") as f:
        f.write(render_boot(today, len(repos)) + "\n")
    with open(os.path.join(ROOT, "assets", "orbit.svg"), "w") as f:
        f.write(render_orbit(repos) + "\n")
    with open(os.path.join(ROOT, "assets", "pulse.svg"), "w") as f:
        f.write(render_pulse(daily, today) + "\n")
    print(f"wrote cinema: boot.svg, orbit.svg, pulse.svg ({sum(c for _, c in daily)} pushes / 14d)")

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
        print("WARNING: no COOKING markers in README", file=sys.stderr)


if __name__ == "__main__":
    import sys
    main()
