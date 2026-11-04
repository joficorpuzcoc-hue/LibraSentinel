# ==========================================================
#  PROJECT: LibraSentinel - A Library Borrowing and Tracking System
#  COURSE:  ITE 260 - Computer Programming 1
#  SCHOOL:  PHINMA - Cagayan de Oro College
#  DATE:    September 18, 2026
# ==========================================================
from datetime import date, timedelta

# ---------------------- CONSTANTS -------------------------
LOAN_DAYS = 7        # how many days a book can be borrowed
MAX_LOANS = 3        # max books one borrower can hold at once
DATE_FORMAT = "%b %d, %Y"

# ---------------------- DATA STORAGE ----------------------
# Lists that store system data in memory
books = []          # [book_id, title, author, category, status]
borrowers = []      # [borrower_id, name, role]
transactions = []   # [trans_id, book_id, borrower_id, date_borrowed, due_date, date_returned]

# Index names so the code is easier to read than book[3], trans[5], etc.
B_ID, B_TITLE, B_AUTHOR, B_CATEGORY, B_STATUS = 0, 1, 2, 3, 4
U_ID, U_NAME, U_ROLE = 0, 1, 2
T_ID, T_BOOK, T_BORROWER, T_BORROWED, T_DUE, T_RETURNED = 0, 1, 2, 3, 4, 5


# ==========================================================
#  PART 1: DATA / LOGIC FUNCTIONS (no input(), no menus)
#  These take parameters and RETURN results.
# ==========================================================
def find_book(book_id):
    """Return the book record with this ID, or None if not found."""
    for book in books:
        if book[B_ID] == book_id:
            return book
    return None


def find_borrower(borrower_id):
    """Return the borrower record with this ID, or None if not found."""
    for person in borrowers:
        if person[U_ID] == borrower_id:
            return person
    return None


def count_active_loans(borrower_id):
    """Count how many books this borrower has not yet returned."""
    count = 0
    for trans in transactions:
        if trans[T_BORROWER] == borrower_id and trans[T_RETURNED] is None:
            count += 1
    return count


def add_book(book_id, title, author, category):
    """Register a new book. Returns (success, message)."""
    if find_book(book_id) is not None:
        return False, f"Book ID {book_id} already exists!"
    books.append([book_id, title, author, category, "Available"])
    return True, f"Book added: '{title}' by {author} (ID: {book_id})"


def edit_book(book_id, new_title, new_author, new_category):
    """Update a book's details. A blank value keeps the old one."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found."
    if new_title != "":
        book[B_TITLE] = new_title
    if new_author != "":
        book[B_AUTHOR] = new_author
    if new_category != "":
        book[B_CATEGORY] = new_category
    return True, f"Book {book_id} updated."


def search_books(keyword):
    """Return a list of books whose ID, title, author, or category match."""
    keyword = keyword.lower()
    results = []
    for book in books:
        if (keyword in book[B_ID].lower()
                or keyword in book[B_TITLE].lower()
                or keyword in book[B_AUTHOR].lower()
                or keyword in book[B_CATEGORY].lower()):
            results.append(book)
    return results


def sort_books(field_index):
    """Return a sorted COPY of the books list by the given field index."""
    # key=lambda tells sorted() which item of each record to compare
    return sorted(books, key=lambda book: book[field_index].lower())


def register_borrower(borrower_id, name, role):
    """Register a student/staff borrower. Returns (success, message)."""
    if find_borrower(borrower_id) is not None:
        return False, f"Borrower ID {borrower_id} is already registered."
    borrowers.append([borrower_id, name, role])
    return True, f"Registered {role}: {name} (ID: {borrower_id})"


def borrow_book(book_id, borrower_id, today):
    """Process a borrowing. Returns (success, message)."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found in system."
    if find_borrower(borrower_id) is None:
        return False, f"Borrower ID {borrower_id} is not registered."
    if book[B_STATUS] != "Available":
        return False, f"Book ID {book_id} is currently borrowed."
    if count_active_loans(borrower_id) >= MAX_LOANS:
        return False, f"Borrower {borrower_id} already has {MAX_LOANS} books (limit reached)."

    due_date = today + timedelta(days=LOAN_DAYS)      # arithmetic on dates
    book[B_STATUS] = "Borrowed"
    transactions.append([len(transactions) + 1, book_id, borrower_id,
                         today, due_date, None])
    return True, (f"Book '{book[B_TITLE]}' borrowed by {borrower_id}. "
                  f"Due: {due_date.strftime(DATE_FORMAT)}")


def return_book(book_id, today):
    """Process a return. Returns (success, message)."""
    book = find_book(book_id)
    if book is None:
        return False, f"Book ID {book_id} not found."
    if book[B_STATUS] != "Borrowed":
        return False, f"Book ID {book_id} is not borrowed."

    for trans in transactions:
        if trans[T_BOOK] == book_id and trans[T_RETURNED] is None:
            trans[T_RETURNED] = today
            book[B_STATUS] = "Available"
            days_late = (today - trans[T_DUE]).days    # arithmetic on dates
            if days_late > 0:
                return True, f"Book {book_id} returned {days_late} day(s) LATE. Now Available."
            return True, f"Book {book_id} returned on time. Now Available."

    # Status said "Borrowed" but no open transaction exists (data mismatch)
    return False, f"No open borrowing record found for Book ID {book_id}."


def get_active_loans():
    """Return all transactions that have not been returned yet."""
    active = []
    for trans in transactions:
        if trans[T_RETURNED] is None:
            active.append(trans)
    return active


def get_overdue_loans(today):
    """Return active transactions whose due date has already passed."""
    overdue = []
    for trans in get_active_loans():
        if trans[T_DUE] < today:
            overdue.append(trans)
    return overdue


# ==========================================================
#  PART 2: INPUT HELPERS (validation)
# ==========================================================
def read_text(prompt):
    """Keep asking until the user types something that is not blank."""
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("[INVALID] This field cannot be empty.")


def read_id(prompt):
    """Read a non-empty ID with no spaces, converted to UPPERCASE."""
    while True:
        value = read_text(prompt).upper()
        if " " in value:
            print("[INVALID] IDs cannot contain spaces.")
        else:
            return value


def read_menu_choice(low, high):
    """Read a number between low and high (inclusive)."""
    while True:
        choice = input(f"Enter your choice ({low}-{high}): ").strip()
        if choice.isdigit() and low <= int(choice) <= high:
            return int(choice)
        print(f"[INVALID] Please enter a number from {low} to {high}.")


def fit(text, width):
    """Cut text so long values do not break the table columns."""
    text = str(text)
    if len(text) > width:
        return text[:width - 2] + ".."
    return text


# ==========================================================
#  PART 3: DISPLAY FUNCTIONS (printing only)
# ==========================================================
def show_books(book_list, heading):
    """Print a table of books."""
    line = "=" * 82
    print("\n" + line)
    print(heading)
    print(line)
    print(f"{'BOOK ID':<10} | {'TITLE':<26} | {'AUTHOR':<18} | {'CATEGORY':<12} | {'STATUS':<9}")
    print("-" * 82)
    if not book_list:
        print("No books to show.")
    for book in book_list:
        print(f"{fit(book[B_ID], 10):<10} | {fit(book[B_TITLE], 26):<26} | "
              f"{fit(book[B_AUTHOR], 18):<18} | {fit(book[B_CATEGORY], 12):<12} | "
              f"{book[B_STATUS]:<9}")
    print(line)


def show_borrowers():
    """Print all registered borrowers."""
    line = "=" * 52
    print("\n" + line)
    print("REGISTERED BORROWERS")
    print(line)
    print(f"{'ID':<14} | {'NAME':<22} | {'ROLE':<10}")
    print("-" * 52)
    if not borrowers:
        print("No borrowers registered yet.")
    for person in borrowers:
        print(f"{fit(person[U_ID], 14):<14} | {fit(person[U_NAME], 22):<22} | {person[U_ROLE]:<10}")
    print(line)


def show_transactions(trans_list, heading):
    """Print a table of transactions."""
    line = "=" * 84
    print("\n" + line)
    print(heading)
    print(line)
    print(f"{'#':<4} | {'BOOK ID':<10} | {'BORROWER':<12} | {'BORROWED':<12} | {'DUE':<12} | {'RETURNED':<12}")
    print("-" * 84)
    if not trans_list:
        print("No records to show.")
    for t in trans_list:
        returned = t[T_RETURNED].strftime(DATE_FORMAT) if t[T_RETURNED] else "Not yet"
        print(f"{t[T_ID]:<4} | {fit(t[T_BOOK], 10):<10} | {fit(t[T_BORROWER], 12):<12} | "
              f"{t[T_BORROWED].strftime(DATE_FORMAT):<12} | "
              f"{t[T_DUE].strftime(DATE_FORMAT):<12} | {returned:<12}")
    print(line)


def show_overdue_notices(overdue_list, today):
    """Print overdue notices with days late."""
    line = "=" * 70
    print("\n" + line)
    print("OVERDUE NOTICES")
    print(line)
    if not overdue_list:
        print("No overdue books. Great!")
    for t in overdue_list:
        days_late = (today - t[T_DUE]).days
        book = find_book(t[T_BOOK])
        title = book[B_TITLE] if book else "Unknown"
        print(f"Borrower {t[T_BORROWER]}: '{fit(title, 25)}' (ID {t[T_BOOK]}) "
              f"is {days_late} day(s) overdue.")
    print(line)


def print_result(result):
    """Print a (success, message) pair with the right tag."""
    success, message = result
    tag = "[SUCCESS]" if success else "[ERROR]"
    print(f"\n{tag} {message}")


# ==========================================================
#  PART 4: MENU ACTIONS (mix input + logic + display)
# ==========================================================
def menu_add_book():
    book_id = read_id("Enter Book ID: ")
    title = read_text("Enter Book Title: ")
    author = read_text("Enter Author: ")
    category = read_text("Enter Category: ")
    print_result(add_book(book_id, title, author, category))


def menu_edit_book():
    book_id = read_id("Enter Book ID to edit: ")
    if find_book(book_id) is None:
        print(f"\n[ERROR] Book ID {book_id} not found.")
        return
    print("Leave a field blank to keep the current value.")
    new_title = input("New Title: ").strip()
    new_author = input("New Author: ").strip()
    new_category = input("New Category: ").strip()
    print_result(edit_book(book_id, new_title, new_author, new_category))


def menu_search_book():
    keyword = read_text("Search by Title / Author / ID / Category: ")
    show_books(search_books(keyword), f"SEARCH RESULTS FOR '{keyword}'")


def menu_sort_books():
    print("\nSort by: [1] Title  [2] Author  [3] Category  [4] Availability")
    choice = read_menu_choice(1, 4)
    field = {1: B_TITLE, 2: B_AUTHOR, 3: B_CATEGORY, 4: B_STATUS}[choice]
    show_books(sort_books(field), "BOOKS (SORTED)")


def menu_register_borrower():
    borrower_id = read_id("Enter Student/Staff ID: ")
    name = read_text("Enter Full Name: ")
    print("Role: [1] Student  [2] Teacher/Staff")
    role = "Student" if read_menu_choice(1, 2) == 1 else "Staff"
    print_result(register_borrower(borrower_id, name, role))


def menu_borrow_book():
    book_id = read_id("Enter Book ID to borrow: ")
    borrower_id = read_id("Enter Borrower ID: ")
    print_result(borrow_book(book_id, borrower_id, date.today()))


def menu_return_book():
    book_id = read_id("Enter Book ID to return: ")
    print_result(return_book(book_id, date.today()))


# ==========================================================
#  PART 5: MAIN MENU LOOP
# ==========================================================
def print_menu():
    print("\n" + "=" * 34)
    print("        MAIN MENU")
    print("=" * 34)
    print("[1]  Add New Book")
    print("[2]  Edit Book")
    print("[3]  Search Book")
    print("[4]  View All Books (Sorted)")
    print("[5]  Register Borrower")
    print("[6]  Borrow Book")
    print("[7]  Return Book")
    print("[8]  View Borrowed Books")
    print("[9]  View Overdue Notices")
    print("[10] View Transaction History")
    print("[11] View Borrowers")
    print("[12] Exit")
    print("=" * 34)


def main():
    print("=" * 50)
    print("   LIBRASENTINEL: LIBRARY MANAGEMENT SYSTEM")
    print("     PHINMA - Cagayan de Oro College")
    print("=" * 50)

    running = True
    while running:
        print_menu()
        choice = read_menu_choice(1, 12)

        if choice == 1:
            menu_add_book()
        elif choice == 2:
            menu_edit_book()
        elif choice == 3:
            menu_search_book()
        elif choice == 4:
            menu_sort_books()
        elif choice == 5:
            menu_register_borrower()
        elif choice == 6:
            menu_borrow_book()
        elif choice == 7:
            menu_return_book()
        elif choice == 8:
            show_transactions(get_active_loans(), "CURRENTLY BORROWED BOOKS")
        elif choice == 9:
            today = date.today()
            show_overdue_notices(get_overdue_loans(today), today)
        elif choice == 10:
            show_transactions(transactions, "TRANSACTION HISTORY")
        elif choice == 11:
            show_borrowers()
        else:
            print("\nExiting system. Thank you!")
            running = False


# ---------------------- RUN PROGRAM -----------------------
if __name__ == "__main__":
    main()
