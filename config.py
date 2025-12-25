# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
    
    # Rate Limiting
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv('RATE_LIMIT_MAX', '100'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATASET_DIR = BASE_DIR / 'datasets'
    OUTPUT_DIR = BASE_DIR / 'outputs'
    LOG_DIR = BASE_DIR / 'logs'
    MODEL_DIR = BASE_DIR / 'models'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    @classmethod
    def init_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.DATASET_DIR, cls.OUTPUT_DIR, cls.LOG_DIR, cls.MODEL_DIR]:
            dir_path.mkdir(exist_ok=True)

# Initialize directories on import
Config.init_directories()