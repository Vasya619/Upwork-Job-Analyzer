import json
import os
import time
from datetime import datetime
from langgraph.graph import END, StateGraph
from langgraph.errors import GraphRecursionError
from typing_extensions import TypedDict
from typing import List
from colorama import Fore, Style
from .agent import Agent
from .utils import scrape_upwork_data, save_jobs_to_file
from .prompts import classify_jobs_prompt, generate_cover_letter_prompt


### Our graph state
class GraphState(TypedDict):
    scraped_jobs_list: str
    matches: List[dict]
    job_description: str
    cover_letter: str
    num_matches: int
    run_folder: str  # Path to the current run's folder


class UpworkAutomationGraph:
    def __init__(self, profile, num_jobs=50, num_pages=5, batch_size=50):
        # Freelancer profile/resume
        self.profile = profile

        # Number of jobs per page
        self.number_of_jobs = num_jobs
        
        # Number of pages to scrape
        self.num_pages = num_pages
        
        # Batch size for classification (how many jobs to send to AI at once)
        self.batch_size = batch_size

        # Create timestamped folder for this run
        self.run_folder = self.create_run_folder()

        # Build agents
        self.init_agents()

        # Build graph
        self.graph = self.build_graph()

    def create_run_folder(self):
        """
        Create a timestamped folder for this run's output files.
        
        @return: Path to the created folder
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        folder_path = os.path.join("files", timestamp)
        
        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        
        print(Fore.CYAN + f"📁 Created run folder: {folder_path}\n" + Style.RESET_ALL)
        return folder_path

    def get_file_path(self, filename):
        """
        Get the full path for a file in the current run folder.
        
        @param filename: Name of the file
        @return: Full path to the file
        """
        return os.path.join(self.run_folder, filename)

    def scrape_upwork_jobs(self, state):
        """
        Scrape Upwork jobs from multiple pages.
        """

        print(
            Fore.YELLOW
            + f"----- Scraping Upwork jobs -----\n"
            + Style.RESET_ALL
        )
        # Generate page list dynamically based on num_pages
        pages = list(range(1, self.num_pages + 1))
        print(
            Fore.CYAN
            + f"📄 Scraping {self.num_pages} pages ({self.number_of_jobs} jobs per page)\n"
            + Style.RESET_ALL
        )
        
        # Scrape all pages in one go
        job_listings = scrape_upwork_data(self.number_of_jobs, pages)

        print(
            Fore.GREEN
            + f"----- Scraped {len(job_listings)} jobs total from {len(pages)} pages -----\n"
            + Style.RESET_ALL
        )
        # write scraped jobs to txt file in the run folder
        scraped_jobs_file = self.get_file_path("upwork_job_listings.txt")
        save_jobs_to_file(job_listings, scraped_jobs_file)
        job_listings_str = json.dumps(job_listings, ensure_ascii=False, indent=2)
        return {**state, "scraped_jobs_list": job_listings_str, "run_folder": self.run_folder}

    def classify_scraped_jobs(self, state):
        """
        Classify scraped jobs based on the profile.
        Uses batching to handle large job lists that exceed AI context limits.

        @param state: The current state of the application.
        @return: Updated state with classified jobs.
        """
        print(Fore.YELLOW + "----- Classifying scraped jobs -----\n" + Style.RESET_ALL)
        scraped_jobs_str = state["scraped_jobs_list"]
        
        # Handle empty job lists
        if not scraped_jobs_str or scraped_jobs_str.strip() == "":
            print(Fore.RED + "No jobs to classify\n" + Style.RESET_ALL)
            return {**state, "matches": []}
        
        # Parse the full job list
        try:
            all_jobs = json.loads(scraped_jobs_str)
        except json.JSONDecodeError as e:
            print(Fore.RED + f"Failed to parse scraped jobs: {e}\n" + Style.RESET_ALL)
            return {**state, "matches": []}
        
        total_jobs = len(all_jobs)
        print(Fore.CYAN + f"📊 Total jobs to classify: {total_jobs}\n" + Style.RESET_ALL)
        print(Fore.CYAN + f"🔢 Batch size: {self.batch_size} jobs per batch\n" + Style.RESET_ALL)
        
        # Split jobs into batches
        all_matches = []
        num_batches = (total_jobs + self.batch_size - 1) // self.batch_size  # Ceiling division
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_jobs)
            batch = all_jobs[start_idx:end_idx]
            
            print(
                Fore.YELLOW
                + f"⚙️  Classifying batch {batch_idx + 1}/{num_batches} "
                + f"(jobs {start_idx + 1}-{end_idx} of {total_jobs})\n"
                + Style.RESET_ALL
            )
            
            # Convert batch to JSON string for the AI
            batch_str = json.dumps(batch, ensure_ascii=False, indent=2)
            
            # Invoke classifier on this batch
            classify_result = self.classify_jobs_agent.invoke(batch_str)
            
            # Handle empty or invalid responses
            if not classify_result or classify_result.strip() == "":
                print(Fore.RED + f"Classifier returned empty response for batch {batch_idx + 1}\n" + Style.RESET_ALL)
                continue
            
            # Clean the response - remove markdown code blocks if present
            classify_result = classify_result.strip()
            if classify_result.startswith("```json"):
                classify_result = classify_result[7:]  # Remove ```json
            if classify_result.startswith("```"):
                classify_result = classify_result[3:]  # Remove ```
            if classify_result.endswith("```"):
                classify_result = classify_result[:-3]  # Remove trailing ```
            classify_result = classify_result.strip()
            
            try:
                batch_matches = json.loads(classify_result, strict=False)["matches"]
                print(Fore.GREEN + f"✅ Found {len(batch_matches)} matches in batch {batch_idx + 1}\n" + Style.RESET_ALL)
                all_matches.extend(batch_matches)
            except (json.JSONDecodeError, KeyError) as e:
                print(Fore.RED + f"Failed to parse classification result for batch {batch_idx + 1}: {e}\n" + Style.RESET_ALL)
                print(Fore.RED + f"Raw response: {classify_result[:500]}\n" + Style.RESET_ALL)
                continue
        
        # Summary
        print(
            Fore.GREEN + Style.BRIGHT
            + f"🎯 Classification complete: {len(all_matches)} total matches from {total_jobs} jobs\n"
            + Style.RESET_ALL
        )
        
        # Save matched jobs to file
        if all_matches:
            self.save_matched_jobs(all_matches, state["run_folder"])
            # Add batch header to cover letters file
            self.write_cover_letter_batch_header(len(all_matches), state["run_folder"])
        else:
            print(Fore.YELLOW + "No matching jobs found\n" + Style.RESET_ALL)
        
        return {**state, "matches": all_matches}

    def check_for_job_matches(self, state):
        print(
            Fore.YELLOW
            + "----- Checking for remaining job matches -----\n"
            + Style.RESET_ALL
        )
        if len(state["matches"]) == 0:
            return {**state, "num_matches": 0}
        else:
            return {**state, "num_matches": len(state["matches"])}

    def need_to_process_matches(self, state):
        """
        Check if there are any job matches.

        @param state: The current state of the application.
        @return: "No matches" if no job matches, otherwise "Process jobs".
        """
        if len(state["matches"]) == 0:
            print(Fore.RED + "No job matches\n" + Style.RESET_ALL)
            return "No matches"
        else:
            print(
                Fore.GREEN
                + f"There are {len(state['matches'])} Job matches to process\n"
                + Style.RESET_ALL
            )
            return "Process jobs"

    def generate_cover_letter(self, state):
        """
        Generate cover letter based on the job description and the profile.

        @param state: The current state of the application.
        @return: Updated state with generated cover letter.
        """
        print(Fore.YELLOW + "----- Generating cover letter -----\n" + Style.RESET_ALL)
        matches = state["matches"]
        # Use the last match (LIFO) for processing
        current_index = len(matches) - 1
        current_match = matches[current_index]
        # Pass both the job description and the match metadata to the writer agent
        job_description = str(current_match.get("job", current_match))
        # Store current match metadata in state so save_cover_letter can reference it
        state = {**state, "current_match_index": current_index, "current_match": current_match}

        cover_letter_result = self.generate_cover_letter_agent.invoke(job_description)
        
        # Clean the response - remove markdown code blocks if present
        cover_letter_result = cover_letter_result.strip()
        if cover_letter_result.startswith("```json"):
            cover_letter_result = cover_letter_result[7:]
        if cover_letter_result.startswith("```"):
            cover_letter_result = cover_letter_result[3:]
        if cover_letter_result.endswith("```"):
            cover_letter_result = cover_letter_result[:-3]
        cover_letter_result = cover_letter_result.strip()
        
        try:
            cover_letter = json.loads(cover_letter_result, strict=False)["letter"]
        except (json.JSONDecodeError, KeyError) as e:
            print(Fore.RED + f"Failed to parse cover letter result: {e}\n" + Style.RESET_ALL)
            print(Fore.RED + f"Raw response: {cover_letter_result[:500]}\n" + Style.RESET_ALL)
            # Use a default cover letter or skip
            cover_letter = f"[Error generating cover letter for: {job_description[:100]}...]"

        # Respect a short pause between generating cover letters to avoid rate limits
        # and to space out API calls / downstream processing.
        time.sleep(6)

        return {
            **state,
            "cover_letter": cover_letter,
            "job_description": job_description,
        }

    def save_cover_letter(self, state):
        """
        Save the generated cover letter to a file.

        @param state: The current state of the application.
        @return: The updated state after saving the cover letter.
        """
        print(Fore.YELLOW + "----- Saving cover letter -----\n" + Style.RESET_ALL)

        current_match = state.get("current_match")
        current_index = state.get("current_match_index")
        
        cover_letters_file = os.path.join(state["run_folder"], "cover_letter.txt")

        with open(cover_letters_file, "a", encoding="utf-8") as file:
            # Write match metadata if available
            if current_match is not None and current_index is not None:
                # Extract job data
                job_data = current_match.get("job") if isinstance(current_match, dict) else current_match
                
                # If job_data is a string, try to parse it as JSON
                if isinstance(job_data, str):
                    try:
                        job_data = json.loads(job_data)
                    except json.JSONDecodeError:
                        job_data = None
                
                # Write match number and job details
                file.write(f"\n{'='*70}\n")
                file.write(f"MATCH #{current_index + 1}\n")
                file.write(f"{'='*70}\n")
                
                if isinstance(job_data, dict):
                    title = job_data.get("title", "N/A")
                    link = job_data.get("link", "N/A")
                    file.write(f"📌 Title: {title}\n")
                    file.write(f"🔗 Link: {link}\n")
                
                file.write(f"{'-'*70}\n\n")

            file.write(state["cover_letter"] + f'\n\n{"-"*70}\n')

        # Remove already processed job and clear current match metadata
        if "matches" in state and len(state["matches"]) > 0:
            state["matches"].pop()
        state.pop("current_match", None)
        state.pop("current_match_index", None)
        return {**state, "matches": state.get("matches", [])}

    def write_cover_letter_batch_header(self, num_matches, run_folder):
        """
        Write a batch header to the cover letters file when a new classification run starts.

        @param num_matches: Number of jobs matched in this batch.
        @param run_folder: Path to the current run folder.
        """
        cover_letters_file = os.path.join(run_folder, "cover_letter.txt")
        
        with open(cover_letters_file, "a", encoding="utf-8") as file:
            file.write(f"\n{'='*70}\n")
            file.write(f"COVER LETTERS BATCH - Generating {num_matches} cover letters\n")
            file.write(f"{'='*70}\n\n")

    def save_matched_jobs(self, matches, run_folder):
        """
        Save the matched/classified jobs to a file.

        @param matches: List of matched job dictionaries with 'job' and 'reason' keys.
        @param run_folder: Path to the current run folder.
        """
        matched_jobs_file = os.path.join(run_folder, "matched_jobs.txt")
        
        with open(matched_jobs_file, "a", encoding="utf-8") as file:
            # Add matched jobs count header for this batch
            file.write(f"\n{'='*70}\n")
            file.write(f"MATCHED JOBS - Found {len(matches)} matches\n")
            file.write(f"{'='*70}\n\n")
            
            for idx, match in enumerate(matches, 1):
                file.write(f"MATCH #{idx}\n")
                file.write(f"{'-'*70}\n\n")
                
                # Get job data - it's already a dict from the AI classifier
                job_data = match.get('job', {})
                
                # If job_data is a string, try to parse it
                if isinstance(job_data, str):
                    try:
                        job_data = json.loads(job_data)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, treat it as plain text
                        file.write(f"Job Info:\n{job_data}\n\n")
                        file.write(f"✅ Match Reason:\n{match.get('reason', 'N/A')}\n")
                        file.write(f"{'='*70}\n\n")
                        continue
                
                # Format job details nicely
                if isinstance(job_data, dict):
                    file.write(f"📌 Title:\n   {job_data.get('title', 'N/A')}\n\n")
                    file.write(f"🔗 Link:\n   {job_data.get('link', 'N/A')}\n\n")
                    file.write(f"💼 Job Type: {job_data.get('job_type', 'N/A')}\n")
                    file.write(f"⭐ Experience Level: {job_data.get('experience_level', 'N/A')}\n")
                    file.write(f"💰 Budget: {job_data.get('budget', 'N/A')}\n\n")
                    
                    # Truncate long descriptions for readability
                    description = job_data.get('description', 'N/A')
                    if len(description) > 500:
                        description = description[:500] + "..."
                    file.write(f"📝 Description:\n{description}\n\n")
                else:
                    file.write(f"Job Info:\n{job_data}\n\n")
                
                file.write(f"✅ Match Reason:\n{match.get('reason', 'N/A')}\n")
                file.write(f"{'='*70}\n\n")

    def init_agents(self):
        """
        Initialize agents for scraping jobs, classifying jobs, and generating cover letters.
        """
        # Using Gemini model for its longer context length
        # llama3 with Groq will hit the TPM limit and throw an error
        self.classify_jobs_agent = Agent(
            name="Job Classifier Agent",
            model="gemini/gemini-2.5-flash",
            system_prompt=classify_jobs_prompt.format(profile=self.profile),
            temperature=0.1,
        )
        self.generate_cover_letter_agent = Agent(
            name="Writer Agent",
            # model="groq/llama-3.1-70b-versatile",
            model="gemini/gemini-2.5-flash",
            system_prompt=generate_cover_letter_prompt.format(profile=self.profile),
            temperature=0.1
        )

    def build_graph(self):
        graph = StateGraph(GraphState)

        # create all required nodes
        graph.add_node("scrape_upwork_jobs", self.scrape_upwork_jobs)
        graph.add_node("classify_scraped_jobs", self.classify_scraped_jobs)
        graph.add_node("check_for_job_matches", self.check_for_job_matches)
        graph.add_node("generate_cover_letter", self.generate_cover_letter)
        graph.add_node("save_cover_letter", self.save_cover_letter)

        # Link nodes to complete workflow
        graph.set_entry_point("scrape_upwork_jobs")
        graph.add_edge("scrape_upwork_jobs", "classify_scraped_jobs")
        graph.add_edge("classify_scraped_jobs", "check_for_job_matches")
        graph.add_conditional_edges(
            "check_for_job_matches",
            self.need_to_process_matches,
            {"Process jobs": "generate_cover_letter", "No matches": END},
        )
        graph.add_edge("generate_cover_letter", "save_cover_letter")
        graph.add_edge("save_cover_letter", "check_for_job_matches")

        return graph.compile()

    def run(self):
        print(
            Fore.BLUE + "----- Running Upwork Jobs Automation -----\n" + Style.RESET_ALL
        )
        try:
            # Increase recursion limit to handle processing multiple jobs
            # Each job requires ~3 iterations (check -> generate -> save)
            state = self.graph.invoke(
                {},  # Empty initial state
                config={"recursion_limit": 200}  # Allow up to ~66 jobs to be processed
            )
        except GraphRecursionError as e:
            print(Fore.RED +
                f"Graph recursion limit reached: {e}\n"
                "Consider increasing the recursion limit or reducing the number of jobs to process.\n"
                + Style.RESET_ALL
            )
            state = {}
        return state
