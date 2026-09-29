"""Terminal interface for the Digital Library Management System."""
from library import Library, LOAN_DAYS, FINE_PER_DAY

MENU = """
========== DIGITAL LIBRARY MANAGEMENT SYSTEM ==========
 1. Add book               7. List members
 2. List all books         8. Issue book
 3. Search books           9. Return book
 4. Remove book           10. View active loans
 5. Register member       11. View full loan history
 0. Exit
=======================================================
"""


def ask_int(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        raise ValueError("Please enter a valid number.")


def print_books(rows):
    if not rows:
        print("No books found.")
        return
    print(f"\n{'ID':<4}{'Title':<32}{'Author':<22}{'ISBN':<16}{'Avail/Total'}")
    print("-" * 86)
    for b in rows:
        print(f"{b['id']:<4}{b['title'][:30]:<32}{b['author'][:20]:<22}"
              f"{b['isbn']:<16}{b['available']}/{b['copies']}")


def print_loans(rows):
    if not rows:
        print("No loans found.")
        return
    print(f"\n{'ID':<4}{'Book':<28}{'Member':<18}{'Issued':<12}{'Due':<12}{'Returned':<12}{'Fine'}")
    print("-" * 94)
    for l in rows:
        print(f"{l['id']:<4}{l['title'][:26]:<28}{l['member'][:16]:<18}"
              f"{l['issue_date']:<12}{l['due_date']:<12}{(l['return_date'] or '-'):<12}{l['fine']}")


def main():
    lib = Library()
    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                title = input("Title: ")
                author = input("Author: ")
                isbn = input("ISBN: ")
                copies = ask_int("Number of copies: ")
                bid = lib.add_book(title, author, isbn, copies)
                print(f"Book added with ID {bid}.")
            elif choice == "2":
                print_books(lib.list_books())
            elif choice == "3":
                print_books(lib.search_books(input("Search (title/author/ISBN): ")))
            elif choice == "4":
                lib.remove_book(ask_int("Book ID to remove: "))
                print("Book removed.")
            elif choice == "5":
                mid = lib.add_member(input("Name: "), input("Email: "))
                print(f"Member registered with ID {mid}.")
            elif choice == "7":
                rows = lib.list_members()
                if not rows:
                    print("No members yet.")
                for m in rows:
                    print(f"{m['id']:<4}{m['name']:<25}{m['email']}")
            elif choice == "8":
                loan_id, due = lib.issue_book(ask_int("Book ID: "), ask_int("Member ID: "))
                print(f"Issued! Loan ID {loan_id}. Due on {due} ({LOAN_DAYS} days).")
            elif choice == "9":
                fine = lib.return_book(ask_int("Loan ID: "))
                print("Book returned." + (f" Late fine: {fine} ({FINE_PER_DAY}/day)." if fine else " No fine."))
            elif choice == "10":
                print_loans(lib.list_loans(active_only=True))
            elif choice == "11":
                print_loans(lib.list_loans(active_only=False))
            elif choice == "0":
                print("Goodbye!")
                lib.close()
                break
            else:
                print("Invalid choice, try again.")
        except ValueError as err:
            print(f"Error: {err}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            lib.close()
            break


if __name__ == "__main__":
    main()
