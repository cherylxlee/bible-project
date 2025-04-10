// DOM elements
const bookDropdownBtn = document.getElementById('book-dropdown-btn');
const bookDropdownContent = document.getElementById('book-dropdown-content');
const chapterDropdownBtn = document.getElementById('chapter-dropdown-btn');
const chapterDropdownContent = document.getElementById('chapter-dropdown-content');
const passageTitle = document.getElementById('passage-title');
const passageText = document.getElementById('passage-text');

// State variables
let selectedBook = '';
let selectedChapter = '';

// API endpoints
const API_URL = 'http://127.0.0.1:8000/api';

function toggleDropdown(dropdownElement) {
    dropdownElement.classList.toggle("show");
}

// Close all dropdowns when clicking outside
window.onclick = function(event) {
    if (!event.target.matches('.dropdown-btn')) {
        const dropdowns = document.getElementsByClassName('dropdown-content');
        for (let i = 0; i < dropdowns.length; i++) {
            if (dropdowns[i].classList.contains('show')) {
                dropdowns[i].classList.remove('show');
            }
        }
    }
}

// Book dropdown toggle
bookDropdownBtn.addEventListener('click', () => {
    toggleDropdown(bookDropdownContent);
});

// Chapter dropdown toggle
chapterDropdownBtn.addEventListener('click', () => {
    if (!chapterDropdownBtn.disabled) {
        toggleDropdown(chapterDropdownContent);
    }
});

// Fetch all books when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_URL}/books/`);
        const books = await response.json();
        
        // Clear any existing options
        bookDropdownContent.innerHTML = '';
        
        // Populate book dropdown
        books.forEach(book => {
            const bookItem = document.createElement('div');
            bookItem.className = 'dropdown-item';
            bookItem.textContent = book.name;
            bookItem.addEventListener('click', () => {
                selectedBook = book.name;
                bookDropdownBtn.textContent = book.name;
                bookDropdownContent.classList.remove('show');
                populateChapters(book.name);
            });
            bookDropdownContent.appendChild(bookItem);
        });
    } catch (error) {
        console.error('Error fetching books:', error);
    }
});

// Populate chapters for selected book
async function populateChapters(bookName) {
    // Clear previous chapters and reset state
    chapterDropdownContent.innerHTML = '';
    chapterDropdownBtn.textContent = 'Select a Chapter';
    chapterDropdownBtn.disabled = false;
    selectedChapter = '';
    
    try {
        // Fetch the chapter count for the selected book
        const response = await fetch(`${API_URL}/books/${bookName}/chapter-count/`);
        const chapterCount = await response.json();
        
        // Add chapter options based on the actual number of chapters
        for (let i = 1; i <= chapterCount; i++) {
            const chapterItem = document.createElement('div');
            chapterItem.className = 'dropdown-item';
            chapterItem.textContent = i;
            chapterItem.addEventListener('click', () => {
                selectedChapter = i;
                chapterDropdownBtn.textContent = `Chapter ${i}`;
                chapterDropdownContent.classList.remove('show');
                fetchVerses(selectedBook, selectedChapter);
            });
            chapterDropdownContent.appendChild(chapterItem);
        }
    } catch (error) {
        console.error('Error fetching chapter count:', error);
        chapterDropdownContent.innerHTML = '<p>Error fetching chapter data.</p>';
    }
}

// Fetch and display verses
async function fetchVerses(book, chapter) {
    try {
        const response = await fetch(`${API_URL}/books/${book}/chapters/${chapter}/verses/`);
        const verses = await response.json();
        
        passageTitle.textContent = (book === "Psalms")
            ? `Psalm ${chapter}`
            : `${book} ${chapter}`;  // For all other books
        passageText.innerHTML = '';
        
        for (const verse of verses) {
            const verseElement = document.createElement('div');
            verseElement.className = 'verse';
            verseElement.id = `verse-${verse.number}`;
            
            const verseContent = document.createElement('div');
            verseContent.className = 'verse-content';
            verseContent.innerHTML = `<span class="verse-number">${verse.number}</span> ${verse.text}`;
            
            // Click handler to toggle/show cross-references
            verseContent.addEventListener('click', () => fetchCrossReferences(book, chapter, verse.number));
            
            verseElement.appendChild(verseContent);
            
            const refsContainer = document.createElement('div');
            refsContainer.className = 'cross-references';
            refsContainer.id = `refs-${verse.number}`;
            verseElement.appendChild(refsContainer);
            
            passageText.appendChild(verseElement);
        }
    } catch (error) {
        console.error('Error fetching verses:', error);
        passageText.innerHTML = '<p>Error loading passage. The chapter may not exist in this book.</p>';
    }
}

// Fetch and display cross-references for a specific verse
async function fetchCrossReferences(book, chapter, verse) {
    const refsContainer = document.getElementById(`refs-${verse}`);
    
    if (refsContainer.dataset.loaded) {
        refsContainer.classList.toggle('visible');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/books/${book}/chapters/${chapter}/verses/${verse}/cross-references`);
        const references = await response.json();
        
        if (references.length === 0) {
            refsContainer.classList.remove('visible');  // Hide the container if no references exist
            return;  // Return early if there are no references
        } else {
            const refsList = document.createElement('ul');
            refsList.className = 'refs-list';
            
            references.forEach(ref => {
                const refItem = document.createElement('li');
                refItem.className = `ref-type-${ref.reference_type}`;
                refItem.innerHTML = `
                    <span class="ref-type">${ref.reference_type}</span>
                    <a href="#" class="ref-link" data-book="${ref.target.book}" data-chapter="${ref.target.chapter}" data-verse="${ref.target.verse}">
                        ${ref.target.book} ${ref.target.chapter}:${ref.target.verse}
                    </a>
                    <div class="ref-text">"${ref.target.text}"</div>
                `;
                
                const refLink = refItem.querySelector('.ref-link');
                refLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetBook = refLink.dataset.book;
                    const targetChapter = refLink.dataset.chapter;
                    
                    // Update UI
                    selectedBook = targetBook;
                    selectedChapter = targetChapter;
                    bookDropdownBtn.textContent = targetBook;
                    populateChapters(targetBook);
                    
                    // Need to wait for chapter options to be populated
                    setTimeout(() => {
                        chapterDropdownBtn.textContent = `Chapter ${targetChapter}`;
                        fetchVerses(targetBook, targetChapter);
                        
                        // Scroll to verse after content loads
                        setTimeout(() => {
                            const targetVerse = document.getElementById(`verse-${refLink.dataset.verse}`);
                            if (targetVerse) {
                                targetVerse.scrollIntoView({ behavior: 'smooth' });
                                targetVerse.classList.add('highlighted');
                                setTimeout(() => targetVerse.classList.remove('highlighted'), 3000);
                            }
                        }, 500);
                    }, 100);
                });
                
                refsList.appendChild(refItem);
            });
            
            refsContainer.appendChild(refsList);
        }
        
        refsContainer.dataset.loaded = 'true';
        refsContainer.classList.add('visible');
        
    } catch (error) {
        console.error('Error fetching cross-references:', error);
        refsContainer.innerHTML = '<p class="error">Error loading cross-references.</p>';
    }
}
