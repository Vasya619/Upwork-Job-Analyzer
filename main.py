from dotenv import load_dotenv
from src.utils import read_text_file
from src.graph import UpworkAutomationGraph

# Load environment variables from a .env file
load_dotenv()

if __name__ == "__main__":

    # load the freelancer profile
    profile = read_text_file("./files/profile.md")

    # Configuration
    num_jobs_per_page = 50  # Jobs per page
    num_pages = 8           # Number of pages to scrape (8 pages = 400 jobs)
    batch_size = 100         # Jobs to classify at once (50-100 is safe for Gemini)

    # run automation graph
    bot = UpworkAutomationGraph(
        profile=profile,
        num_jobs=num_jobs_per_page,
        num_pages=num_pages,
        batch_size=batch_size
    )
    bot.run()