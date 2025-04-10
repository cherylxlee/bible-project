import requests
import json
import os
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, Book, Chapter, Verse

def import_kjv_from_json():
    """
    Import KJV Bible text from a JSON file
    """
    # URL to a public domain KJV Bible in JSON format
    kjv_url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"
    
    try:
        print("Downloading KJV Bible data...")
        # Download the JSON file
        response = requests.get(kjv_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download Bible data: Status code {response.status_code}")
            
        # bible_data = response.json()
        bible_data = json.loads(response.content.decode('utf-8-sig'))
        
        # Create database session
        db = SessionLocal()
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check if we already have data
        if db.query(Book).first():
            print("Bible data already exists. Skipping import.")
            return
        
        print(f"Found {len(bible_data)} books in the Bible data")
            
        # Process the JSON data
        for book_idx, book_data in enumerate(bible_data, 1):
            try:
                # Determine testament
                testament = "OT" if book_idx <= 39 else "NT"
                
                # Get book name and abbreviation
                book_name = book_data.get("name")
                if not book_name:
                    print(f"Skipping book at index {book_idx}: Missing name")
                    continue
                    
                abbreviation = book_data.get("abbrev", book_name[:3])
                
                # Add book
                book = Book(
                    name=book_name,
                    abbreviation=abbreviation,
                    testament=testament
                )
                db.add(book)
                db.flush()  # This gives us the book ID
                
                # Get chapters
                chapters = book_data.get("chapters", [])
                if not chapters:
                    print(f"Warning: No chapters found for {book_name}")
                    continue
                
                print(f"Importing {book_name} with {len(chapters)} chapters...")
                
                # Add chapters and verses
                for chapter_idx, chapter_verses in enumerate(chapters, 1):
                    # Add chapter
                    chapter = Chapter(
                        number=chapter_idx,
                        book_id=book.id
                    )
                    db.add(chapter)
                    db.flush()  # This gives us the chapter ID
                    
                    # Add verses
                    if not isinstance(chapter_verses, list):
                        print(f"Warning: Invalid chapter format for {book_name} chapter {chapter_idx}")
                        continue
                        
                    for verse_idx, verse_text in enumerate(chapter_verses, 1):
                        if verse_text:  # Skip empty verses
                            verse = Verse(
                                number=verse_idx,
                                text=verse_text,
                                chapter_id=chapter.id
                            )
                            db.add(verse)
                
                # Commit after each book to avoid large transactions
                db.commit()
                print(f"Successfully imported {book_name}")
                
            except Exception as e:
                print(f"Error importing book {book_idx}: {e}")
                db.rollback()
        
        print("Bible import completed successfully!")
        
    except Exception as e:
        print(f"Error importing Bible: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    import_kjv_from_json()
