from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Float
from sqlalchemy.orm import relationship

from .base import BaseModel
from utils import format_number, display_title, display_list
from settings import NUTRITION_TEMPLATE, TOTALS_TEMPLATE

from .food import Food


class Entry(BaseModel):
    __tablename__ = 'entries'

    def __init__(self, food, weight, date, submitted_at=datetime.now()):
        self.weight = weight
        self.food = food
        self.date = date
        self.submitted_at = submitted_at
        self.calculate()

    weight = Column(Float, nullable=False, comment="in grams")
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    submitted_at = Column(DateTime, nullable=False)

    food_id = Column(Integer, ForeignKey('food.id'), nullable=False)
    food = relationship('Food', backref='entries')

    def __str__(self):
        return NUTRITION_TEMPLATE.format(
            food_name=self.food.name,
            weight=format_number(self.weight),
            calories=format_number(self.calories),
            protein=format_number(self.protein),
            fat=format_number(self.fat),
            carbs=format_number(self.carbs),
        )

    @classmethod
    def from_input(cls, date=None):
        """Create an Entry object from user input."""
        food = Food.select()
        print()
        print(f'Food: {food.name}')
        weight = float(input('Weight (g): '))
        if not date:
            date_str = input(f'Date (YYYY-MM-DD) (Press enter for {datetime.now().date()}): ')
            if not date_str:
                date = datetime.now().date()
            else:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return cls(food=food, weight=weight, date=date)

    def calculate(self):
        """Calculate the nutritional value of a food item based on the weight given."""
        data = self.food.calculate(self.weight)
        self.calories = data['calories']
        self.protein = data['protein']
        self.fat = data['fat']
        self.carbs = data['carbs']

    def save(self):
        if not self.submitted_at:
            self.submitted_at = datetime.now()
        return super().save()
    
    @staticmethod
    def delete_entries(date=None):
        """Select an entry to delete, optionally multiple entries with comma separated values, and by date."""
        entries = Entry.get_all()
        if date:
            entries = [entry for entry in entries if entry.date == date]
        display_title('Select an entry to delete:')
        display_list(entries)
        input_str = input('Enter the number(s) of the entry to delete (comma separated): ')
        if not input_str:
            print('No entries selected.')
            return
        to_delete = [entries[int(i)-1] for i in input_str.split(',')]
        for entry in to_delete:
            entry.delete()

    @staticmethod
    def preview_entry():
        """Preview an entry before saving."""
        display_title('Preview Entry')
        entry = Entry.from_input()
        print(entry)
        if input('Would you like to save this entry? (y/n): ').lower() == 'y':
            entry.save()

    @staticmethod
    def show_entries(date=None):
        """Show entries for the given date."""
        entries = Entry.query()
        if entries.count() == 0:
            print('No entries to show.')
            return
        if not date:
            while True:
                date = Entry.select_date()
                entries = entries.filter(Entry.date == date)
                print()
                break
        else:
            entries = entries.filter(Entry.date == date)
        entries = entries.order_by(Entry.submitted_at.asc()).all()
        display_title(f'Entries for {date}')
        if len(entries) == 0:
            print('No entries to show.')
            return
        display_list(entries, symbol='.')

    @staticmethod
    def select_date() -> date:
        """Select a date to show entries for."""
        available_dates = Entry.get_available_dates()
        display_title('Select a date to show entries for:')
        display_list(available_dates)
        print()
        while True:
            choice = input('Enter the number of the date (Press Enter for today): ')
            if not choice:
                return datetime.now().date()
            elif choice not in [str(i) for i in range(1, len(available_dates)+1)]:
                print('Invalid choice.')
                continue
            else: 
                return datetime.strptime(available_dates[int(choice)-1], '%Y-%m-%d').date()

    @staticmethod
    def get_available_dates():
        available_dates = Entry.query().with_entities(Entry.date).distinct().all()
        available_dates = [date[0] for date in available_dates]
        return available_dates

    @staticmethod
    def get_totals(date=None):
        entries = Entry.get_all()
        if date:
            entries = [entry for entry in entries if entry.date == date]
        totals = {
            'calories': sum([entry.calories for entry in entries]),
            'protein': sum([entry.protein for entry in entries]),
            'fat': sum([entry.fat for entry in entries]),
            'carbs': sum([entry.carbs for entry in entries]),
        }
        return totals

    @staticmethod
    def show_totals(date=None):
        """Show the total nutritional value for today."""
        totals = Entry.get_totals(date)
        print(TOTALS_TEMPLATE.format(
            calories=format_number(totals['calories']),
            protein=format_number(totals['protein']),
            fat=format_number(totals['fat']),
            carbs=format_number(totals['carbs']),
        ))

    @staticmethod
    def show_entries_and_totals(date: datetime.date =None):
        """Show all entries for a specific day and the total nutritional value."""
        if not date:
            date = datetime.strptime(input('Date (YYYY-MM-DD): '), '%Y-%m-%d').date()
        Entry.show_entries(date)
        print()
        Entry.show_totals(date)

    @staticmethod
    def show_todays_entries_and_totals():
        """Show all entries for today and the total nutritional value."""
        today = datetime.now().date()
        Entry.show_entries_and_totals(today)

    @staticmethod
    def add_entries():
        """Add entries to the database."""
        while True:
            entry = Entry.from_input()
            entry.save()
            print('Entry added.')
            if input('Add another entry? (y/n): ').lower() != 'y':
                break
