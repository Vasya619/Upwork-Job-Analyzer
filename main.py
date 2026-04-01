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
        num_jobs_per_page = 50  # Jobs per page
        num_pages = 8           # Number of pages to scrape (8 pages = 400 jobs)
        batch_size = 100         # Jobs to classify at once (50-100 keeps requests manageable)

        # run automation graph
        bot = UpworkAutomationGraph(
            profile=profile,
            num_jobs=num_jobs_per_page,
            num_pages=num_pages,
            batch_size=batch_size
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