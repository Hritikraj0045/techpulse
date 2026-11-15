# TechPulse — Automated Technology Blog

TechPulse generates one educational technology article per day and commits it to this repository. It requires **no AI provider, API key, or third-party Python package**.

## What it does

- Runs daily at 06:00 India Standard Time (00:30 UTC).
- Rotates through a curated topic catalogue in `data/topics.json`.
- Generates Markdown articles in `articles/YYYY/MM-Month/`.
- Records published dates and topic IDs in `data/state.json`.
- Skips a date that has already been published.
- Can also be run manually from GitHub Actions.

## Important limitation

This is a deterministic template-and-topic engine, not an AI researcher. It creates structured educational drafts from curated topic metadata. It does not browse the web, discover breaking news, or independently fact-check claims. Review articles before treating them as authoritative. The article's code sample is illustrative.

## Create your new GitHub repository

1. On GitHub, create a new repository named `techpulse` (or another name you prefer).
2. Choose **Public** if you want the articles to be publicly visible; choose Private otherwise.
3. Initialize it with a README or leave it empty.
4. Download/extract this project locally.
5. From the extracted project folder, run:

   ```bash
   git init
   git add .
   git commit -m "chore: initialize TechPulse"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/techpulse.git
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` and the repository name as needed. If Git says the remote contains work that you do not have locally because you initialized it with a README, first run `git pull --rebase origin main`, resolve any conflict, then push.

## Enable workflow write access

In the repository:
1. Open **Settings → Actions → General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Save.
4. Open **Actions** and enable workflows if GitHub asks.

The workflow uses the built-in `GITHUB_TOKEN`; no personal access token or secret is required.

## Test locally

Python 3.9+ is required (the workflow uses Python 3.12).

```bash
python scripts/generate_article.py
```

Generate a specific topic:

```bash
python scripts/generate_article.py --topic-id docker-containers
```

Test a date without waiting:

```bash
python scripts/generate_article.py --date 2026-11-15
```

The test command writes an article and updates `data/state.json`. If you test using today's date, the scheduled run will correctly skip that date. To reset local test history, restore `data/state.json` from Git or remove its contents and set it to:

```json
{
  "published_topic_ids": [],
  "published_dates": [],
  "topic_queue": []
}
```

## Add topics

Edit `data/topics.json`. Each topic needs:
- `id`: unique stable identifier
- `title`, `category`, `tags`
- `focus`, `example`, `pitfalls`
- `questions`: list of review questions
- `references`: list of primary or reputable URLs

Avoid reusing an `id` for a different subject. The topic ID is used for rotation and duplicate prevention.

## Article publishing and duplicate prevention

The generator prevents more than one article from being recorded for the same local calendar date. It also avoids repeating a topic until all currently curated topics have been used once. Once the queue is exhausted, a new rotation begins.

For a larger publication, consider adding a human review step, richer topic-specific article content, automated link checking, and a real research/LLM layer later.

## Schedule

GitHub Actions scheduled workflows use UTC. `30 0 * * *` corresponds to 06:00 in India (UTC+05:30). GitHub may delay scheduled runs during periods of high load. Use **Actions → TechPulse Daily Blog → Run workflow** to publish manually.
