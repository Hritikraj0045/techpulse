# TechPulse — AI-Powered Technology Blog

TechPulse researches and publishes one educational technology article per day using Groq GPT-OSS, built-in browser search, Python, and GitHub Actions.

## What it does

- Runs daily at 06:00 India Standard Time (00:30 UTC).
- Uses AI-assisted web research to select a useful engineering topic and draft an original article.
- Uses Groq built-in browser search during generation; the article must include links to sources actually consulted.
- Covers engineering concepts, architecture, practical code, use cases, trade-offs, mistakes, exercises, and interview questions.
- Validates article structure, minimum length, source links, and code-fence balance before publishing.
- Maintains publication history, prevents duplicate daily articles, and rebuilds the article index.
- Supports manual execution through GitHub Actions.

## Architecture

```text
GitHub Actions (daily schedule)
        |
        v
AI Publisher (scripts/ai_publisher.py)
        |
        +--> Groq Responses API
        |       |
        |       +--> Web search for current source material
        |       +--> Topic selection and research synthesis
        |       +--> Markdown article drafting
        |
        v
Quality gates
        |
        +--> Required sections and minimum word count
        +--> At least four distinct source links
        +--> Code-fence validation
        |
        v
Article archive + publication state + index.md
        |
        v
Git commit and push
```

The existing deterministic publisher (`scripts/generate_article.py`) and curated blueprints remain available as a no-API fallback for local experimentation. The scheduled workflow now uses the AI publisher.

## Setup

### 1. Create a Groq API key

Create an API key in the Groq Console. API usage is billed separately from a ChatGPT subscription.

### 2. Add the GitHub Actions secret

In the repository, open:

**Settings → Secrets and variables → Actions → New repository secret**

Add:

- Name: `GROQ_API_KEY`
- Value: your API key

Never commit the key to the repository or put it in source code.

### 3. Optional model configuration

Under **Settings → Secrets and variables → Actions → Variables**, add:

- Name: `GROQ_MODEL`
- Value: a model available to your API project (default: `openai/gpt-oss-120b`)

### 4. Run a manual test

Open **Actions → TechPulse Daily Blog → Run workflow**.

Check the workflow logs and inspect the generated article under `articles/YYYY/MM-Month/`.

## Run locally

Python 3.10+ is required.

```bash
python -m pip install openai
export GROQ_API_KEY="your-key"
export GROQ_MODEL="openai/gpt-oss-120b"  # optional
python scripts/ai_publisher.py
```

On Windows PowerShell:

```powershell
python -m pip install openai
$env:GROQ_API_KEY="your-key"
$env:GROQ_MODEL="openai/gpt-oss-120b"  # optional
python scripts/ai_publisher.py
```

To generate for a specific date:

```bash
python scripts/ai_publisher.py 2026-11-16
```

A date already present in publication history is skipped.

## Project structure

- `scripts/ai_publisher.py`: AI research, article drafting, validation, and publishing.
- `scripts/generate_article.py`: deterministic curated-content publisher.
- `data/topics.json`: original topic catalogue.
- `data/blueprints.json`: curated topic-specific fallback material.
- `data/state.json`: publication dates, titles, and rotation state.
- `articles/`: dated Markdown articles.
- `index.md`: automatically rebuilt article index.
- `.github/workflows/daily-blog.yml`: daily automation.

## Editorial and reliability notes

AI web research and structural checks do not guarantee factual correctness. A source link can be valid without supporting every claim. Review important claims, check source dates and version compatibility, and test code before production use. The publisher fails rather than publishing if the API key is missing, the response is empty, required sections are missing, the article is too short, or there are fewer than four distinct linked sources.

GitHub scheduled workflows may start later than the requested cron time during periods of high load. The workflow needs repository Actions write permissions to commit generated articles.
