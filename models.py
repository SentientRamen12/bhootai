# Conversations

# interactions

import sqlite3
from datetime import datetime
from typing import List, Optional

class Conversation:
    def __init__(self, sender: str, receiver: str, message: str, timestamp: Optional[datetime] = None, id: Optional[int] = None):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.timestamp = timestamp or datetime.now()
    
    def save(self, db_connection: sqlite3.Connection) -> int:
        """Save conversation to database"""
        cursor = db_connection.cursor()
        cursor.execute('''
            INSERT INTO conversations (sender, receiver, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (self.sender, self.receiver, self.message, self.timestamp))
        db_connection.commit()
        self.id = cursor.lastrowid
        return self.id
    
    @classmethod
    def get_by_id(cls, db_connection: sqlite3.Connection, conversation_id: int) -> Optional['Conversation']:
        """Get conversation by ID"""
        cursor = db_connection.cursor()
        cursor.execute('SELECT id, sender, receiver, message, timestamp FROM conversations WHERE id = ?', (conversation_id,))
        row = cursor.fetchone()
        if row:
            return cls(sender=row[1], receiver=row[2], message=row[3], timestamp=row[4], id=row[0])
        return None
    
    @classmethod
    def get_conversation_history(cls, db_connection: sqlite3.Connection, sender: str = None, receiver: str = None, limit: int = 100) -> List['Conversation']:
        """Get conversation history with optional filters"""
        cursor = db_connection.cursor()
        
        if sender and receiver:
            cursor.execute('''
                SELECT id, sender, receiver, message, timestamp 
                FROM conversations 
                WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (sender, receiver, receiver, sender, limit))
        elif sender:
            cursor.execute('''
                SELECT id, sender, receiver, message, timestamp 
                FROM conversations 
                WHERE sender = ? OR receiver = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (sender, sender, limit))
        elif receiver:
            cursor.execute('''
                SELECT id, sender, receiver, message, timestamp 
                FROM conversations 
                WHERE sender = ? OR receiver = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (receiver, receiver, limit))
        else:
            cursor.execute('''
                SELECT id, sender, receiver, message, timestamp 
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append(cls(sender=row[1], receiver=row[2], message=row[3], timestamp=row[4], id=row[0]))
        
        return conversations

class Interaction:
    def __init__(self, entity: str, description: str, timestamp: Optional[datetime] = None, id: Optional[int] = None):
        self.id = id
        self.entity = entity
        self.description = description
        self.timestamp = timestamp or datetime.now()
    
    def save(self, db_connection: sqlite3.Connection) -> int:
        """Save interaction to database"""
        cursor = db_connection.cursor()
        cursor.execute('''
            INSERT INTO interactions (entity, description, timestamp)
            VALUES (?, ?, ?)
        ''', (self.entity, self.description, self.timestamp))
        db_connection.commit()
        self.id = cursor.lastrowid
        return self.id
    
    @classmethod
    def get_by_id(cls, db_connection: sqlite3.Connection, interaction_id: int) -> Optional['Interaction']:
        """Get interaction by ID"""
        cursor = db_connection.cursor()
        cursor.execute('SELECT id, entity, description, timestamp FROM interactions WHERE id = ?', (interaction_id,))
        row = cursor.fetchone()
        if row:
            return cls(entity=row[1], description=row[2], timestamp=row[3], id=row[0])
        return None
    
    @classmethod
    def get_by_entity(cls, db_connection: sqlite3.Connection, entity: str, limit: int = 100) -> List['Interaction']:
        """Get interactions by entity"""
        cursor = db_connection.cursor()
        cursor.execute('''
            SELECT id, entity, description, timestamp 
            FROM interactions 
            WHERE entity = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (entity, limit))
        
        interactions = []
        for row in cursor.fetchall():
            interactions.append(cls(entity=row[1], description=row[2], timestamp=row[3], id=row[0]))
        
        return interactions
    
    @classmethod
    def get_recent_interactions(cls, db_connection: sqlite3.Connection, limit: int = 100) -> List['Interaction']:
        """Get recent interactions"""
        cursor = db_connection.cursor()
        cursor.execute('''
            SELECT id, entity, description, timestamp 
            FROM interactions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        interactions = []
        for row in cursor.fetchall():
            interactions.append(cls(entity=row[1], description=row[2], timestamp=row[3], id=row[0]))
        
        return interactions

