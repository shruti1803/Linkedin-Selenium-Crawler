import hashlib
import logging
import os
from datetime import datetime


def generate_cache_key(url: str) -> str:
    """
    Generate unique cache key from URL using MD5 hash
    
    Args:
        url: URL to generate key from
        
    Returns:
        MD5 hash as cache key
    """
    return hashlib.md5(url.encode()).hexdigest()


def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/crawler.log'):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")


def format_timestamp(timestamp: str = None) -> str:
    """
    Format timestamp to readable string
    
    Args:
        timestamp: ISO format timestamp (uses current time if None)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp:
        dt = datetime.fromisoformat(timestamp)
    else:
        dt = datetime.now()
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def clean_text(text: str) -> str:
    """
    Clean scraped text by removing extra whitespace and special characters
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text or text == 'N/A':
        return text
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    # Remove newlines and tabs
    text = text.replace('\n', ' ').replace('\t', ' ')
    
    # Remove multiple spaces again
    text = ' '.join(text.split())
    
    return text.strip()


def validate_url(url: str, url_type: str = 'job') -> bool:
    """
    Validate LinkedIn URL format
    
    Args:
        url: URL to validate
        url_type: Type of URL ('job' or 'profile')
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    if url_type == 'job':
        return 'linkedin.com/jobs/view/' in url
    elif url_type == 'profile':
        return 'linkedin.com/in/' in url
    
    return False


def extract_job_id(job_url: str) -> str:
    """
    Extract job ID from LinkedIn job URL
    
    Args:
        job_url: LinkedIn job URL
        
    Returns:
        Job ID or empty string if not found
    """
    try:
        if '/jobs/view/' in job_url:
            parts = job_url.split('/jobs/view/')
            if len(parts) > 1:
                job_id = parts[1].split('/')[0].split('?')[0]
                return job_id
    except:
        pass
    
    return ''


def extract_profile_id(profile_url: str) -> str:
    """
    Extract profile ID from LinkedIn profile URL
    
    Args:
        profile_url: LinkedIn profile URL
        
    Returns:
        Profile ID or empty string if not found
    """
    try:
        if '/in/' in profile_url:
            parts = profile_url.split('/in/')
            if len(parts) > 1:
                profile_id = parts[1].split('/')[0].split('?')[0]
                return profile_id
    except:
        pass
    
    return ''


def create_project_structure():
    """Create necessary project directories"""
    directories = [
        'data',
        'logs',
        'src',
        'tests',
        'examples'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create __init__.py for Python packages
        if directory in ['src', 'tests']:
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'w').close()
    
    print("Project structure created successfully!")


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         LinkedIn Selenium Crawler v1.0                    ║
    ║         Automated Job & Profile Data Extraction           ║
    ║                                                           ║
    ║         Features:                                         ║
    ║         ✓ SQLite Caching                                  ║
    ║         ✓ Retry Logic (30% Reliability Boost)             ║
    ║         ✓ Custom Wait Strategies                          ║
    ║         ✓ Structured Error Handling                       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def calculate_cache_hit_rate(total_requests: int, cache_hits: int) -> float:
    """
    Calculate cache hit rate percentage
    
    Args:
        total_requests: Total number of requests
        cache_hits: Number of cache hits
        
    Returns:
        Cache hit rate as percentage
    """
    if total_requests == 0:
        return 0.0
    
    return round((cache_hits / total_requests) * 100, 2)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size to human-readable string
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    # Test utilities
    print_banner()
    create_project_structure()
    setup_logging()
    
    # Test cache key generation
    test_url = "https://www.linkedin.com/jobs/view/12345"
    cache_key = generate_cache_key(test_url)
    print(f"\nCache key for '{test_url}': {cache_key}")
    
    # Test URL validation
    print(f"\nJob URL valid: {validate_url(test_url, 'job')}")
    print(f"Job ID: {extract_job_id(test_url)}")