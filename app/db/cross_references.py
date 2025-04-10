from sqlalchemy.orm import Session
from .models import Verse, CrossReference, Book, Chapter

def get_verse_id(db: Session, book_name: str, chapter: int, verse: int):
    """Helper function to get a verse ID by book, chapter, and verse number"""
    try:
        book = db.query(Book).filter(Book.name == book_name).first()
        if not book:
            return None
            
        chapter_obj = db.query(Chapter).filter(
            Chapter.book_id == book.id, 
            Chapter.number == chapter
        ).first()
        if not chapter_obj:
            return None
            
        verse_obj = db.query(Verse).filter(
            Verse.chapter_id == chapter_obj.id,
            Verse.number == verse
        ).first()
        
        return verse_obj.id if verse_obj else None
    except Exception as e:
        print(f"Error finding verse: {e}")
        return None

def populate_cross_references(db: Session):
    """Populate some well-known cross-references, with bi-directional references"""
    # Check if we already have cross-references
    existing = db.query(CrossReference).first()
    if existing:
        print("Cross-references already exist.")
        return
        
    # Define some well-known cross-references
    references = [
        # Format: (source_book, source_chapter, source_verse, target_book, target_chapter, target_verse, type)
        ("John", 1, 29, "Isaiah", 53, 7, "prophetic"),
        ("Matthew", 4, 4, "Deuteronomy", 8, 3, "quotation"),
        ("Romans", 3, 23, "Ecclesiastes", 7, 20, "thematic"),
        ("Hebrews", 11, 1, "Romans", 8, 24, "thematic"),
        ("Matthew", 22, 37, "Deuteronomy", 6, 5, "quotation"),
        ("John", 3, 16, "Romans", 5, 8, "thematic"),
        ("Psalms", 22, 1, "Matthew", 27, 46, "quotation"),
        ("Isaiah", 7, 14, "Matthew", 1, 23, "prophetic"),
        ("Genesis", 1, 1, "John", 1, 1, "thematic"),
        ("Psalms", 23, 1, "John", 10, 11, "thematic"),
    ]
    
    print("Adding cross-references...")
    added = 0
    
    for ref in references:
        source_book, source_chapter, source_verse, target_book, target_chapter, target_verse, ref_type = ref
        
        # Get source verse ID
        source_id = get_verse_id(db, source_book, source_chapter, source_verse)
        if not source_id:
            print(f"Could not find source verse: {source_book} {source_chapter}:{source_verse}")
            continue
            
        # Get target verse ID
        target_id = get_verse_id(db, target_book, target_chapter, target_verse)
        if not target_id:
            print(f"Could not find target verse: {target_book} {target_chapter}:{target_verse}")
            continue
            
        # Create source-to-target cross-reference
        cross_ref = CrossReference(
            source_verse_id=source_id,
            target_verse_id=target_id,
            reference_type=ref_type
        )
        
        db.add(cross_ref)
        added += 1
        
        # Create target-to-source cross-reference (bi-directional)
        cross_ref_reverse = CrossReference(
            source_verse_id=target_id,
            target_verse_id=source_id,
            reference_type=ref_type
        )
        
        db.add(cross_ref_reverse)
        added += 1
        
    try:
        db.commit()
        print(f"Added {added} cross-references.")
    except Exception as e:
        print(f"Error adding cross-references: {e}")
        db.rollback()

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    try:
        populate_cross_references(db)
    finally:
        db.close()