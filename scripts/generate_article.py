#!/usr/bin/env python3
"""Topic-specific no-API TechPulse article publisher."""
import argparse, json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Kolkata")
F = chr(96) * 3

def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def slug(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")

def select_topic(topics, state, forced=None):
    lookup = {x["id"]: x for x in topics}
    if forced:
        if forced not in lookup:
            raise SystemExit("Unknown topic id: " + forced)
        return lookup[forced]
    used = set(state.get("published_topic_ids", []))
    remaining = [x for x in topics if x["id"] not in used]
    if not remaining:
        state["published_topic_ids"] = []
        remaining = topics[:]
    queue = [x for x in state.get("topic_queue", []) if x in lookup and x not in used]
    if not queue:
        queue = [x["id"] for x in remaining]
    selected = queue.pop(0)
    state["topic_queue"] = queue
    return lookup[selected]

def language(topic_id):
    return {"sql-indexes":"sql", "docker-containers":"dockerfile",
            "kubernetes-basics":"yaml", "web3-smart-contracts":"solidity",
            "react-state":"jsx"}.get(topic_id, "python")

def build_article(topic, bp, now):
    title = topic["title"]
    lines = [
        "# " + title, "",
        "> **Published:** " + now.strftime("%Y-%m-%d") + "  ",
        "> **Category:** " + topic["category"] + "  ",
        "> **Tags:** " + ", ".join(topic.get("tags", [])), "",
        "## Introduction", "", bp["problem"], "",
        "This technical guide connects the underlying concepts to architecture, implementation, operational trade-offs, and practical engineering decisions. It is designed as an educational starting point; check the linked primary documentation for version-specific behavior.", "",
        "## 1. The engineering problem", "", bp["problem"], "",
        "Before adopting a technology, define the workload, expected inputs and outputs, scale, latency needs, failure modes, data sensitivity, and operational ownership. Those constraints determine whether the technology is appropriate and how success should be measured.", "",
        "## 2. Core concepts", ""
    ]
    for n, pair in enumerate(bp["concepts"], 1):
        lines += ["### 2." + str(n) + " " + pair[0], "", pair[1], ""]
    lines += ["## 3. Architecture and flow", "",
              "The diagram is a simplified conceptual view. Production systems may add authentication, queues, caches, retries, observability, and recovery paths.", "",
              F + "mermaid", "flowchart TD"]
    nodes = [re.sub(r"\s+", " ", x.strip()).replace('"', "'") for x in bp["flow"].split("-->")]
    for n, node in enumerate(nodes):
        lines.append('    N' + str(n) + '["' + node + '"]')
    for n in range(len(nodes)-1):
        lines.append("    N" + str(n) + " --> N" + str(n+1))
    lines += [F, "", "### Understanding the flow", ""]
    for n, node in enumerate(nodes, 1):
        lines.append(str(n) + ". **" + node + ":** identify the inputs, outputs, owner, and failure behavior at this stage.")
    lines += ["", "Trace data across each boundary. Ask where validation occurs, which component owns state, how timeouts and partial failures are handled, and what telemetry helps an operator diagnose a problem.", "",
              "## 4. Practical code example", "",
              "The following example illustrates a relevant building block. It is not a complete production service. Add project-specific configuration, tests, dependency management, logging, and error handling before deployment.", "",
              F + language(topic["id"])]
    lines += bp["code"].strip().splitlines()
    lines += [F, "", "### What to review in the example", "",
              "- Validate untrusted inputs at system boundaries.",
              "- Keep each function or component focused on one responsibility.",
              "- Define behavior for invalid input and unavailable dependencies.",
              "- Test normal cases, edge cases, and failure paths.",
              "- Prefer maintained libraries for security-sensitive and protocol-heavy work.", "",
              "## 5. Real-world use cases", ""]
    lines += ["- " + x + "." for x in bp["use"]]
    lines += ["", "Use the technology when its strengths solve a real requirement better than a simpler alternative. Introducing another dependency also introduces maintenance and operational cost.", "",
              "## 6. Trade-offs and design decisions", ""]
    lines += ["- " + x for x in bp["tradeoffs"]]
    lines += ["", "Validate decisions against representative workload data. Benchmarks should reflect real request shapes, data sizes, concurrency, failure conditions, and deployment environments.", "",
              "## 7. Common mistakes", ""]
    lines += ["- " + x for x in bp["mistakes"]]
    lines += ["", "Also avoid copying configuration from an unrelated software version. Consult versioned documentation and test changes safely before production rollout.", "",
              "## 8. Hands-on learning exercise", "",
              "1. Reproduce the example in an isolated project.",
              "2. Draw the components and label the data crossing each boundary.",
              "3. Add tests for a valid case, invalid input, and dependency failure.",
              "4. Measure one meaningful property such as latency, throughput, memory, or retrieval quality.",
              "5. Change one design decision and compare the result.",
              "6. Record when a simpler alternative would be preferable.", "",
              "## 9. Interview and review questions", ""]
    lines += ["- " + q for q in bp["questions"]]
    lines += ["", "Answer each question with a concrete example. A strong explanation connects a definition to its mechanism, a trade-off, and a situation where it matters.", "",
              "## Conclusion", "",
              title + " is best understood as an engineering choice with specific strengths, limitations, and operational consequences. Start from the problem, understand the lifecycle and boundaries, validate the design with tests and measurements, and account for security, reliability, observability, and maintainability.", "",
              "## References and further reading", ""]
    lines += ["- [" + ref + "](" + ref + ")" for ref in topic.get("references", [])]
    lines += ["", "## Editorial note", "",
              "This article is assembled from a curated, topic-specific editorial blueprint without an external AI service. It does not claim to be live research or independent fact-checking. Review claims and test code against current official documentation before relying on it.", ""]
    return "\n".join(lines)

def rebuild_index(root):
    articles = root / "articles"
    entries = []
    for path in sorted(articles.rglob("*.md"), reverse=True):
        try:
            heading = next((x[2:].strip() for x in path.read_text(encoding="utf-8").splitlines() if x.startswith("# ")), path.stem)
        except OSError:
            continue
        entries.append("- [" + heading + "](" + path.relative_to(root).as_posix() + ")")
    (root / "index.md").write_text("# TechPulse — Article Index\n\nA growing collection of educational technology articles.\n\nPublished articles: " + str(len(entries)) + "\n\n" + "\n".join(entries) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-id")
    parser.add_argument("--date")
    args = parser.parse_args()
    now = datetime.now(TZ)
    if args.date:
        now = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=TZ)
    topics = read_json(ROOT / "data/topics.json", [])
    blueprints = {x["id"]: x for x in read_json(ROOT / "data/blueprints.json", [])}
    state_path = ROOT / "data/state.json"
    state = read_json(state_path, {"published_topic_ids": [], "published_dates": [], "topic_queue": []})
    topic = select_topic(topics, state, args.topic_id)
    bp = blueprints.get(topic["id"])
    if not bp:
        raise SystemExit("Missing blueprint for topic: " + topic["id"])
    day = now.strftime("%Y-%m-%d")
    folder = ROOT / "articles" / now.strftime("%Y") / now.strftime("%m-%B")
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / (day + "-" + slug(topic["title"]) + ".md")
    if output.exists() or day in state.get("published_dates", []):
        print("Already published for " + day + "; skipping.")
        return
    content = build_article(topic, bp, now)
    count = len(re.findall(r"\b[\w'-]+\b", re.sub(r"```.*?```", "", content, flags=re.S)))
    if count < 650:
        raise SystemExit("Quality gate failed: article has only " + str(count) + " words.")
    output.write_text(content, encoding="utf-8")
    state.setdefault("published_topic_ids", []).append(topic["id"])
    state.setdefault("published_dates", []).append(day)
    state["last_topic_id"] = topic["id"]
    state["last_published_at"] = now.isoformat()
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    rebuild_index(ROOT)
    print("Generated " + str(output.relative_to(ROOT)) + " (" + str(count) + " words)")

if __name__ == "__main__":
    main()
