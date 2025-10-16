"""
Database module for SQLite-based caching
Provides quick, structured data retrieval
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for caching scraped data"""
    
    def __init__(self, cache_expiry_days: int = 7, db_path: str = 'data/linkedin_cache.db'):
        """
        Initialize database connection
        
        Args:
            cache_expiry_days: Days before cache expires
            db_path: Path to SQLite database file
        """
        self.cache_expiry_days = cache_expiry_days
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = self._create_connection()
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                posted_date TEXT,
                job_type TEXT,
                seniority_level TEXT,
                job_url TEXT,
                scraped_at TIMESTAMP NOT NULL,
                data_json TEXT NOT NULL,
                UNIQUE(cache_key)
            )
        ''')
        
        # Profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                name TEXT,
                headline TEXT,
                location TEXT,
                about TEXT,
                connections TEXT,
                profile_url TEXT,
                scraped_at TIMESTAMP NOT NULL,
                data_json TEXT NOT NULL,
                UNIQUE(cache_key)
            )
        ''')
        
        # Create indices for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_jobs_cache_key 
            ON jobs(cache_key)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at 
            ON jobs(scraped_at)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_profiles_cache_key 
            ON profiles(cache_key)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_profiles_scraped_at 
            ON profiles(scraped_at)
        ''')
        
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    def get_cached_job(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached job data if not expired
        
        Args:
            cache_key: Unique cache key for the job
            
        Returns:
            Dict with job data or None if not found/expired
        """
        cursor = self.conn.cursor()
        expiry_date = datetime.now() - timedelta(days=self.cache_expiry_days)
        
        cursor.execute('''
            SELECT data_json FROM jobs
            WHERE cache_key = ? AND scraped_at > ?
        ''', (cache_key, expiry_date))
        
        result = cursor.fetchone()
        
        if result:
            logger.debug(f"Cache hit for job key: {cache_key}")
            return json.loads(result['data_json'])
        
        logger.debug(f"Cache miss for job key: {cache_key}")
        return None
    
    def get_cached_profile(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached profile data if not expired
        
        Args:
            cache_key: Unique cache key for the profile
            
        Returns:
            Dict with profile data or None if not found/expired
        """
        cursor = self.conn.cursor()
        expiry_date = datetime.now() - timedelta(days=self.cache_expiry_days)
        
        cursor.execute('''
            SELECT data_json FROM profiles
            WHERE cache_key = ? AND scraped_at > ?
        ''', (cache_key, expiry_date))
        
        result = cursor.fetchone()
        
        if result:
            logger.debug(f"Cache hit for profile key: {cache_key}")
            return json.loads(result['data_json'])
        
        logger.debug(f"Cache miss for profile key: {cache_key}")
        return None
    
    def save_job(self, cache_key: str, job_data: Dict):
        """
        Save job data to cache
        
        Args:
            cache_key: Unique cache key
            job_data: Job data dictionary
        """
        cursor = self.conn.cursor()
        data_json = json.dumps(job_data, ensure_ascii=False)
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (cache_key, title, company, location, description, 
                 posted_date, job_type, seniority_level, job_url, 
                 scraped_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key,
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                job_data.get('description'),
                job_data.get('posted_date'),
                job_data.get('job_type'),
                job_data.get('seniority_level'),
                job_data.get('url'),
                datetime.now(),
                data_json
            ))
            
            self.conn.commit()
            logger.debug(f"Job data cached with key: {cache_key}")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to save job to cache: {e}")
            self.conn.rollback()
    
    def save_profile(self, cache_key: str, profile_data: Dict):
        """
        Save profile data to cache
        
        Args:
            cache_key: Unique cache key
            profile_data: Profile data dictionary
        """
        cursor = self.conn.cursor()
        data_json = json.dumps(profile_data, ensure_ascii=False)
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO profiles 
                (cache_key, name, headline, location, about, 
                 connections, profile_url, scraped_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key,
                profile_data.get('name'),
                profile_data.get('headline'),
                profile_data.get('location'),
                profile_data.get('about'),
                profile_data.get('connections'),
                profile_data.get('url'),
                datetime.now(),
                data_json
            ))
            
            self.conn.commit()
            logger.debug(f"Profile data cached with key: {cache_key}")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to save profile to cache: {e}")
            self.conn.rollback()
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dict with cache statistics
        """
        cursor = self.conn.cursor()
        
        # Total jobs
        cursor.execute('SELECT COUNT(*) as count FROM jobs')
        total_jobs = cursor.fetchone()['count']
        
        # Total profiles
        cursor.execute('SELECT COUNT(*) as count FROM profiles')
        total_profiles = cursor.fetchone()['count']
        
        # Expired jobs
        expiry_date = datetime.now() - timedelta(days=self.cache_expiry_days)
        cursor.execute('SELECT COUNT(*) as count FROM jobs WHERE scraped_at <= ?', (expiry_date,))
        expired_jobs = cursor.fetchone()['count']
        
        # Expired profiles
        cursor.execute('SELECT COUNT(*) as count FROM profiles WHERE scraped_at <= ?', (expiry_date,))
        expired_profiles = cursor.fetchone()['count']
        
        # Database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()['size']
        
        return {
            'total_jobs': total_jobs,
            'total_profiles': total_profiles,
            'expired_jobs': expired_jobs,
            'expired_profiles': expired_profiles,
            'valid_jobs': total_jobs - expired_jobs,
            'valid_profiles': total_profiles - expired_profiles,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'cache_expiry_days': self.cache_expiry_days
        }
    
    def clear_cache(self, older_than_days: int = None):
        """
        Clear cache entries
        
        Args:
            older_than_days: Clear entries older than specified days (None = clear all)
        """
        cursor = self.conn.cursor()
        
        try:
            if older_than_days is None:
                # Clear all cache
                cursor.execute('DELETE FROM jobs')
                cursor.execute('DELETE FROM profiles')
                logger.info("All cache cleared")
            else:
                # Clear expired cache
                expiry_date = datetime.now() - timedelta(days=older_than_days)
                cursor.execute('DELETE FROM jobs WHERE scraped_at <= ?', (expiry_date,))
                jobs_deleted = cursor.rowcount
                cursor.execute('DELETE FROM profiles WHERE scraped_at <= ?', (expiry_date,))
                profiles_deleted = cursor.rowcount
                logger.info(f"Cleared {jobs_deleted} jobs and {profiles_deleted} profiles older than {older_than_days} days")
            
            self.conn.commit()
            
            # Vacuum to reclaim space
            cursor.execute('VACUUM')
            
        except sqlite3.Error as e:
            logger.error(f"Failed to clear cache: {e}")
            self.conn.rollback()
    
    def search_jobs(self, keyword: str = None, company: str = None, location: str = None, limit: int = 10) -> list:
        """
        Search cached jobs by keyword, company, or location
        
        Args:
            keyword: Search in title and description
            company: Search by company name
            location: Search by location
            limit: Maximum results to return
            
        Returns:
            List of job dictionaries
        """
        cursor = self.conn.cursor()
        
        query = 'SELECT data_json FROM jobs WHERE 1=1'
        params = []
        
        if keyword:
            query += ' AND (title LIKE ? OR description LIKE ?)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        if company:
            query += ' AND company LIKE ?'
            params.append(f'%{company}%')
        
        if location:
            query += ' AND location LIKE ?'
            params.append(f'%{location}%')
        
        query += ' ORDER BY scraped_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [json.loads(row['data_json']) for row in results]
    
    def export_to_json(self, output_file: str = 'export.json'):
        """
        Export all cached data to JSON file
        
        Args:
            output_file: Output file path
        """
        cursor = self.conn.cursor()
        
        # Get all jobs
        cursor.execute('SELECT data_json FROM jobs')
        jobs = [json.loads(row['data_json']) for row in cursor.fetchall()]
        
        # Get all profiles
        cursor.execute('SELECT data_json FROM profiles')
        profiles = [json.loads(row['data_json']) for row in cursor.fetchall()]
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_jobs': len(jobs),
            'total_profiles': len(profiles),
            'jobs': jobs,
            'profiles': profiles
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data exported to {output_file}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")