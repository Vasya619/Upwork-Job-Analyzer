import json
import os
from datetime import datetime
from typing import List
from colorama import Fore, Style
from .agent import Agent
from .utils import scrape_upwork_data, save_jobs_to_file
from .prompts import classify_jobs_prompt, generate_cover_letter_prompt

# Default model served by LM Studio (uses whatever model is loaded)
LM_STUDIO_MODEL = os.environ.get("LM_STUDIO_MODEL", "local-model")


class UpworkAutomationGraph:
    def __init__(self, profile, num_jobs=50, num_pages=5, batch_size=10, upwork_url='https://www.upwork.com/nx/search/jobs/'):
        # Freelancer profile/resume
        self.profile = profile

        # Number of jobs per page
        self.number_of_jobs = num_jobs
        
        # Number of pages to scrape
        self.num_pages = num_pages
        
        # Batch size for classification (how many jobs to send to AI at once)
        self.batch_size = batch_size

        # Upwork search url
        self.upwork_url = upwork_url

        # Create timestamped folder for this run
        self.run_folder = self.create_run_folder()

        # Build agents
        self.init_agents()

    def create_run_folder(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        folder_path = os.path.join("files", timestamp)
        os.makedirs(folder_path, exist_ok=True)
        print(Fore.CYAN + f"📁 Created run folder: {folder_path}\n" + Style.RESET_ALL)
        return folder_path

    def get_file_path(self, filename):
        return os.path.join(self.run_folder, filename)

    def scrape_upwork_jobs(self):
        print(Fore.YELLOW + "----- Scraping Upwork jobs -----\n" + Style.RESET_ALL)
        pages = list(range(1, self.num_pages + 1))
        print(Fore.CYAN + f"📄 Scraping {self.num_pages} pages ({self.number_of_jobs} jobs per page)\n" + Style.RESET_ALL)
        
        job_listings = scrape_upwork_data(self.upwork_url, self.number_of_jobs, pages)

        print(Fore.GREEN + f"----- Scraped {len(job_listings)} jobs total from {len(pages)} pages -----\n" + Style.RESET_ALL)
        save_jobs_to_file(job_listings, self.get_file_path("upwork_job_listings.txt"))
        return job_listings

    def classify_scraped_jobs(self, all_jobs):
        print(Fore.YELLOW + "----- Classifying scraped jobs -----\n" + Style.RESET_ALL)
        
        if not all_jobs:
            print(Fore.RED + "No jobs to classify\n" + Style.RESET_ALL)
            return []
        
        total_jobs = len(all_jobs)
        print(Fore.CYAN + f"📊 Total jobs to classify: {total_jobs}\n" + Style.RESET_ALL)
        print(Fore.CYAN + f"🔢 Batch size: {self.batch_size} jobs per batch\n" + Style.RESET_ALL)
        
        all_matches = []
        num_batches = (total_jobs + self.batch_size - 1) // self.batch_size
        
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
            
            batch_str = json.dumps(batch, ensure_ascii=False, indent=2)
            
            try:
                classify_result = self.classify_jobs_agent.invoke(batch_str)
            except Exception as e:
                print(Fore.RED + f"❌ Failed to classify batch {batch_idx + 1}: {str(e)}")
                print(Fore.YELLOW + "⏭️  Halting classification for remaining batches...\n" + Style.RESET_ALL)
                break
            
            if not classify_result or classify_result.strip() == "":
                print(Fore.RED + f"Classifier returned empty response for batch {batch_idx + 1}\n" + Style.RESET_ALL)
                continue
            
            # Clean markdown code blocks if present
            classify_result = classify_result.strip()
            if classify_result.startswith("```json"):
                classify_result = classify_result[7:]
            if classify_result.startswith("```"):
                classify_result = classify_result[3:]
            if classify_result.endswith("```"):
                classify_result = classify_result[:-3]
            classify_result = classify_result.strip()
            
            try:
                batch_matches = json.loads(classify_result, strict=False)["matches"]
                print(Fore.GREEN + f"✅ Found {len(batch_matches)} matches in batch {batch_idx + 1}\n" + Style.RESET_ALL)
                all_matches.extend(batch_matches)
            except (json.JSONDecodeError, KeyError) as e:
                print(Fore.RED + f"Failed to parse classification result for batch {batch_idx + 1}: {e}\n" + Style.RESET_ALL)
                print(Fore.RED + f"Raw response: {classify_result[:500]}\n" + Style.RESET_ALL)
                continue
        
        print(
            Fore.GREEN + Style.BRIGHT
            + f"🎯 Classification complete: {len(all_matches)} total matches from {total_jobs} jobs\n"
            + Style.RESET_ALL
        )
        
        if all_matches:
            self.save_matched_jobs(all_matches, self.run_folder)
            self.write_cover_letter_batch_header(len(all_matches), self.run_folder)
        else:
            print(Fore.YELLOW + "No matching jobs found\n" + Style.RESET_ALL)
        
        return all_matches

    def generate_cover_letters(self, matches):
        if not matches:
            print(Fore.RED + "No job matches\n" + Style.RESET_ALL)
            return
        
        print(Fore.GREEN + f"There are {len(matches)} job matches to process\n" + Style.RESET_ALL)
        
        for idx, match in enumerate(matches):
            print(Fore.YELLOW + f"----- Generating cover letter {idx + 1}/{len(matches)} -----\n" + Style.RESET_ALL)
            
            job_description = str(match.get("job", match))
            
            try:
                cover_letter_result = self.generate_cover_letter_agent.invoke(job_description)
            except Exception as e:
                print(Fore.RED + f"❌ Failed to generate cover letter for match #{idx + 1}: {str(e)}")
                print(Fore.YELLOW + "⏭️  Using error placeholder and continuing...\n" + Style.RESET_ALL)
                cover_letter_result = '{"letter": "[Error: Failed to generate cover letter.]"}'
            
            # Clean markdown code blocks
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
                cover_letter = f"[Error generating cover letter for: {job_description[:100]}...]"
            
            self.save_cover_letter(match, idx, cover_letter)

    def save_cover_letter(self, match, index, cover_letter):
        print(Fore.YELLOW + "----- Saving cover letter -----\n" + Style.RESET_ALL)
        cover_letters_file = os.path.join(self.run_folder, "cover_letter.txt")

        with open(cover_letters_file, "a", encoding="utf-8") as file:
            job_data = match.get("job") if isinstance(match, dict) else match
            
            if isinstance(job_data, str):
                try:
                    job_data = json.loads(job_data)
                except json.JSONDecodeError:
                    job_data = None
            
            file.write(f"\n{'='*70}\n")
            file.write(f"MATCH #{index + 1}\n")
            file.write(f"{'='*70}\n")
            
            if isinstance(job_data, dict):
                file.write(f"📌 Title: {job_data.get('title', 'N/A')}\n")
                file.write(f"🔗 Link: {job_data.get('link', 'N/A')}\n")
            
            file.write(f"{'-'*70}\n\n")
            file.write(cover_letter + f'\n\n{"-"*70}\n')

    def write_cover_letter_batch_header(self, num_matches, run_folder):
        cover_letters_file = os.path.join(run_folder, "cover_letter.txt")
        with open(cover_letters_file, "a", encoding="utf-8") as file:
            file.write(f"\n{'='*70}\n")
            file.write(f"COVER LETTERS BATCH - Generating {num_matches} cover letters\n")
            file.write(f"{'='*70}\n\n")

    def save_matched_jobs(self, matches, run_folder):
        matched_jobs_file = os.path.join(run_folder, "matched_jobs.txt")
        
        with open(matched_jobs_file, "a", encoding="utf-8") as file:
            file.write(f"\n{'='*70}\n")
            file.write(f"MATCHED JOBS - Found {len(matches)} matches\n")
            file.write(f"{'='*70}\n\n")
            
            for idx, match in enumerate(matches, 1):
                file.write(f"MATCH #{idx}\n")
                file.write(f"{'-'*70}\n\n")
                
                job_data = match.get('job', {})
                
                if isinstance(job_data, str):
                    try:
                        job_data = json.loads(job_data)
                    except json.JSONDecodeError:
                        file.write(f"Job Info:\n{job_data}\n\n")
                        file.write(f"✅ Match Reason:\n{match.get('reason', 'N/A')}\n")
                        file.write(f"{'='*70}\n\n")
                        continue
                
                if isinstance(job_data, dict):
                    file.write(f"📌 Title:\n   {job_data.get('title', 'N/A')}\n\n")
                    file.write(f"🔗 Link:\n   {job_data.get('link', 'N/A')}\n\n")
                    file.write(f"💼 Job Type: {job_data.get('job_type', 'N/A')}\n")
                    file.write(f"⭐ Experience Level: {job_data.get('experience_level', 'N/A')}\n")
                    file.write(f"💰 Budget: {job_data.get('budget', 'N/A')}\n\n")
                    
                    description = job_data.get('description', 'N/A')
                    if len(description) > 500:
                        description = description[:500] + "..."
                    file.write(f"📝 Description:\n{description}\n\n")
                else:
                    file.write(f"Job Info:\n{job_data}\n\n")
                
                file.write(f"✅ Match Reason:\n{match.get('reason', 'N/A')}\n")
                file.write(f"{'='*70}\n\n")

    def init_agents(self):
        self.classify_jobs_agent = Agent(
            name="Job Classifier Agent",
            model=LM_STUDIO_MODEL,
            system_prompt=classify_jobs_prompt.format(profile=self.profile),
            temperature=0.1,
            enable_thinking=False,  # Disable thinking — classification doesn't benefit from it
        )
        self.generate_cover_letter_agent = Agent(
            name="Writer Agent",
            model=LM_STUDIO_MODEL,
            system_prompt=generate_cover_letter_prompt.format(profile=self.profile),
            temperature=0.6,
            enable_thinking=True,
        )

    def run(self):
        print(Fore.BLUE + "----- Running Upwork Jobs Automation -----\n" + Style.RESET_ALL)
        try:
            job_listings = self.scrape_upwork_jobs()
            matches = self.classify_scraped_jobs(job_listings)
            self.generate_cover_letters(matches)
            print(Fore.BLUE + "----- Automation complete -----\n" + Style.RESET_ALL)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n⚠️  Process interrupted during execution")
            print(Fore.CYAN + "💾 Saving any completed work...")
            print(Fore.GREEN + "✅ Partial results saved. You can resume later.\n" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"❌ Unexpected error during execution: {str(e)}" + Style.RESET_ALL)
