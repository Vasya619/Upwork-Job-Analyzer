# Upwork-Job-Analyzer: Automated Jobs Application on Upwork

**Upwork-Job-Analyzer is not just a tool; it's your intelligent partner in navigating the competitive world of freelancing, helping you process hundreds of jobs, secure more projects, and grow your freelance career. 🚀**

## Introduction

**Upwork-Job-Analyzer** is a scalable AI-powered tool designed to simplify and accelerate the freelance job application process on Upwork. In today's fast-paced gig economy, where opportunities can disappear within hours, this system offers freelancers a significant edge. By harnessing the power of AI automation with intelligent batching, it enables freelancers to efficiently process hundreds of job listings across multiple pages, identify the best matches, and generate personalized cover letters—all organized in timestamped folders for easy tracking and review.

## The Challenge of Modern Freelancing

The freelance marketplace has undergone a dramatic transformation in the digital age. While platforms like Upwork have opened up a world of opportunities, they have also intensified competition. Freelancers often find themselves spending countless hours searching through hundreds of job listings, tailoring proposals, and crafting unique cover letters. This process can be not only time-consuming but also mentally exhausting, leading to missed opportunities and proposal fatigue.

## Enter Upwork-Job-Analyzer: Your Intelligent Freelance Assistant

Upwork-Job-Analyzer steps in as a game-changing solution to these challenges. It's not just a tool; it's your tireless, scalable, 24/7 freelance proposal partner. By automating the most time-consuming aspects of the job search and application process—including multi-page scraping, batch classification, and organized file management—it allows you to focus on what truly matters: preparing for client interviews and delivering outstanding work.

## Key Features

### 🔍 Multi-Page Job Scraping
- **Configurable page scraping**: Process 5, 10, or more pages in a single run (250-500+ jobs)
- **Selenium with stealth mode**: Bypasses Cloudflare protection for reliable scraping
- **Smart delays**: Automatic wait times between pages to avoid rate limiting
- **Customizable search criteria**: Define your own Upwork search URLs and filters

### 🤖 Intelligent Batch Classification
- **AI-powered matching**: Uses Google Gemini 2.5 Flash to analyze job descriptions against your profile
- **Scalable batch processing**: Splits large job lists (250+ jobs) into manageable batches (50-100 jobs each)
- **Context-aware filtering**: Identifies jobs that match your skills, experience, and preferences
- **Progress tracking**: Real-time feedback on classification progress (`Batch 3/5: 12 matches found`)

### ✍️ Personalized Cover Letter Generation
- **Dynamic creation**: Generates unique cover letters tailored to each matched job
- **Profile-based personalization**: Aligns with your writing style, skills, and past experiences
- **Keyword optimization**: Improves proposal relevance for better visibility
- **Rate limiting**: 6-second delay between generations to respect API limits

### 📁 Timestamped Run Organization
- **Isolated run folders**: Each execution creates a new timestamped folder (`files/2025-10-24_14.30.15/`)
- **Complete history**: All runs preserved with three files per run:
  - `upwork_job_listings.txt`: All scraped jobs (raw data)
  - `matched_jobs.txt`: Filtered jobs that match your profile with match reasons
  - `cover_letter.txt`: Generated cover letters with job metadata (title, link, match number)
- **No overwrites**: Previous runs remain untouched, enabling easy comparison and tracking

### 📊 Enhanced Logging & Progress Tracking
- **Color-coded output**: Visual feedback with emojis and colored text
- **Batch progress**: Shows current batch, job range, and matches found
- **Error handling**: Graceful degradation if individual batches or generations fail
- **Summary statistics**: Total jobs scraped, classified, and matched

## How It Works

### Architecture Overview

The system follows a **scrape-all-then-batch-classify** approach for optimal performance:

1. **Multi-Page Scraping** (Phase 1)
   - Opens a single browser session with stealth settings
   - Scrapes pages 1-N sequentially (configurable, default 5-8 pages)
   - Extracts job title, description, link, budget, experience level, and job type
   - Saves all jobs to timestamped folder: `files/YYYY-MM-DD_HH.MM.SS/upwork_job_listings.txt`

2. **Batch Classification** (Phase 2)
   - Splits scraped jobs into batches (default 50-100 jobs per batch)
   - Sends each batch to Gemini AI classifier
   - AI analyzes jobs against your freelancer profile
   - Aggregates matches from all batches
   - Saves matched jobs with detailed formatting and match reasons

3. **Cover Letter Generation** (Phase 3)
   - Processes each matched job sequentially
   - Generates personalized cover letter using AI
   - Includes job metadata (Match #, title, link) for easy reference
   - Applies 6-second delay between generations
   - Saves all letters to same timestamped folder

4. **Review & Track** (Phase 4)
   - All outputs saved in organized timestamped folders
   - Easy to compare runs from different days
   - No risk of overwriting previous work
   - Ready for manual review before submission

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Upwork-Job-Analyzer WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

📁 CREATE RUN FOLDER
   │ files/2025-10-24_14.30.15/
   ├── upwork_job_listings.txt (created in Phase 1)
   ├── matched_jobs.txt (created in Phase 2)
   └── cover_letter.txt (created in Phase 3)

🔍 PHASE 1: MULTI-PAGE SCRAPING
   │
   ├─► Open Chrome with Stealth Mode
   ├─► Loop through pages 1-8 (configurable)
   │   ├─► Wait for Cloudflare bypass (5-15s)
   │   ├─► Extract job listings (title, link, description, budget, etc.)
   │   └─► Delay 5s between pages
   ├─► Save all jobs to upwork_job_listings.txt
   └─► Total: 400 jobs scraped

🤖 PHASE 2: BATCH CLASSIFICATION
   │
   ├─► Split 400 jobs into batches of 100
   ├─► For each batch (4 batches total):
   │   ├─► Send batch to Gemini AI Classifier
   │   ├─► AI compares against freelancer profile
   │   ├─► Returns matched jobs with reasons
   │   └─► Progress: "Batch 2/4: 15 matches found"
   ├─► Aggregate all matches (60 total matches)
   └─► Save to matched_jobs.txt with formatting

✍️ PHASE 3: COVER LETTER GENERATION
   │
   ├─► For each of 60 matched jobs:
   │   ├─► Send job description to Gemini Writer Agent
   │   ├─► Generate personalized cover letter
   │   ├─► Add metadata (Match #, title, link)
   │   ├─► Save to cover_letter.txt
   │   └─► Delay 6 seconds (rate limiting)
   └─► Complete: 60 cover letters generated

📊 RESULTS
   │
   ├─► 400 jobs scraped from 8 pages
   ├─► 60 jobs matched your profile (15% match rate)
   ├─► 60 personalized cover letters ready
   └─► All saved in files/2025-10-24_14.30.15/
```

## Tech Stack & Architecture

### **Core Technologies**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Workflow Engine** | LangGraph | Orchestrates multi-step workflow with precise control |
| **AI Model** | Google Gemini 2.5 Flash | Classification and cover letter generation |
| **LLM Gateway** | LiteLLM | Unified interface for multiple AI providers |
| **Web Scraping** | Selenium + selenium-stealth | Cloudflare bypass and job extraction |
| **File Management** | Python `os`, `json`, `datetime` | Timestamped folder organization |

### **Why LangGraph?**

For building agentic workflows, there are multiple popular frameworks available, such as CrewAI, AutoGen, or Agency Swarm. However, most of them grant full autonomy to the agents while accomplishing tasks and do not provide control over the working process of the agents.

**LangGraph advantages for this project:**
- **Precise control**: Define exactly when each agent or tool is called
- **Conditional routing**: Smart decisions based on state (e.g., "no matches" → end workflow)
- **Hybrid nodes**: Mix LLM calls with pure Python logic (scraping doesn't need AI)
- **State management**: Pass data between nodes with typed dictionaries
- **Cost efficiency**: Only invoke AI when necessary, reducing API costs

**Example workflow graph:**
```python
graph.add_node("scrape_upwork_jobs", self.scrape_upwork_jobs)
graph.add_node("classify_scraped_jobs", self.classify_scraped_jobs)
graph.add_conditional_edges(
    "check_for_job_matches",
    self.need_to_process_matches,
    {"Process jobs": "generate_cover_letter", "No matches": END}
)
```

### **Why LiteLLM?**

LiteLLM standardizes calls to 100+ LLMs, allowing seamless switching between providers with zero code changes—just update the model name.

**Switch models instantly:**

```python
# Option 1: Use Google Gemini (current default)
model = "gemini/gemini-2.5-flash"

# Option 2: Use LLAMA3 with Groq
model = "groq/llama3-70b-8192"

# Option 3: Use Claude
model = "anthropic/claude-3-5-sonnet-20241022"

# Same code for all models
response = completion(
    model=model,
    messages=messages,
    temperature=0.1
)
```

### **Why Batch Processing?**

**Problem**: Gemini 2.5 Flash has a 1M token context window. While large, sending 400 jobs at once risks:
- Exceeding token limits (400 jobs × 1000 tokens = 400k tokens + profile + prompt)
- Longer processing times and higher chance of timeout
- Difficulty debugging which jobs caused failures

**Solution**: Split jobs into batches of 50-100 jobs each
- Each batch: ~50k-100k tokens (safe margin)
- Parallel processing possible in future (batch independence)
- Failed batches don't affect others
- Clear progress tracking per batch

### **Cloudflare Bypass Strategy**

Upwork uses Cloudflare protection, which blocks standard Selenium. Our approach:

1. **selenium-stealth**: Patches WebDriver to remove automation signatures
2. **Custom user agent**: Mimics real browser behavior
3. **Smart delays**: 5-15 second waits for challenge completion
4. **Stealth settings**: Disables automation flags, fixes hairline rendering

```python
stealth(driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)
```

### **File Organization Philosophy**

**Old approach** (overwrite single files):
```
files/
├── upwork_job_listings.txt  ← Overwritten each run
├── matched_jobs.txt          ← Lost previous results
└── cover_letter.txt          ← Mixed runs, confusing
```

**New approach** (timestamped isolation):
```
files/
├── 2025-10-23_09.15.30/
│   ├── upwork_job_listings.txt
│   ├── matched_jobs.txt
│   └── cover_letter.txt
├── 2025-10-24_14.22.45/
│   ├── upwork_job_listings.txt
│   ├── matched_jobs.txt
│   └── cover_letter.txt
└── profile.md
```

**Benefits:**
- Complete audit trail of all runs
- Easy to compare results across days
- No accidental overwrites
- Can track match rate trends over time

## Configuration

All settings are configurable in `main.py`:

```python
num_jobs_per_page = 50  # Jobs to scrape per page
num_pages = 8           # Total pages (8 × 50 = 400 jobs)
batch_size = 100        # Jobs per classification batch
```

**Recommended configurations:**

| Scenario | Pages | Jobs | Batch Size | Time Est. |
|----------|-------|------|------------|-----------|
| Quick test | 2 | 100 | 50 | ~5 min |
| Daily scan | 5 | 250 | 100 | ~15 min |
| Deep search | 8 | 400 | 100 | ~25 min |
| Max coverage | 10 | 500 | 100 | ~35 min |

## Future Improvements

While the current system is production-ready, these enhancements could further improve results:

### Short-term
- **Enhanced profile**: Include 5-10 example cover letters in user's writing style
- **Retry logic**: Auto-retry failed batches with exponential backoff
- **Parallel batching**: Process multiple classification batches simultaneously
- **Filter customization**: Add configurable filters (budget range, job type, etc.)

### Medium-term
- **Auto-submission**: Direct API integration with Upwork (if available)
- **Performance metrics**: Track match rates, cover letter effectiveness over time
- **Template library**: Multiple cover letter styles (formal, casual, technical)
- **Job deduplication**: Skip jobs already seen in previous runs

### Long-term
- **Feedback loop**: Learn from accepted vs. rejected proposals (RLHF-style)
- **A/B testing**: Generate multiple cover letter variants, track which performs best
- **Multi-platform**: Extend to Freelancer.com, Fiverr, Toptal
- **Smart scheduling**: Auto-run at optimal times based on job posting patterns

## Installation & Setup

### Prerequisites

- **Python 3.9+** (tested with Python 3.13)
- **Chrome browser** (for Selenium WebDriver)
- **API Keys**:
  - Google Gemini API key (required) - [Get it here](https://ai.google.dev/)
  - Groq API key (optional, for Llama3) - [Get it here](https://console.groq.com/)
  - Tavily API key (optional, for research features) - [Get it here](https://tavily.com/)

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AIXerum/Upwork-Auto-Jobs-Applier-using-AI.git
   cd Upwork-Auto-Jobs-Applier-using-AI
   ```

2. **Create and activate a virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the root directory:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here  # Optional
   TAVILY_API_KEY=your_tavily_api_key   # Optional
   ```

   **Note**: `.env` is gitignored automatically to protect your secrets.

5. **Customize your profile:**

   Edit `files/profile.md` with your skills, experience, and writing style. This is crucial for accurate job matching and personalized cover letters.

   ```markdown
   # Your Name
   ## Skills
   - Node.js, PostgreSQL, Express.js
   - API Development & Integration
   ...
   ```

6. **Configure search parameters** (optional):

   Edit `main.py` to adjust scraping settings:

   ```python
   num_jobs_per_page = 50  # Jobs per page
   num_pages = 5           # Start with 5 pages for testing
   batch_size = 50         # Classification batch size
   ```

   You can also customize the Upwork search URL in `src/utils.py` (line ~45) to match your desired job filters.

### Running the Application

**Basic usage:**

```bash
python main.py
```

**Expected output:**

```
📁 Created run folder: files/2025-10-24_14.30.15

----- Scraping Upwork jobs -----
📄 Scraping 5 pages (50 jobs per page)

Scraping page 1...
Found 50 jobs on page 1
Scraping page 2...
Found 50 jobs on page 2
...

----- Scraped 250 jobs total from 5 pages -----

----- Classifying scraped jobs -----
📊 Total jobs to classify: 250
🔢 Batch size: 50 jobs per batch

⚙️  Classifying batch 1/5 (jobs 1-50 of 250)
✅ Found 8 matches in batch 1
...

🎯 Classification complete: 35 total matches from 250 jobs

----- Generating cover letters -----
...
```

**Output location:**

All results are saved in a timestamped folder:
```
files/2025-10-24_14.30.15/
├── upwork_job_listings.txt  # All 250 scraped jobs
├── matched_jobs.txt          # 35 matched jobs with reasons
└── cover_letter.txt          # 35 personalized cover letters
```

### Testing & Validation

**Test scraping only:**

```bash
python scrape_upwork_jobs.py
```

This runs the scraper independently to verify Cloudflare bypass is working.

**Start small:**

For your first run, use conservative settings to test:
```python
num_pages = 2      # Just 100 jobs
batch_size = 50    # Smaller batches
```

Once validated, scale up to 5-10 pages.

## Customization Guide

### 1. Personalize Your Profile

The `files/profile.md` file is the heart of the system. The AI uses this to:
- Filter relevant jobs
- Personalize cover letters
- Match your writing style

**Include:**
- Detailed skills list (languages, frameworks, tools)
- Years of experience in each area
- Notable projects or achievements
- Your writing tone/style
- 2-3 example cover letters you've written (optional but recommended)

### 2. Customize Job Search

Edit the search URL in `src/utils.py` (line ~45):

```python
url = f'https://www.upwork.com/nx/search/jobs/?q=YOUR_SEARCH_TERMS&...'
```

**Modify search parameters:**
- `q=`: Search keywords (e.g., `Node.js Backend`)
- `category2_uid=`: Category filter
- `hourly_rate=`: Budget range
- `t=`: Job type (0=hourly, 1=fixed)

### 3. Adjust AI Prompts

Edit `src/prompts.py` to customize:
- **Classification criteria** (`classify_jobs_prompt`): What makes a job a good match?
- **Cover letter style** (`generate_cover_letter_prompt`): Formal, casual, technical?
- **Example structure**: Add your own examples

### 4. Switch AI Models

In `src/graph.py` (line ~365):

```python
# Current: Google Gemini (recommended)
model="gemini/gemini-2.5-flash"

# Alternative: Llama 3 via Groq (faster, may need tuning)
model="groq/llama3-70b-8192"

# Alternative: Claude (requires Anthropic API key)
model="anthropic/claude-3-5-sonnet-20241022"
```

### 5. Rate Limiting

Adjust delays in `src/graph.py`:
- **Cover letter delay** (line ~260): `time.sleep(6)` → Change to desired seconds
- **Page scraping delay** in `src/utils.py`: Modify wait times between pages

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **No jobs found** | Cloudflare blocked scraper | Increase wait time in `utils.py` (line ~52): `time.sleep(15)` |
| **Classification fails** | Batch too large | Reduce `batch_size` in `main.py` to 50 |
| **API rate limit** | Too many requests | Increase delay in cover letter generation |
| **Import errors** | Missing dependencies | Run `pip install -r requirements.txt` |
| **Chrome not found** | WebDriver issue | Install Chrome browser or update `webdriver_manager` |
| **Empty matches** | Profile mismatch | Review and enhance `files/profile.md` with more details |

**Enable debug mode:**

If scraping fails, screenshots are saved as `debug_screenshot_pageX.png` in the root directory.

## Project Structure

```
Upwork-Auto-Jobs-Applier-using-AI/
├── main.py                      # Entry point, configuration
├── scrape_upwork_jobs.py       # Standalone scraper test
├── requirements.txt            # Python dependencies
├── .env                        # API keys (gitignored)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── files/
│   ├── profile.md              # Your freelancer profile
│   ├── 2025-10-23_09.15.30/   # Example run folder
│   │   ├── upwork_job_listings.txt
│   │   ├── matched_jobs.txt
│   │   └── cover_letter.txt
│   └── 2025-10-24_14.30.15/   # Another run folder
│       └── ...
└── src/
    ├── __init__.py
    ├── agent.py                # LiteLLM agent wrapper
    ├── graph.py                # LangGraph workflow
    ├── prompts.py              # AI prompts for classification & writing
    └── utils.py                # Scraping and file utilities
```

## Performance & Costs

### Time Estimates

| Pages | Jobs | Batches | Scraping | Classification | Cover Letters | Total |
|-------|------|---------|----------|----------------|---------------|-------|
| 2 | 100 | 2 | 2 min | 1 min | 2 min | ~5 min |
| 5 | 250 | 5 | 4 min | 2 min | 5 min | ~15 min |
| 8 | 400 | 4 | 6 min | 3 min | 10 min | ~25 min |
| 10 | 500 | 5 | 8 min | 4 min | 15 min | ~35 min |

*Assumes 15% match rate and 6-second delay between cover letters*

### API Costs (Gemini 2.5 Flash)

**Pricing**: $0.075 per 1M input tokens, $0.30 per 1M output tokens

| Operation | Input Tokens | Output Tokens | Cost per Call |
|-----------|-------------|---------------|---------------|
| Classify 100 jobs | ~55k | ~2k | $0.0047 |
| Generate cover letter | ~3k | ~500 | $0.0004 |

**Total cost example (400 jobs, 60 matches):**
- Classification: 4 batches × $0.0047 = $0.019
- Cover letters: 60 × $0.0004 = $0.024
- **Total: ~$0.043** (less than 5 cents per run!)

## Contributing

Contributions are welcome! Areas for improvement:
- Add support for other freelance platforms
- Implement parallel batch processing
- Create web UI for configuration
- Add job deduplication across runs
- Improve Cloudflare bypass reliability

## License

MIT License - feel free to use and modify for your freelance journey!

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration
- [LiteLLM](https://github.com/BerriAI/litellm) - Multi-model AI gateway
- [Selenium](https://www.selenium.dev/) + [selenium-stealth](https://github.com/diprajpatra/selenium-stealth) - Web scraping
- [Google Gemini](https://ai.google.dev/) - AI classification and generation

---

**Happy freelancing! May your proposals be many and your matches be plenty. 🚀✨**
