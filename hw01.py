from collections import UserDict
from datetime import datetime, timedelta
import pickle
ADDRESS_BOOK_FILE = "addressbook.pkl"

def save_data(book, filename=ADDRESS_BOOK_FILE):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename=ADDRESS_BOOK_FILE):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    @Field.value.setter
    def value(self, value):
        if value:
            self._value = value
        else:
            raise ValueError('Name cannot be empty')

class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError('Phone number must contain 10 digits')
        self._value = value

class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def show_bd(self):
        return f"Date of birthday {self.birthday.value.strftime('%d.%m.%Y')}"

    def add_phone(self, phone):
        try:
            self.phones.append(Phone(phone))
        except ValueError as e:
            print(f"Error adding phone: {e}")

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True  # Повертаємо True, якщо телефон видалено
        return False  # Повертаємо False, якщо телефон не знайдено

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                try:
                    self.phones[i] = Phone(new_phone)
                    return True  # Повертаємо True, якщо телефон змінено
                except ValueError as e:
                    print(f"Error editing phone: {e}")
        return False  # Повертаємо False, якщо телефон не знайдено

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday_date):
        try:
            self.birthday = Birthday(birthday_date)
        except ValueError as e:
            print(f"Error adding birthday: {e}")
            
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def __init__(self, initial_data=None):
        # If initial_data is provided, use it; otherwise, start with an empty dictionary
        super().__init__(initial_data or {})
    
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        for user in self.data.values():
            if user.birthday == None:
                continue
            birthday = user.birthday.value
            birthday_this_year = birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            days_until_birthday = (birthday_this_year - today).days
            if 0 <= days_until_birthday <= 7:
                congratulation_date = birthday_this_year + timedelta(days=(7 - birthday_this_year.weekday()) % 7)
                upcoming_birthdays.append({"name": user.name.value, "congratulation_date": congratulation_date.strftime("%Y.%m.%d")})
        return upcoming_birthdays

def parse_input(user_input):
    # Розбирає введений користувачем рядок на команду та її аргументи.
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            return str(error)

    return inner
@input_error
def add_contact(args, book):
    # Додає новий контакт до адресної книги.
    if len(args) != 2:
        return "Invalid command format. Please use: add [name] [phone]"
    name, phone = args
    if book.find(name):
        return f"Contact with name '{name}' already exists."
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, book): 
    # Змінює номер телефону існуючого контакту.
    if len(args) != 2:
        return "Invalid command format. Please use: change [name] [new_phone]"
    name, new_phone = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    if not record.edit_phone(new_phone):  # Перевірка на успішну зміну
        return "Phone number not found for this contact."
    return "Contact updated."
@input_error
def show_phone(args, book):
    # Виводить номер телефону зазначеного контакту.
    if len(args) != 1:
        return "Invalid command format. Please use: phone [name]"
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    if not record.phones:
        return "No phone numbers found for this contact."
    return "; ".join(p.value for p in record.phones)

def show_all(book):
    # Виводить всі збережені контакти.
    if not book:
        return "No contacts saved yet."
    else:
        return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book):
    # Додає день народження до існуючого контакту.
    if len(args) != 2:
        return "Invalid command format. Please use: birthday [name] [DD.MM.YYYY]"
    name, birthday_date = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday_date)
        return f"Birthday {birthday_date} added to contact {name}"
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    # Показує день народження зазначеного контакту.
    if len(args) != 1:
        return "Invalid command format. Please use: show-birthday [name]"
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    if not record.birthday:
        return "Birthday not found for this contact."
    return record.show_bd()

def birthdays(args, book):
    # Показує контакти, у яких день народження протягом наступного тижня.
    if len(args) != 0:
        return "Invalid command format. Please use: birthdays"
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays found."
    else:
        return "\n".join(f"{record.name.value}: {record.birthday.value.strftime('%d.%m.%Y')}" for record in upcoming_birthdays)
def main():
    # Основний цикл обробки команд.
    book = AddressBook(load_data())  # Використовуємо AddressBook замість словника
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book.data.values())
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()