import pickle
from collections import UserDict
from datetime import datetime

from birthday import get_birthdays_per_week


# CUSTOM ERRORS


class BirthdayError(Exception):
    pass


class DateError(Exception):
    pass


class TheNameError(Exception):
    pass


class PhoneIndexError(Exception):
    pass


class PhoneError(Exception):
    pass


class RecordError(Exception):
    pass


# CLASSES


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, name):
        if len(str(name)) < 3:
            raise TheNameError()
        self.__value = name


class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, phone):
        if not str(phone).isdecimal():
            raise PhoneError()
        elif len(str(phone)) != 10:
            raise PhoneError()
        else:
            self.__value = phone


class Birthday(Field):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, birthday):
        try:
            birth = datetime.strptime(birthday, "%d.%m.%Y").date()
        except ValueError as exc:
            raise BirthdayError() from exc
        if not 0 < (datetime.today().date() - birth).days < 100 * 365:
            raise DateError()
        self._value = datetime.strptime(birthday, "%d.%m.%Y").date()

    def __str__(self):
        return str(self.value.strftime("%d.%m.%Y"))


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def delete_phone(self, phone_number):
        index = self.find_phone(phone_number)
        self.phones.pop(index)

    def edit_phone(self, phone_numbers):
        index = self.find_phone(phone_numbers[0])
        self.phones[index] = Phone(phone_numbers[1])

    def find_phone(self, phone_number):
        index = 0
        for item in self.phones:
            if item.value == phone_number:
                return index
            index += 1
        raise PhoneIndexError()

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        numbers = "; ".join(p.value for p in self.phones) if self.phones else None
        return f"Contact name: {self.name.value}, phones: {numbers}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        if str(record.name) in self.data.keys():
            raise RecordError()
        self.data[str(record.name)] = record

    def find(self, name):
        return self.data[name]

    def delete(self, name):
        self.data.pop(name)


# INPUT ERRORS HANDLER


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError, TypeError) as err:
            if isinstance(err, KeyError):
                return "Record not found."
            elif isinstance(err, TypeError):
                return "Enter record name."
            elif isinstance(err, ValueError):
                return "Enter record name and phone number."
            elif isinstance(err, IndexError):
                return "Enter record name."
        except (
            TheNameError,
            PhoneIndexError,
            PhoneError,
            RecordError,
            BirthdayError,
            DateError,
        ) as custom_err:
            if isinstance(custom_err, TheNameError):
                return "Name must have min. 3 characters."
            elif isinstance(custom_err, PhoneIndexError):
                return "No such phone."
            elif isinstance(custom_err, PhoneError):
                return "Phone must have 10 digits."
            elif isinstance(custom_err, RecordError):
                return "Contact with this name already exists."
            elif isinstance(custom_err, BirthdayError):
                return "Birthday must have in DD.MM.YYYY format."
            elif isinstance(custom_err, DateError):
                return "Birthday must be in the past and no more than 100 years."

    return inner


# FUNCTIONS


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def get_command(input):
    commands = {
        "add": add_record,
        "all": show_all,
        "hello": greeting,
        "phone": find_phone,
        "delete": delete_record,
        "add_phone": add_phone,
        "change": edit_phone,
        "find": find_record,
        "birthdays": get_birthdays_per_week,
        "add_birthday": add_birthday,
        "show_birthday": show_birthday,
    }

    command = commands.get(input)
    if not command:
        return invalid_command
    return command


@input_error
def add_record(book, *args):
    name, *phone_number = args
    record = Record(Name(name))
    if phone_number:
        record.add_phone(phone_number[0])
    book.add_record(record)
    return "Contact added."


@input_error
def add_phone(book, *args):
    name, phone_number = args
    record = book.find(name)
    record.add_phone(phone_number)
    return f"Phone added."


@input_error
def add_birthday(book, *args):
    name, *birthday = args
    record = book.find(name)
    record.add_birthday(birthday[0])
    return f"Birthday added."


@input_error
def edit_phone(book, *args):
    name, *phone_numbers = args
    record = book.find(name)
    record.edit_phone(phone_numbers)
    return f"Phone updated."


@input_error
def find_record(book, *args):
    name = args[0]
    return book.find(name)


def greeting(*_):
    return "How can I help you?"


def invalid_command(*_):
    return "Invalid command."


@input_error
def delete_record(book, *args):
    name = args[0]
    book.delete(name)
    return f"Record deleted."


@input_error
def find_phone(book, *args):
    name, phone_number = args
    record = book.find(name)
    index = record.find_phone(phone_number)
    return f"{record.name}: {record.phones[index]}."


def show_all(book):
    if len(book):
        result = "All contacts: "
        for _, record in book.items():
            result += f"\n{record}"
        return result
    return "No contacts."


@input_error
def show_birthday(book, *args):
    name = args[0]
    record = book.find(name)
    return f"{record.name}: {record.birthday}."


def main():
    book = load_address_book()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_or_not = input("Save address book ('Y' or 'N')? ").lower()
            if save_or_not == "y":
                save_address_book(book)
                print("Address book saved.\n Good bye!")
                break
            print("Good bye!")
            break

        print(get_command(command)(book, *args))


# ADDITIONAL TASK


def load_address_book():
    book = AddressBook()
    try:
        with open("book.dat", "rb") as file:
            book.data = pickle.load(file)
    except FileNotFoundError:
        pass
    return book


def save_address_book(book):
    if book.data:
        with open("book.dat", "wb") as file:
            pickle.dump(book.data, file)


if __name__ == "__main__":
    main()
