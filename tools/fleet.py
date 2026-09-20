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
