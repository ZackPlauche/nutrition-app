from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Date, Float
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, DeclarativeMeta, scoped_session
from sqlalchemy.exc import IntegrityError
from utils import display_title, display_list

NUTRITION_TEMPLATE = '{food_name} ({weight}g): {calories} cals | {protein}g protein | {fat}g fat | {carbs}g carbs'

engine = create_engine('sqlite:///db.sqlite3')

Session = scoped_session(sessionmaker(bind=engine))
Base: DeclarativeMeta = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
    
    def save(self):
        """Save the object to the database."""
        session = Session()
        try:
            session.add(self)
            session.commit()
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                print(f'{self.__class__.__name__} with that name already exists')
                session.rollback()
            else:
                raise e
        return self
    
    def is_detached(self):
        """Check if the object is detached from a session."""
        session = Session.object_session(self)
        return session is None or session.is_modified(self)

    def delete(self, commit=True):
        """Delete the object from the database."""
        session = Session()
        session.delete(self)
        session.commit()


    @classmethod
    def _validate_kwargs(cls, **kwargs):
        """Validate that key word arguments are valid column names."""
        for key in kwargs.keys():
            if not hasattr(cls, key):
                raise ValueError(f'{cls.__class__.__name__} has no attribute {key}')

    @classmethod
    def get(cls, **kwargs):
        """Get an object of this type by keyword arguments."""
        cls._validate_kwargs(**kwargs)
        session = Session()
        obj = session.query(cls).filter_by(**kwargs).first()
        return obj
    
    @classmethod
    def get_all(cls):
        """Get all objects of this type."""
        session = Session()
        objs = session.query(cls).all()
        return objs
    
    @classmethod
    def query(cls):
        """Get a query object for this type."""
        session = Session()
        return session.query(cls)

    
class Food(BaseModel):
    __tablename__ = 'food'

    name = Column(String(50), nullable=False, unique=True)
    calories = Column(Float, nullable=False, comment="per 100g")
    protein = Column(Float, nullable=False, comment="per 100g")
    fat = Column(Float, nullable=False, comment="per 100g")
    carbs = Column(Float, nullable=False, comment="per 100g")
    source = Column(String(50), nullable=True, default=None)

    def __str__(self):
        return NUTRITION_TEMPLATE.format(
            food_name=self.name,
            weight=100,
            calories=self.calories,
            protein=self.protein,
            fat=self.fat,
            carbs=self.carbs,
        )

    def __repr__(self):
        return f'<Food id={self.id} name={self.name}>'

    @classmethod
    def from_input(self):
        """Create a Food object from user input."""
        name = input('Name: ')
        calories = float(input('Calories: '))
        protein = float(input('Protein: '))
        fat = float(input('Fat: '))
        carbs = float(input('Carbs: '))
        return Food(name=name, calories=calories, protein=protein, fat=fat, carbs=carbs)
    
    def calculate(self, weight):
        """Calculate the nutritional value of a food item based on the weight given."""
        return {
            'calories': self.calories * weight / 100,
            'protein': self.protein * weight / 100,
            'fat': self.fat * weight / 100,
            'carbs': self.carbs * weight / 100,
        }

    @staticmethod
    def select():
        """Select a food item from the database."""
        print('Select a food item:')
        display_list(Food.get_all())
        return Food.get(id=int(input('Enter the number of the food item: ')))

    @staticmethod
    def add_foods():
        """Add a food item or multiple to the database."""
        while True:
            food = Food.from_input()
            food.save()
            print(f'Added {food}')
            if input('Add another? (y/n): ') != 'y':
                break

    @staticmethod
    def display_foods():
        """Display all food items in the database."""
        display_title('Food Items')
        for food in Food.get_all():
            print(food)

    @staticmethod
    def update_foods():
        """Update a food item or multiple in the database."""
        display_title('Update Food Items')
        while True:
            food = Food.get_all()
            display_list(food)
            choice = input('Enter the number of the food item to update: ')
            if not choice:
                break
            food = food[int(choice)-1]
            print(f'Updating {food}')
            food.name = input('Name: ')
            food.calories = float(input('Calories: '))
            food.protein = float(input('Protein: '))
            food.fat = float(input('Fat: '))
            food.carbs = float(input('Carbs: '))
            food.save()
            print(f'Updated {food}')
            if input('Update another? (y/n): ') != 'y':
                break


    @staticmethod
    def delete_foods():
        """Delete a food item or multiple from the database."""
        display_title('Delete Food Items')
        food = Food.get_all()
        display_list(food)
        input_str = input('Enter the number(s) of the food(s) to delete (comma separated): ')
        if not input_str:
            print('No foods selected.')
            return
        to_delete = [food[int(i)-1] for i in input_str.split(',')]
        for entry in to_delete:
            entry.delete()


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
            weight=self.weight,
            calories=self.calories,
            protein=self.protein,
            fat=self.fat,
            carbs=self.carbs,
        )

    @classmethod
    def from_input(cls, date=None):
        """Create an Entry object from user input."""
        food = Food.select()
        weight = float(input('Weight (g): '))
        if not date:
            date = datetime.strptime(input('Date (YYYY-MM-DD): '), '%Y-%m-%d').date()
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
    def show_entries(date=None):
        """Show all entries for today."""
        entries = Entry.query()
        if not date:
            while True:
                date = Entry.select_date()
                if not date:
                    print('No date selected. Please select a date.')
                    continue
                entries = entries.filter(Entry.date == date)
                print()
                break
        entries = entries.order_by(Entry.submitted_at.desc()).all()
        display_title(f'Entries for {date}')
        display_list(entries, symbol='.')

    @staticmethod
    def select_date():
        available_dates = Entry.query().with_entities(Entry.date).distinct().all()
        available_dates = [date[0] for date in available_dates]
        display_title('Select a date:')
        display_list(available_dates)
        date = input('Enter the number of the date to select: ')
        if not date:
            return None
        return available_dates[int(date)-1]

    @staticmethod
    def show_totals(date=None):
        """Show the total nutritional value for today."""
        entries = Entry.get_all()
        if date:
            entries = [entry for entry in entries if entry.date == date]
        totals = {
            'calories': sum([entry.calories for entry in entries]),
            'protein': sum([entry.protein for entry in entries]),
            'fat': sum([entry.fat for entry in entries]),
            'carbs': sum([entry.carbs for entry in entries]),
        }
        print('TOTALS: {calories} cals | {protein}g pro | {fat}g fat | {carbs}g carbs'.format(**totals))

    @staticmethod
    def show_entries_and_totals(date=None):
        """Show all entries for a specific day and the total nutritional value."""
        if not date:
            date = datetime.strptime(input('Date (YYYY-MM-DD): '), '%Y-%m-%d').date()
        Entry.show_entries(date)
        Entry.show_totals(date)

    @staticmethod
    def show_todays_entries_and_totals():
        """Show all entries for today and the total nutritional value."""
        today = datetime.now().date()
        Entry.show_entries(today)
        Entry.show_totals(today)

    @staticmethod
    def add_entries():
        """Add entries to the database."""
        while True:
            entry = Entry.from_input()
            entry.save()
            print('Entry added.')
            if input('Add another entry? (y/n): ').lower() != 'y':
                break



Base.metadata.create_all(engine)

def show_todays_entries_and_totals():
    """Show all entries for today and the total nutritional value."""
    today = datetime.now().date()
    entries = Entry.get_all()
    entries = [entry for entry in entries if entry.date == today]
    for entry in entries:
        print(entry)
    totals = {
        'calories': sum([entry.calories for entry in entries]),
        'protein': sum([entry.protein for entry in entries]),
        'fat': sum([entry.fat for entry in entries]),
        'carbs': sum([entry.carbs for entry in entries]),
    }
    print(NUTRITION_TEMPLATE.format(
        food_name='TOTAL',
        weight='N/A',
        calories=totals['calories'],
        protein=totals['protein'],
        fat=totals['fat'],
        carbs=totals['carbs'],
    ))