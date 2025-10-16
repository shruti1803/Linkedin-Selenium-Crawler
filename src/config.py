"""
Configuration and Utility modules
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for crawler settings"""
    
    # LinkedIn credentials
    LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '')
    
    # Scraping settings
    WAIT_TIMEOUT = int(os.getenv('WAIT_TIMEOUT', '10'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))
    
    # Cache settings
    CACHE_EXPIRY_DAYS = int(os.getenv('CACHE_EXPIRY_DAYS', '7'))
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/linkedin_cache.db')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/crawler.log')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.LINKEDIN_EMAIL or not cls.LINKEDIN_PASSWORD:
            print("Warning: LinkedIn credentials not set in .env file")
        
        if cls.MAX_RETRIES < 1:
            raise ValueError("MAX_RETRIES must be at least 1")
        
        if cls.CACHE_EXPIRY_DAYS < 1:
            raise ValueError("CACHE_EXPIRY_DAYS must be at least 1")