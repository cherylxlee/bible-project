from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db.database import get_db
from .db.models import Book, Chapter, Verse, CrossReference
from typing import List
from pydantic import BaseModel
# from sqlalchemy.orm import joinedload


app = FastAPI(title="Bible Study Tool API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookResponse(BaseModel):
    id: int
    name: str
    abbreviation: str
    testament: str
    
    class Config:
        orm_mode = True

class VerseResponse(BaseModel):
    id: int
    number: int
    text: str
    
    class Config:
        orm_mode = True

class CrossReferenceTarget(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str
    
    class Config:
        orm_mode = True

class CrossReferenceResponse(BaseModel):
    id: int
    reference_type: str
    target: CrossReferenceTarget
    
    class Config:
        orm_mode = True

@app.get("/api/")
def read_root():
    return {"message": "Welcome to the Bible Study Tool API"}

@app.get("/api/books/", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

@app.get("/api/books/{book_name}/chapter-count/")
def get_chapter_count(book_name: str, db: Session = Depends(get_db)):
    # Find the book
    book = db.query(Book).filter(Book.name == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Get the number of chapters for the book
    chapter_count = db.query(Chapter).filter(Chapter.book_id == book.id).count()
    
    return chapter_count

@app.get("/api/books/{book_name}/chapters/{chapter_number}/verses/", response_model=List[VerseResponse])
def get_verses(book_name: str, chapter_number: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.name == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapter = db.query(Chapter).filter(Chapter.book_id == book.id, Chapter.number == chapter_number).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    verses = db.query(Verse).filter(Verse.chapter_id == chapter.id).order_by(Verse.number).all()
    return verses

# Adding simple cross-references
@app.get("/api/books/{book_name}/chapters/{chapter_number}/verses/{verse_number}/cross-references", response_model=List[CrossReferenceResponse])
def get_cross_references(book_name: str, chapter_number: int, verse_number: int, db: Session = Depends(get_db)):
    # Find the verse
    book = db.query(Book).filter(Book.name == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapter = db.query(Chapter).filter(Chapter.book_id == book.id, Chapter.number == chapter_number).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    verse = db.query(Verse).filter(Verse.chapter_id == chapter.id, Verse.number == verse_number).first()
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    # Get cross-references
    cross_refs = []
    db_cross_refs = db.query(CrossReference).filter(CrossReference.source_verse_id == verse.id).all()
    
    for ref in db_cross_refs:
        # Get target verse details
        target_verse = db.query(Verse).filter(Verse.id == ref.target_verse_id).first()
        target_chapter = db.query(Chapter).filter(Chapter.id == target_verse.chapter_id).first()
        target_book = db.query(Book).filter(Book.id == target_chapter.book_id).first()
        
        cross_refs.append({
            "id": ref.id,
            "reference_type": ref.reference_type,
            "target": {
                "book": target_book.name,
                "chapter": target_chapter.number,
                "verse": target_verse.number,
                "text": target_verse.text
            }
        })
    
    return cross_refs

# Mount static files
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
