"""
Example script for scraping LinkedIn profiles
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.crawler import LinkedInCrawler
from src.config import Config
from src.utils import setup_logging, print_banner, validate_url
import json


def scrape_profiles_example():
    """Example: Scrape multiple LinkedIn profiles"""
    
    print_banner()
    setup_logging()
    
    # Initialize crawler
    config = Config()
    crawler = LinkedInCrawler(config)
    
    try:
        # Login (required for profiles)
        print("⚠️  Note: Login required to view profiles")
        if config.LINKEDIN_EMAIL and config.LINKEDIN_PASSWORD:
            crawler.login()
        else:
            email = input("LinkedIn Email: ")
            password = input("LinkedIn Password: ")
            crawler.login(email, password)
        
        # Profile URLs to scrape
        profile_urls = []
        
        print("\n" + "="*60)
        print("Enter LinkedIn profile URLs (one per line)")
        print("Press Enter twice when done")
        print("="*60)
        
        while True:
            url = input("Profile URL: ").strip()
            if not url:
                break
            
            if validate_url(url, 'profile'):
                profile_urls.append(url)
                print("✅ Added")
            else:
                print("❌ Invalid LinkedIn profile URL")
        
        if not profile_urls:
            print("No profiles to scrape!")
            return
        
        # Scrape profiles
        all_profiles = []
        
        print(f"\n{'='*60}")
        print(f"Scraping {len(profile_urls)} profiles")
        print('='*60)
        
        for i, url in enumerate(profile_urls, 1):
            print(f"\n[{i}/{len(profile_urls)}] Scraping profile...")
            profile_data = crawler.scrape_profile(url)
            
            if profile_data:
                all_profiles.append(profile_data)
                print(f"✅ {profile_data.get('name')}")
                print(f"   {profile_data.get('headline')}")
                print(f"   {profile_data.get('location')}")
            else:
                print("❌ Failed to scrape")
        
        # Save to JSON
        output_file = 'scraped_profiles.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_profiles, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Scraped {len(all_profiles)} profiles")
        print(f"📁 Data saved to {output_file}")
        
        # Display cache stats
        stats = crawler.get_cache_stats()
        print(f"\n📊 Cache Stats:")
        print(f"   Total profiles cached: {stats['total_profiles']}")
        print(f"   Database size: {stats['database_size_mb']} MB")
        
    finally:
        crawler.close()


if __name__ == "__main__":
    scrape_profiles_example()


