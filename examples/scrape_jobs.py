# ==================== examples/scrape_jobs.py ====================

"""
Example script for scraping LinkedIn jobs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.crawler import LinkedInCrawler
from src.config import Config
from src.utils import setup_logging, print_banner
import json


def scrape_jobs_example():
    """Example: Search and scrape multiple jobs"""
    
    print_banner()
    setup_logging()
    
    # Initialize crawler
    config = Config()
    crawler = LinkedInCrawler(config)
    
    try:
        # Login (optional)
        # crawler.login()
        
        # Define search parameters
        search_queries = [
            {'keywords': 'Python Developer', 'location': 'United States', 'max': 5},
            {'keywords': 'Data Scientist', 'location': 'Remote', 'max': 5},
            {'keywords': 'Machine Learning Engineer', 'location': 'California', 'max': 5}
        ]
        
        all_jobs = []
        
        for query in search_queries:
            print(f"\n{'='*60}")
            print(f"Searching: {query['keywords']} in {query['location']}")
            print('='*60)
            
            # Search for jobs
            job_urls = crawler.search_jobs(
                query['keywords'],
                query['location'],
                query['max']
            )
            
            print(f"Found {len(job_urls)} jobs")
            
            # Scrape each job
            for i, url in enumerate(job_urls, 1):
                print(f"\n[{i}/{len(job_urls)}] Scraping job...")
                job_data = crawler.scrape_job(url)
                
                if job_data:
                    all_jobs.append(job_data)
                    print(f"✅ {job_data.get('title')} at {job_data.get('company')}")
                else:
                    print("❌ Failed to scrape")
        
        # Save all jobs to JSON
        output_file = 'scraped_jobs.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Scraped {len(all_jobs)} jobs")
        print(f"📁 Data saved to {output_file}")
        
        # Display cache stats
        stats = crawler.get_cache_stats()
        print(f"\n📊 Cache Stats:")
        print(f"   Total jobs cached: {stats['total_jobs']}")
        print(f"   Database size: {stats['database_size_mb']} MB")
        
    finally:
        crawler.close()


if __name__ == "__main__":
    scrape_jobs_example()


