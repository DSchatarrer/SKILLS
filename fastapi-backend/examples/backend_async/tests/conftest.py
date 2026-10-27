"""Tests need explicit non-production defaults; never embed real secrets."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
os.environ.setdefault('FASTAPI_SECRET_KEY', 'test-fastapi-secret-never-in-production')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret-never-in-production')
os.environ.setdefault('API_KEY', 'test-api-key')
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///:memory:')
