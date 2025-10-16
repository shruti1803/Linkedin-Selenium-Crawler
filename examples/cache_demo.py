"""
Demonstrate caching capabilities
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.crawler import LinkedInCrawler
from src.config import Config
from src.utils import setup_logging


def cache_demo():
    """Demonstrate caching performance"""
    
    setup_logging()
    
    config = Config()
    crawler = LinkedInCrawler(config)
    
    try:
        # Example job URL
        job_url = input("Enter a LinkedIn job URL: ").strip()
        
        print("\n" + "="*60)
        print("FIRST SCRAPE (No Cache)")
        print("="*60)
        
        start = time.time()
        job_data1 = crawler.scrape_job(job_url)
        time1 = time.time() - start
        
        print(f"✅ Scraped in {time1:.2f} seconds")
        print(f"Title: {job_data1.get('title')}")
        
        print("\n" + "="*60)
        print("SECOND SCRAPE (With Cache)")
        print("="*60)
        
        start = time.time()
        job_data2 = crawler.scrape_job(job_url)
        time2 = time.time() - start
        
        print(f"✅ Retrieved in {time2:.2f} seconds")
        print(f"Title: {job_data2.get('title')}")
        
        print("\n" + "="*60)
        print("PERFORMANCE COMPARISON")
        print("="*60)
        print(f"First scrape:  {time1:.2f}s")
        print(f"Second scrape: {time2:.2f}s (from cache)")
        print(f"Speed improvement: {((time1 - time2) / time1 * 100):.1f}%")
        
        # Cache stats
        stats = crawler.get_cache_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"   Total entries: {stats['total_jobs'] + stats['total_profiles']}")
        print(f"   Database size: {stats['database_size_mb']} MB")
        
    finally:
        crawler.close()


if __name__ == "__main__":
    cache_demo()