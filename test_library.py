import unittest
from datetime import date, timedelta
from library import Library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.lib = Library(":memory:")
        self.book = self.lib.add_book("Clean Code", "Robert Martin", "111", 1)
        self.member = self.lib.add_member("Asha", "asha@example.com")

    def test_duplicate_isbn_rejected(self):
        with self.assertRaises(ValueError):
            self.lib.add_book("Other", "X", "111", 1)

    def test_search(self):
        self.assertEqual(len(self.lib.search_books("martin")), 1)
        self.assertEqual(len(self.lib.search_books("zzz")), 0)

    def test_issue_and_return_on_time(self):
        loan_id, _ = self.lib.issue_book(self.book, self.member)
        self.assertEqual(self.lib.list_books()[0]["available"], 0)
        self.assertEqual(self.lib.return_book(loan_id), 0)
        self.assertEqual(self.lib.list_books()[0]["available"], 1)

    def test_no_copies_left(self):
        self.lib.issue_book(self.book, self.member)
        other = self.lib.add_member("Ravi", "ravi@example.com")
        with self.assertRaises(ValueError):
            self.lib.issue_book(self.book, other)

    def test_late_fine(self):
        issued = date.today() - timedelta(days=20)
        loan_id, _ = self.lib.issue_book(self.book, self.member, today=issued)
        self.assertEqual(self.lib.return_book(loan_id), 6 * 2)  # 6 days late

    def test_cannot_remove_book_with_history(self):
        self.lib.issue_book(self.book, self.member)
        with self.assertRaises(ValueError):
            self.lib.remove_book(self.book)


if __name__ == "__main__":
    unittest.main()
