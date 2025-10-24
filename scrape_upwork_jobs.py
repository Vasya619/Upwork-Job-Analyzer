from src.utils import scrape_upwork_data, save_jobs_to_file

if __name__ == "__main__":
    number_of_jobs = 50
    pages = [1, 2]
    job_listings = scrape_upwork_data(number_of_jobs, pages)
    save_jobs_to_file(job_listings, 'files/upwork_job_listings.txt')
    print(job_listings)
