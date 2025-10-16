"""
Test suite for LinkedIn Crawler
"""

# ==================== tests/test_crawler.py ====================

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.crawler import LinkedInCrawler
from src.database import Database
from src.config import Config
from src.utils import (
    generate_cache_key,
    validate_url,
    extract_job_id,
    extract_profile_id,
    clean_text
)


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_generate_cache_key(self):
        """Test cache key generation"""
        url = "https://www.linkedin.com/jobs/view/12345"
        key1 = generate_cache_key(url)
        key2 = generate_cache_key(url)
        
        # Same URL should produce same key
        self.assertEqual(key1, key2)
        
        # Key should be 32 characters (MD5 hash)
        self.assertEqual(len(key1), 32)
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid job URL
        self.assertTrue(validate_url(
            'https://www.linkedin.com/jobs/view/12345',
            'job'
        ))
        
        # Valid profile URL
        self.assertTrue(validate_url(
            'https://www.linkedin.com/in/john-doe',
            'profile'
        ))
        
        # Invalid URLs
        self.assertFalse(validate_url('invalid-url', 'job'))
        self.assertFalse(validate_url('', 'job'))
        self.assertFalse(validate_url(None, 'job'))
    
    def test_extract_job_id(self):
        """Test job ID extraction"""
        url = "https://www.linkedin.com/jobs/view/3812345678"
        job_id = extract_job_id(url)
        self.assertEqual(job_id, '3812345678')
        
        # With query parameters
        url_with_params = "https://www.linkedin.com/jobs/view/3812345678?param=value"
        job_id = extract_job_id(url_with_params)
        self.assertEqual(job_id, '3812345678')
    
    def test_extract_profile_id(self):
        """Test profile ID extraction"""
        url = "https://www.linkedin.com/in/john-doe-12345"
        profile_id = extract_profile_id(url)
        self.assertEqual(profile_id, 'john-doe-12345')
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  Multiple   spaces\n\nand\tnewlines  "
        clean = clean_text(dirty_text)
        self.assertEqual(clean, "Multiple spaces and newlines")
        
        # Handle N/A
        self.assertEqual(clean_text('N/A'), 'N/A')


class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Setup test database"""
        self.test_db_path = 'test_cache.db'
        self.db = Database(cache_expiry_days=7, db_path=self.test_db_path)
    
    def tearDown(self):
        """Cleanup test database"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_save_and_retrieve_job(self):
        """Test saving and retrieving job data"""
        cache_key = "test_job_key_123"
        job_data = {
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'description': 'Great opportunity',
            'url': 'https://linkedin.com/jobs/view/123'
        }
        
        # Save job
        self.db.save_job(cache_key, job_data)
        
        # Retrieve job
        retrieved = self.db.get_cached_job(cache_key)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], 'Python Developer')
        self.assertEqual(retrieved['company'], 'Tech Corp')
    
    def test_save_and_retrieve_profile(self):
        """Test saving and retrieving profile data"""
        cache_key = "test_profile_key_456"
        profile_data = {
            'name': 'John Doe',
            'headline': 'Software Engineer',
            'location': 'San Francisco',
            'url': 'https://linkedin.com/in/johndoe'
        }
        
        # Save profile
        self.db.save_profile(cache_key, profile_data)
        
        # Retrieve profile
        retrieved = self.db.get_cached_profile(cache_key)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], 'John Doe')
        self.assertEqual(retrieved['headline'], 'Software Engineer')
    
    def test_cache_expiry(self):
        """Test cache expiry functionality"""
        # Create database with 0 day expiry
        short_db = Database(cache_expiry_days=0, db_path='short_cache.db')
        
        cache_key = "expired_key"
        job_data = {'title': 'Test Job', 'url': 'http://test.com'}
        
        short_db.save_job(cache_key, job_data)
        
        # Should return None because it's expired
        retrieved = short_db.get_cached_job(cache_key)
        self.assertIsNone(retrieved)
        
        short_db.close()
        if os.path.exists('short_cache.db'):
            os.remove('short_cache.db')
    
    def test_get_cache_stats(self):
        """Test cache statistics"""
        stats = self.db.get_cache_stats()
        
        self.assertIn('total_jobs', stats)
        self.assertIn('total_profiles', stats)
        self.assertIn('database_size_mb', stats)
        self.assertIn('cache_expiry_days', stats)
        
        self.assertEqual(stats['cache_expiry_days'], 7)
    
    def test_search_jobs(self):
        """Test job search functionality"""
        # Add test jobs
        jobs = [
            {'title': 'Python Developer', 'company': 'Company A', 'location': 'NYC'},
            {'title': 'Java Developer', 'company': 'Company B', 'location': 'SF'},
            {'title': 'Python Engineer', 'company': 'Company C', 'location': 'NYC'}
        ]
        
        for i, job in enumerate(jobs):
            job['url'] = f'http://test.com/{i}'
            self.db.save_job(f'key_{i}', job)
        
        # Search by keyword
        results = self.db.search_jobs(keyword='Python')
        self.assertEqual(len(results), 2)
        
        # Search by location
        results = self.db.search_jobs(location='NYC')
        self.assertEqual(len(results), 2)
        
        # Search by company
        results = self.db.search_jobs(company='Company A')
        self.assertEqual(len(results), 1)


class TestConfig(unittest.TestCase):
    """Test configuration"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = Config()
        
        self.assertEqual(config.MAX_RETRIES, 3)
        self.assertEqual(config.RETRY_DELAY, 2)
        self.assertEqual(config.WAIT_TIMEOUT, 10)
        self.assertEqual(config.CACHE_EXPIRY_DAYS, 7)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Should not raise any errors with valid config
        try:
            Config.validate()
        except ValueError:
            self.fail("Config validation raised ValueError unexpectedly")


class TestCrawlerInitialization(unittest.TestCase):
    """Test crawler initialization (without actual scraping)"""
    
    def test_crawler_init(self):
        """Test crawler initialization"""
        config = Config()
        config.HEADLESS_MODE = True
        
        crawler = LinkedInCrawler(config)
        
        self.assertIsNotNone(crawler.driver)
        self.assertIsNotNone(crawler.db)
        self.assertEqual(crawler.max_retries, 3)
        
        crawler.close()


def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
