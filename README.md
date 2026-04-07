# Upwork Job Analyzer

AI-powered tool that scrapes Upwork job listings, filters them against your freelancer profile, and generates personalized cover letters. Runs locally via [LM Studio](https://lmstudio.ai/).

## Quickstart

**Prerequisites:** Python 3.9+, Chrome browser, [LM Studio](https://lmstudio.ai/) with a model loaded and server running on port 1234.

1. Run:

```bash
git clone https://github.com/Vasya619/Upwork-Job-Analyzer
cd Upwork-Job-Analyzer
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

2. Edit `files/profile.md` with your skills, experience, and writing style.
3. Edit the `upwork_url` in `main.py` to match your desired search query.
4. Run:

```bash
python main.py
```

Results are saved to a timestamped folder under `files/`:

```
files/2025-10-24_14.30.15/
├── upwork_job_listings.txt   # All scraped jobs
├── matched_jobs.txt          # Jobs matching your profile
└── cover_letter.txt          # Generated cover letters
```

## Configuration

### Scraping & Batch Settings

In `main.py`:

```python
num_jobs_per_page = 50                             # Jobs per page
num_pages = 5                                      # Pages to scrape (5 × 50 = 250 jobs)
batch_size = 10                                    # Jobs per AI classification batch (keep small for local models)
upwork_url = 'upwork.com/nx/search/jobs/?q=...'    # Upwork search query url to scrape jobs
```

Lower `batch_size` if your model has a small context window. Raise it if you have VRAM to spare.

### Environment Variables

Optional `.env` file (see `.env.example`):

```env
LM_STUDIO_API_BASE=http://localhost:1234/v1   # LM Studio server URL
LM_STUDIO_MODEL=local-model                   # Model identifier (or leave default)
```

### Profile

`files/profile.md` drives both job matching and cover letter tone. Include your skills, experience level, notable projects, and preferred writing style.

### AI Prompts

Edit `src/prompts.py` to tweak:
- **`classify_jobs_prompt`** — what counts as a good match
- **`generate_cover_letter_prompt`** — letter style, examples, structure

## How It Works

The tool runs a simple three-phase pipeline:

1. **Scrape** — Selenium with stealth mode opens Upwork, scrapes N pages of job listings, saves raw data.
2. **Classify** — Jobs are split into small batches and sent to your local LLM. The model compares each job against your profile and returns matches with reasons.
3. **Generate** — For each matched job, the LLM writes a personalized cover letter. All letters are saved with job metadata (title, link).

Each run creates a new timestamped folder, so previous results are never overwritten.

### Project Structure

```
├── main.py              # Entry point & config
├── requirements.txt
├── files/
│   ├── profile.md       # Your freelancer profile
│   └── <timestamp>/     # Output folders per run
└── src/
    ├── agent.py          # LM Studio API client
    ├── graph.py          # Workflow pipeline
    ├── prompts.py        # AI prompts
    └── utils.py          # Scraping & file utilities
```

### Troubleshooting

| Issue | Fix |
|-------|-----|
| No jobs found | Cloudflare blocked the scraper — increase `time.sleep()` in `utils.py` |
| Classification fails | Reduce `batch_size` in `main.py` |
| Connection refused | Make sure LM Studio server is running on the configured port |
| Empty matches | Improve `files/profile.md` with more detail |

## Credits

Fork of [Upwork-Auto-Jobs-Applier-using-AI](https://github.com/AIXerum/Upwork-Auto-Jobs-Applier-using-AI) by [AIXerum](https://github.com/AIXerum). Extended with multi-page scraping, batch classification, local LLM support, and timestamped output.
