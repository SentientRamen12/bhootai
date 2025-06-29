import sqlite3
import chromadb
from config.configs import SQLITE_DB_PATH, CHROMADB_PATH

def get_sqlite_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(SQLITE_DB_PATH)

def get_chromadb_client():
    """Get ChromaDB client"""
    return chromadb.PersistentClient(path=str(CHROMADB_PATH)) 