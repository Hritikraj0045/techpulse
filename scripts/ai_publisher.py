#!/usr/bin/env python3
"""AI-powered TechPulse publisher using Groq GPT-OSS and built-in browser search."""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Kolkata")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MIN_WORDS = int(os.getenv("TECHPULSE_MIN_WORDS", "900"))
MAX_WORDS = int(os.getenv("TECHPULSE_MAX_WORDS", "2200"))


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def slug(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def recent_topics(state, limit=30):
    history = state.get("published_titles", [])
    return history[-limit:]


def research_and_write(client, date, history):
    prompt = f"""
You are the research editor and senior technical writer for TechPulse, an engineering publication.
Today's publication date is {date}. Select ONE timely, useful topic for software engineers.
Use the built-in browser search tool to research it before writing. Prefer official documentation, standards, original
engineering posts, release notes, and primary research. Avoid repeating these recent article titles:
{json.dumps(history, ensure_ascii=False)}

Choose a topic with practical value across backend, Python, frontend, databases, cloud/DevOps,
AI engineering, security, system design, developer tooling, or software architecture. Do not invent
breaking news or imply a release is recent unless a source confirms its date.

Write a complete, original Markdown article of approximately {MIN_WORDS}-{MAX_WORDS} words.
Return Markdown only, beginning with exactly one H1 title. Include:
- publication date and category as a short blockquote
- a concise introduction and the engineering problem
- clear explanation of core concepts and how they work
- architecture/flow (include a Mermaid diagram when it genuinely helps)
- a practical, correct code/configuration example with language-labelled fenced code
- real-world use cases and concrete trade-offs
- common implementation mistakes and security/reliability considerations
- a hands-on exercise and 5 interview/review questions
- conclusion
- An exact heading "## Sources and further reading" with at least 4 direct Markdown links to sources actually consulted.
- An exact heading "## Conclusion".
Use these exact section headings: "## Introduction", "## Sources and further reading", and "## Conclusion".
Use inline links for factual claims where possible. Never fabricate URLs, quotes, benchmarks,
release dates, API behavior, or source attributions. Distinguish established facts from your own
recommendations. If evidence is uncertain or conflicting, say so. Avoid generic filler and repetitive
sections. The article must teach a reader something concrete, not merely summarize headlines.
At the end add a short editorial note: AI-assisted research and drafting; sources should be checked
and code tested before production use.
"""
    response = client.responses.create(
        model=MODEL,
        tools=[{"type": "browser_search"}],
        tool_choice="required",
        input=prompt,
    )
    article = (response.output_text or "").strip()
    if not article:
        raise RuntimeError("The model returned an empty article.")
    return article


def validate(article):
    if not article.startswith("# "):
        raise RuntimeError("Article must begin with a single H1 title.")
    words = re.findall(r"\b[\w'-]+\b", re.sub(r"```.*?```", "", article, flags=re.S))
    if len(words) < MIN_WORDS:
        raise RuntimeError(f"Article quality gate failed: {len(words)} words; need at least {MIN_WORDS}.")
    headings = {
        re.sub(r"[：:。.!]+$", "", re.sub(r"\\s+", " ", line.lstrip("#").strip().lower()))
        for line in article.splitlines()
        if line.startswith("#")
    }
    def has_heading(target):
        return target.lower() in headings

    required = ["introduction", "sources and further reading", "conclusion"]
    missing = [heading for heading in required if not has_heading(heading)]
    if missing:
        raise RuntimeError("Missing required sections: " + ", ".join(missing))
    links = re.findall(r"\]\((https?://[^)]+)\)", article)
    if len(set(links)) < 4:
        raise RuntimeError("Article must include at least four distinct source links.")
    if article.count("```") % 2:
        raise RuntimeError("Article contains an unclosed code fence.")


def main():
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is not configured. Add it as a GitHub Actions repository secret.")
    now = datetime.now(TZ)
    if len(sys.argv) > 1:
        now = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=TZ)
    day = now.strftime("%Y-%m-%d")
    state_path = ROOT / "data/state.json"
    state = read_json(state_path, {"published_dates": [], "published_topic_ids": [], "topic_queue": []})
    folder = ROOT / "articles" / now.strftime("%Y") / now.strftime("%m-%B")
    folder.mkdir(parents=True, exist_ok=True)
    if day in state.get("published_dates", []) or any(folder.glob(day + "-*.md")):
        print("Already published for " + day + "; skipping.")
        return

    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
        timeout=240.0,
        max_retries=2,
    )
    article = research_and_write(client, day, recent_topics(state))
    validate(article)

    title = next(line[2:].strip() for line in article.splitlines() if line.startswith("# "))
    output = folder / (day + "-" + slug(title) + ".md")
    if output.exists():
        raise RuntimeError("Refusing to overwrite existing article: " + str(output))
    output.write_text(article.rstrip() + "\n", encoding="utf-8")

    state.setdefault("published_dates", []).append(day)
    state.setdefault("published_titles", []).append(title)
    state["last_topic_id"] = "ai-researched"
    state["last_title"] = title
    state["last_published_at"] = now.isoformat()
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    articles = ROOT / "articles"
    entries = []
    for path in sorted(articles.rglob("*.md"), reverse=True):
        heading = next((line[2:].strip() for line in path.read_text(encoding="utf-8").splitlines()
                        if line.startswith("# ")), path.stem)
        entries.append("- [" + heading + "](" + path.relative_to(ROOT).as_posix() + ")")
    (ROOT / "index.md").write_text(
        "# TechPulse — Article Index\n\nAI-researched technology articles for engineers.\n\n"
        + "Published articles: " + str(len(entries)) + "\n\n"
        + "\n".join(entries) + "\n", encoding="utf-8"
    )
    print(f"Published: {output.relative_to(ROOT)} ({len(article.split())} words; model={MODEL})")


if __name__ == "__main__":
    main()
