from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    abbreviation = Column(String, unique=True)
    testament = Column(String)  # 'OT' or 'NT'
    
    # Relationship to chapters
    chapters = relationship("Chapter", back_populates="book")
    
class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    book_id = Column(Integer, ForeignKey("books.id"))
    
    # Relationships
    book = relationship("Book", back_populates="chapters")
    verses = relationship("Verse", back_populates="chapter")

class Verse(Base):
    __tablename__ = "verses"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    text = Column(Text)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    
    # Relationship
    chapter = relationship("Chapter", back_populates="verses")

class CrossReference(Base):
    __tablename__ = "cross_references"
    
    id = Column(Integer, primary_key=True, index=True)
    source_verse_id = Column(Integer, ForeignKey("verses.id"))
    target_verse_id = Column(Integer, ForeignKey("verses.id"))
    reference_type = Column(String)  # e.g., 'direct', 'thematic', 'parallel'