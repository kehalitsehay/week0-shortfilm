"""Build showcase/index.html: a static page (GitHub Pages / Hugging Face static Space ready)
that plays the film and shows why every shot exists."""
import html
from collections import Counter
from .core import config, runlog

CSS = """
:root{--bg:#0f1722;--ink:#ece6da;--dim:#93a0b3;--ember:#f0a646;--line:#25324a;color-scheme:dark}
@media (prefers-color-scheme:light){:root{--bg:#f5efe3;--ink:#1b2331;--dim:#5b6678;--ember:#b4620b;--line:#d9cfba;color-scheme:light}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 Georgia,'Iowan Old Style',serif}
main{max-width:1040px;margin:0 auto;padding:clamp(20px,5vw,64px)}
h1{font-size:clamp(2.2rem,6vw,4.2rem);line-height:1.08;margin:0 0 .4em;max-width:16ch;font-weight:600}
h2{font-size:1.4rem;margin:2.4em 0 .6em}
.lede{color:var(--dim);max-width:52ch;margin:0 0 2em}
.film{display:grid;grid-template-columns:minmax(0,320px) minmax(0,1fr);gap:clamp(20px,4vw,48px);align-items:start}
video{width:100%;background:#000;border-radius:6px;display:block}
.film p{margin:.2em 0 1em;color:var(--dim)}
.shot{display:grid;grid-template-columns:3.2rem 1fr;gap:0 1rem;padding:1.1em 0;border-top:1px solid var(--line)}
.shot b{color:var(--ember);font-weight:600}.shot q{display:block;margin-top:.3em;font-style:italic}
.shot span{color:var(--dim)}
.stats{display:flex;gap:2.5em;flex-wrap:wrap;margin:0}.stats div{min-width:6em}
.stats dt{color:var(--dim);font-size:.9rem}.stats dd{margin:0;font-size:1.8rem;color:var(--ember)}
footer{margin-top:4em;color:var(--dim);font-size:.9rem}
a{color:var(--ember)}
@media (max-width:720px){.film{grid-template-columns:1fr}}
"""


def build(sb) -> str:
    runs = runlog.read_all()
    fresh = [r for r in runs if not r.get("cache_hit")]
    hits = sum(1 for r in runs if r.get("cache_hit"))
    stages = Counter(r["stage"] for r in fresh)
    e = html.escape
    shots = "".join(
        f"<div class='shot'><b>{e(s['id'])}</b><div>{e(s['reason'])}"
        f"<q>{e(s['narration']['text'])}</q><span>{e(s['narration']['speaker'].replace('_', ' '))}</span></div></div>"
        for s in sb.shots)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(sb['title'])}</title>
<style>{CSS}</style></head><body><main>
<h1>Time is the only currency you cannot earn back.</h1>
<p class="lede">{e(sb['title'])}: a {int(sb.runtime_estimate())}-second short about a young man who keeps promising to start tomorrow.
Written, voiced and scored with AI, assembled by a small Python pipeline that reads one file, storyboard.json.</p>
<div class="film"><div><video controls preload="metadata" playsinline src="../outputs/film_9x16.mp4"></video></div>
<div><p>Vertical cut for phones. The widescreen cut is <a href="../outputs/film_16x9.mp4">here</a>.</p>
<p>This film uses AI-generated images, voices and music. It was made with the Heritage Short pipeline; every model call is logged.</p>
<dl class="stats"><div><dt>shots</dt><dd>{len(sb.shots)}</dd></div>
<div><dt>model calls logged</dt><dd>{len(fresh)}</dd></div>
<div><dt>cache hits</dt><dd>{hits}</dd></div></dl></div></div>
<h2>Why each shot exists</h2>{shots}
<footer>Made with AI. Stages: {', '.join(f'{k} ({v})' for k, v in stages.items()) or 'not run yet'}.</footer>
</main></body></html>"""
    out = config.ROOT / "showcase" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)
    return str(out)
