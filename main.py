"""
Main script and example usage files
"""

# ==================== main.py ====================

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.crawler import LinkedInCrawler
from src.config import Config
from src.utils import setup_logging, print_banner


def main():
    """Main execution function"""
    
    # Print banner
    print_banner()
    
    # Setup logging
    config = Config()
    setup_logging(config.LOG_LEVEL, config.LOG_FILE)
    
    # Initialize crawler
    print("\n🚀 Initializing LinkedIn Crawler...")
    crawler = LinkedInCrawler(config)
    
    try:
        # Login (optional - comment out if not needed)
        if config.LINKEDIN_EMAIL and config.LINKEDIN_PASSWORD:
            print("🔐 Logging in to LinkedIn...")
            crawler.login()
            print("✅ Login successful!\n")
        else:
            print("⚠️  No credentials provided - running without login\n")
        
        # Example 1: Search and scrape jobs
        print("=" * 60)
        print("📊 SEARCHING FOR JOBS")
        print("=" * 60)
        
        keywords = input("Enter job keywords (e.g., 'Python Developer'): ").strip()
        location = input("Enter location (e.g., 'United States'): ").strip()
        max_results = int(input("How many jobs to scrape? (1-20): ").strip() or "5")
        
        print(f"\n🔍 Searching for: '{keywords}' in '{location}'...")
        job_urls = crawler.search_jobs(keywords, location, max_results)
        
        if not job_urls:
            print("❌ No jobs found!")
            return
        
        print(f"✅ Found {len(job_urls)} jobs!\n")
        
        # Scrape each job
        print("=" * 60)
        print("📥 SCRAPING JOB DETAILS")
        print("=" * 60 + "\n")
        
        scraped_jobs = []
        for i, url in enumerate(job_urls, 1):
            print(f"[{i}/{len(job_urls)}] Scraping job...")
            job_data = crawler.scrape_job(url)
            
            if job_data:
                scraped_jobs.append(job_data)
                print(f"✅ Title: {job_data.get('title', 'N/A')}")
                print(f"   Company: {job_data.get('company', 'N/A')}")
                print(f"   Location: {job_data.get('location', 'N/A')}")
                print(f"   Posted: {job_data.get('posted_date', 'N/A')}\n")
            else:
                print(f"❌ Failed to scrape job\n")
        
        # Display cache statistics
        print("\n" + "=" * 60)
        print("📊 CACHE STATISTICS")
        print("=" * 60)
        stats = crawler.get_cache_stats()
        print(f"Total Jobs Cached: {stats['total_jobs']}")
        print(f"Total Profiles Cached: {stats['total_profiles']}")
        print(f"Valid Jobs: {stats['valid_jobs']}")
        print(f"Valid Profiles: {stats['valid_profiles']}")
        print(f"Database Size: {stats['database_size_mb']} MB")
        print(f"Cache Expiry: {stats['cache_expiry_days']} days")
        
        # Export option
        print("\n" + "=" * 60)
        export = input("\n💾 Export data to JSON? (y/n): ").strip().lower()
        if export == 'y':
            filename = input("Enter filename (default: export.json): ").strip() or "export.json"
            crawler.db.export_to_json(filename)
            print(f"✅ Data exported to {filename}")
        
        print("\n✨ Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("\n🔒 Closing crawler...")
        crawler.close()
        print("👋 Goodbye!\n")


if __name__ == "__main__":
    main()


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