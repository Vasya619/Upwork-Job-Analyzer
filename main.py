from dotenv import load_dotenv
from src.utils import read_text_file
from src.graph import UpworkAutomationGraph
import signal
import sys
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Load environment variables from a .env file
load_dotenv()

# Load environment variables from a .env file
load_dotenv()

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    print(Fore.YELLOW + "\n\n⚠️  Received interrupt signal (CTRL+C)")
    print(Fore.CYAN + "🛑 Shutting down gracefully...")
    print(Fore.GREEN + "✅ Process stopped. Any completed work has been saved.\n" + Style.RESET_ALL)
    sys.exit(0)

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # load the freelancer profile
        profile = read_text_file("./files/profile.md")

        # Configuration
        num_jobs_per_page = 50  # Jobs per page (50 max typically)
        num_pages = 5           # Number of pages to scrape (5 pages = 250 jobs)
        batch_size = 10         # Jobs to classify at once (small for local models with limited context)

        # The upwork search url
        upwork_url = f'https://www.upwork.com/nx/search/jobs/?q=%28Node%20OR%20Node.js%20OR%20PostgreSQL%20OR%20Postgres%20OR%20Handlebars%20OR%20Backend%20OR%20API%20OR%20integration%20OR%20Back-end%20OR%20React%29%20AND%20NOT%20%28Django%20OR%20jQuery%20OR%20Next%20OR%20Next.js%20OR%20NestJS%20OR%20Nest.js%20OR%20Nest%20OR%20Redis%20OR%20MongoDB%20OR%20Wordpress%20OR%20PHP%20OR%20Python%20OR%20C%23%20OR%20n8n%20OR%20designer%20OR%20mobile%20OR%20zapier%20OR%20make%20OR%20make.com%20OR%20angular%29&page=1&per_page={num_jobs_per_page}&page={num_pages}'

        # run automation graph
        bot = UpworkAutomationGraph(
            profile=profile,
            num_jobs=num_jobs_per_page,
            num_pages=num_pages,
            batch_size=batch_size,
            upwork_url=upwork_url
        )
        bot.run()
        
    except KeyboardInterrupt:
        # This should be caught by the signal handler, but just in case
        print(Fore.YELLOW + "\n\n⚠️  Process interrupted by user")
        print(Fore.GREEN + "✅ Shutdown complete.\n" + Style.RESET_ALL)
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n❌ An unexpected error occurred: {str(e)}")
        print(Fore.YELLOW + "💡 Check your configuration and try again.\n" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()