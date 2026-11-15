# TechPulse — Automated Technology Blog

TechPulse publishes one educational technology article per day using Python and GitHub Actions. It requires no paid AI provider, API key, or third-party Python package.

## What it does
- Runs daily at 06:00 India Standard Time (00:30 UTC).
- Rotates through the topic catalogue without repeating topics until a full rotation is exhausted.
- Uses topic-specific editorial blueprints.
- Produces concepts, Mermaid flow diagrams, relevant code samples, use cases, trade-offs, common mistakes, exercises, interview questions, and references.
- Maintains publication history and rebuilds the article index.
- Prevents more than one publication per local calendar date.

## Content model and limitations
This is a deterministic editorial engine, not an AI researcher. Explanations and examples are curated in the blueprint file. It does not browse for breaking news or independently fact-check sources. A length check is not a factual accuracy check. Review and test content before treating it as authoritative.

## Key files
- `data/topics.json`: topic catalogue, tags, categories, and references.
- `data/blueprints.json`: topic-specific explanations, diagrams, code, use cases, trade-offs, mistakes, and questions.
- `scripts/generate_article.py`: article generation, duplicate prevention, and index rebuild.
- `data/state.json`: publication history and topic rotation.
- `index.md`: automatically rebuilt article index.

## Run locally
Python 3.9+:
```bash
python scripts/generate_article.py
python scripts/generate_article.py --topic-id docker-containers
python scripts/generate_article.py --date 2026-11-16
```
A date already in the publication history is skipped.

## Add a topic
Add a topic to `data/topics.json` and a matching blueprint to `data/blueprints.json`. The IDs must match. Use authoritative references and verify version-specific claims before public use.

## GitHub setup
1. Push the project to the repository's default branch.
2. Open Settings → Actions → General.
3. Enable Read and write permissions under Workflow permissions.
4. Ensure Actions is enabled.
5. Run Actions → TechPulse Daily Blog → Run workflow to test.

The workflow uses GitHub's built-in GITHUB_TOKEN; no personal access token is required. GitHub scheduled jobs can be delayed during high-load periods.

## Schedule
GitHub cron is UTC. 30 0 * * * is 06:00 in India (UTC+05:30).
