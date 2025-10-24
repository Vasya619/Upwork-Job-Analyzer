import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

def read_text_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        # Strip newline characters and any surrounding whitespace
        lines = [line.strip() for line in lines if line.strip()]
        return "".join(lines)

def scrape_upwork_data(number_of_jobs, pages):
    # Setup Chrome WebDriver with stealth options
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Apply stealth settings to bypass Cloudflare
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    job_listings = []

    try:
        # Scrape from multiple pages
        for page_num in pages:
            print(f"Scraping page {page_num}...")
            # Open Upwork job search page
            url = f'https://www.upwork.com/nx/search/jobs/?nbs=1&page={page_num}&per_page={number_of_jobs}&q=%28Node%20OR%20Node.js%20OR%20PostgreSQL%20OR%20Postgres%20OR%20Handlebars%20OR%20Backend%20OR%20Fix%20OR%20API%20OR%20integration%20OR%20Back-end%29%20AND%20NOT%20%28React%20OR%20Django%20OR%20jQuery%20OR%20Next%20OR%20Next.js%20OR%20NestJS%20OR%20Nest.js%20OR%20Nest%20OR%20Redis%20OR%20MongoDB%20OR%20Wordpress%20OR%20PHP%20OR%20Python%20OR%20C%23%20OR%20n8n%20OR%20designer%20OR%20mobile%29'
            driver.get(url)

            # Wait for page to load and Cloudflare check
            time.sleep(5)
            
            # Check if Cloudflare challenge is present
            page_source = driver.page_source
            if "challenges.cloudflare.com" in page_source or "Just a moment" in page_source:
                print("Cloudflare challenge detected, waiting longer...")
                time.sleep(10)  # Additional wait

            # Find job listings
            jobs = driver.find_elements(By.CSS_SELECTOR, 'article[data-test="JobTile"]')
            
            if len(jobs) == 0:
                print(f"No jobs found on page {page_num}. Page title: {driver.title}")
                print(f"Current URL: {driver.current_url}")
                # Save screenshot for debugging
                try:
                    driver.save_screenshot(f'debug_screenshot_page{page_num}.png')
                    print(f"Screenshot saved as debug_screenshot_page{page_num}.png")
                except:
                    pass
                continue  # Skip to next page

            print(f"Found {len(jobs)} jobs on page {page_num}")
            
            # Extract and collect job details
            for job in jobs:
                try:
                    title_element = job.find_element(By.CSS_SELECTOR, 'h2.job-tile-title > a')
                    title = title_element.text.strip()
                    link = title_element.get_attribute('href')
                    description = job.find_element(By.CSS_SELECTOR, 'div[data-test="JobTileDetails"] > div > div > p').text.strip()
                    
                    job_info = job.find_element(By.CSS_SELECTOR, 'ul.job-tile-info-list')
                    job_type = job_info.find_element(By.CSS_SELECTOR, 'li[data-test="job-type-label"]').text.strip()
                    experience_level = job_info.find_element(By.CSS_SELECTOR, 'li[data-test="experience-level"]').text.strip()

                    # Check for budget (fixed price or hourly)
                    try:
                        budget = job_info.find_element(By.CSS_SELECTOR, 'li[data-test="is-fixed-price"]').text.strip()
                    except:
                        budget = job_info.find_element(By.CSS_SELECTOR, 'li[data-test="duration-label"]').text.strip()

                    job_listings.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'job_type': job_type,
                        'experience_level': experience_level,
                        'budget': budget
                    })
                except Exception as e:
                    print(f'Error parsing job listing on page {page_num}: {e}')
                    continue
            
            # Brief pause between pages
            if page_num < pages[-1]:
                print(f"Waiting before next page...")
                time.sleep(5)

    finally:
        # Close the browser
        driver.quit()

    return job_listings

def save_jobs_to_file(job_listings, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for job in job_listings:
            file.write(f"Title: {job['title']}\n")
            file.write(f"Link: {job['link']}\n")
            file.write(f"Description: {job['description']}\n")
            file.write(f"Job Type: {job['job_type']}\n")
            file.write(f"Experience Level: {job['experience_level']}\n")
            file.write(f"Budget: {job['budget']}\n")
            file.write("\n---\n\n")