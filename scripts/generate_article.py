#!/usr/bin/env python3
"""Generate one educational technology article without an external AI/API."""
from __future__ import annotations
import argparse, json, random, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TOPICS_FILE = ROOT / "data" / "topics.json"
STATE_FILE = ROOT / "data" / "state.json"
ARTICLES_DIR = ROOT / "articles"

def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def slugify(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")

def choose_topic(topics, state, forced_id=None):
    by_id = {t["id"]: t for t in topics}
    if forced_id:
        if forced_id not in by_id:
            raise SystemExit(f"Unknown topic id: {forced_id}")
        return by_id[forced_id]
    used = set(state.get("published_topic_ids", []))
    available = [t for t in topics if t["id"] not in used]
    if not available:
        # Start a new rotation only after every curated topic has been used.
        state["published_topic_ids"] = []
        available = topics[:]
    # Stable daily selection: randomize the order once per rotation, then persist it.
    queue = state.get("topic_queue", [])
    queue = [topic_id for topic_id in queue if topic_id in by_id and topic_id not in used]
    if not queue:
        queue = [t["id"] for t in available]
        random.Random(datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()).shuffle(queue)
    selected_id = queue[0]
    state["topic_queue"] = queue[1:]
    return by_id[selected_id]

def article_markdown(topic, now):
    date = now.strftime("%Y-%m-%d")
    title = topic["title"]
    tags = ", ".join(topic["tags"])
    focus = topic["focus"]
    example = topic["example"]
    pitfalls = topic["pitfalls"]
    questions = topic["questions"]
    refs = topic["references"]

    sections = [
        f"# {title}",
        "",
        f"> **Published:** {date}  ",
        f"> **Category:** {topic['category']}  ",
        f"> **Tags:** {tags}",
        "",
        "## Introduction",
        "",
        f"Modern technology is less about choosing a fashionable tool and more about understanding the problem a tool is designed to solve. This article examines **{title.lower()}** from that practical engineering perspective. The goal is to build a mental model that helps when designing, implementing, reviewing, or operating real systems.",
        "",
        f"The central area covered here is {focus} This matters because technical decisions rarely exist in isolation: they affect maintainability, reliability, performance, security, cost, and the experience of the people using the system.",
        "",
        "## 1. The problem and the core idea",
        "",
        f"A useful starting point is to ask what constraint or recurring problem this technology addresses. In this topic, the key concerns are {focus.lower()} A good implementation begins by identifying the workload, its constraints, and the outcome that needs to improve.",
        "",
        "Avoid starting with configuration copied from a tutorial. First write down the expected inputs, outputs, failure cases, scale, and operational requirements. That simple exercise often reveals whether the technology is appropriate at all.",
        "",
        "## 2. How the main concepts fit together",
        "",
        f"The important concepts to understand include {focus} They should be treated as connected parts of a system rather than isolated vocabulary.",
        "",
        "A practical way to reason about the design is to follow the lifecycle:",
        "",
        "1. **Input:** identify where data or requests originate and validate assumptions at the boundary.",
        "2. **Processing:** understand which component performs the main work and what state it owns.",
        "3. **Communication:** define how components exchange information, including timeouts and error behavior.",
        "4. **Persistence:** decide what must survive a restart and how consistency is maintained.",
        "5. **Operations:** decide what to measure, how to deploy changes, and how to recover from failure.",
        "",
        "This lifecycle is useful because many production issues occur between components, not inside the happy-path code of one component.",
        "",
        "## 3. A practical engineering example",
        "",
        f"The following is an illustrative exercise related to this topic: **{example}**",
        "",
        "Use the example as a starting point rather than a production-ready implementation. Before adopting it, add input validation, explicit error handling, tests, configuration management, and observability appropriate to the application.",
        "",
        "```python",
        "def process_item(item):",
        '    """Illustrative boundary for a small, testable unit of work."""',
        "    if item is None:",
        '        raise ValueError("item must not be None")',
        "",
        "    # Keep the core operation explicit and easy to test.",
        "    result = {",
        '        "status": "processed",',
        '        "value": item,',
        "    }",
        "    return result",
        "",
        'if __name__ == "__main__":',
        '    print(process_item("example"))',
        "```",
        "",
        "The example deliberately keeps the business operation small. In a real application, the function would call the relevant library or service for the chosen technology. Keeping that dependency behind a clear boundary makes it easier to test behavior and replace implementation details later.",
        "",
        "## 4. Design decisions and trade-offs",
        "",
        "There is rarely a universally best design. Evaluate at least these dimensions:",
        "",
        "- **Correctness:** does the design preserve the required behavior under normal and failure conditions?",
        "- **Performance:** what is the actual bottleneck, and has it been measured?",
        "- **Reliability:** what happens when a dependency is slow, unavailable, or returns malformed data?",
        "- **Security:** are identity, permissions, secrets, and untrusted inputs handled deliberately?",
        "- **Maintainability:** can another developer understand and safely change the implementation?",
        "- **Cost:** what are the infrastructure, licensing, operational, and engineering costs?",
        "",
        f"For this particular subject, pay special attention to {pitfalls} A small proof of concept and representative measurements are usually more useful than assumptions based on benchmark headlines.",
        "",
        "## 5. Common mistakes to avoid",
        "",
        f"Some recurring mistakes are: {pitfalls}",
        "",
        "A useful review checklist is to ask whether the implementation has explicit boundaries, sensible defaults, meaningful failure behavior, tests for edge cases, and enough telemetry to diagnose problems. Also check the official documentation for version-specific behavior: defaults and recommended practices can change.",
        "",
        "## 6. A step-by-step learning exercise",
        "",
        "To turn the concepts into practical knowledge:",
        "",
        "1. Build the smallest working example in an isolated project.",
        "2. Write down the expected behavior before adding complexity.",
        "3. Add tests for valid input, invalid input, and dependency failure.",
        "4. Measure the behavior with representative data rather than guessing.",
        "5. Add logging and metrics that help explain what the system is doing.",
        "6. Document the trade-offs and the conditions under which you would choose another approach.",
        "",
        "## 7. Questions to check your understanding",
        "",
    ]
    for q in questions:
        sections.append(f"- {q}")
    sections += [
        "",
        "Try answering these without looking back at the article. Then explain the concept to another developer and identify one real system where the trade-offs would matter.",
        "",
        "## Conclusion",
        "",
        f"Understanding {title.lower()} means understanding both the underlying idea and the operational consequences of using it. Strong engineering comes from matching a tool to a clearly defined problem, validating assumptions with tests and measurements, and making trade-offs visible. Start small, consult primary documentation, and evolve the design as real requirements become clearer.",
        "",
        "## Further reading",
        "",
    ]
    for ref in refs:
        sections.append(f"- [{ref}]({ref})")
    sections += [
        "",
        "## Editorial note",
        "",
        "This is an automatically generated educational overview. Examples are illustrative and should be reviewed, tested, and adapted before production use. Always consult the linked primary documentation for current, version-specific details.",
        "",
    ]
    return "\n".join(sections)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-id", help="Generate a specific topic (useful for local testing).")
    parser.add_argument("--date", help="Override date in YYYY-MM-DD format (useful for testing).")
    args = parser.parse_args()

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    if args.date:
        now = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    topics = load_json(TOPICS_FILE, [])
    state = load_json(STATE_FILE, {"published_topic_ids": [], "published_dates": [], "topic_queue": []})
    topic = choose_topic(topics, state, args.topic_id)

    year = now.strftime("%Y")
    month = now.strftime("%m-%B")
    out_dir = ARTICLES_DIR / year / month
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{now.strftime('%Y-%m-%d')}-{slugify(topic['title'])}.md"
    out_path = out_dir / filename

    if out_path.exists() or now.strftime("%Y-%m-%d") in state.get("published_dates", []):
        print(f"An article is already recorded for {now.date()}; skipping.")
        return

    out_path.write_text(article_markdown(topic, now), encoding="utf-8")
    state.setdefault("published_topic_ids", []).append(topic["id"])
    state.setdefault("published_dates", []).append(now.strftime("%Y-%m-%d"))
    state["last_topic_id"] = topic["id"]
    state["last_published_at"] = now.isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Generated: {out_path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
