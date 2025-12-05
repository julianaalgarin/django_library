
class LoanSelectionItem:
    def __init__(self, book_id, title, quantity=1):
        self.book_id = book_id
        self.title = title
        self.quantity = quantity

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "quantity": self.quantity,
        }

    @staticmethod
    def from_dict(data):
        return LoanSelectionItem(
            book_id=data["book_id"],
            title=data["title"],
            quantity=data["quantity"]
        )

class LoanSelection:
    def __init__(self):
        self.items = {}

    def add_book(self, book, quantity=1):
        if book.id in self.items:
            self.items[book.id].quantity += quantity
        else:
            self.items[book.id] = LoanSelectionItem(book.id, book.title, quantity)

    def remove_book(self, book_id):
        self.items.pop(book_id, None)

    def clear(self):
        self.items = {}

    def __len__(self):
        return sum(item.quantity for item in self.items.values())

    def to_dict(self):
        return {bid: item.to_dict() for bid, item in self.items.items()}

    @staticmethod
    def from_dict(data):
        sel = LoanSelection()
        for item_dict in data.values():
            item = LoanSelectionItem.from_dict(item_dict)
            sel.items[item.book_id] = item
        return sel    