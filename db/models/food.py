from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.exc import IntegrityError

from .base import BaseModel
from settings import NUTRITION_TEMPLATE, TOTALS_TEMPLATE
from utils import format_number, display_title, display_list
    
class Food(BaseModel):
    """A food item that will be selected to calculate nutritional value in a meal."""
    __tablename__ = 'food'

    name = Column(String(50), nullable=False, unique=True)
    weight = Column(Integer, nullable=True, default=100)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    source = Column(String(50), nullable=True, default=None)

    def __str__(self):
        return NUTRITION_TEMPLATE.format(
            food_name=self.name,
            weight=format_number(self.weight),
            calories=format_number(self.calories),
            protein=format_number(self.protein),
            fat=format_number(self.fat),
            carbs=format_number(self.carbs),
        )

    def __repr__(self):
        return f'<Food id={self.id} name={self.name}>'

    @classmethod
    def from_input(self):
        """Create a Food object from user input."""
        name = input('Name: ')
        weight = float(input('Weight (g): '))
        calories = float(input('Calories: '))
        protein = float(input('Protein: '))
        fat = float(input('Fat: '))
        carbs = float(input('Carbs: '))
        source = input('Source (Press enter to skip): ')
        return Food(name=name, calories=calories, protein=protein, fat=fat, carbs=carbs, weight=weight, source=source)
    
    def calculate(self, weight):
        """Calculate the nutritional value of a food item based on the weight given with respect to the food's weight."""
        factor = weight / self.weight
        return {
            'calories': self.calories * factor,
            'protein': self.protein * factor,
            'fat': self.fat * factor,
            'carbs': self.carbs * factor,
        }

    @staticmethod
    def select():
        """Select a food item from the database."""
        print('Select a food item:')
        food_list = Food.query().order_by(Food.name).all()
        display_list(food_list)
        print()
        while True:
            choice = input('Enter the number of the food item (or type "add" to add a new one): ')
            if choice == 'add':
                print()
                food = Food.add_food()
                break
            try:
                food = food_list[int(choice) - 1]
                break
            except IndexError:
                print('Invalid choice')
        return food

    @staticmethod
    def add_food():
        """Add a food item to the database."""
        display_title('Adding Food Item')
        food = Food.from_input()
        food.save()
        print(f'Added {food}')
        return food

    @staticmethod
    def add_foods():
        """Add a food item or multiple to the database."""
        display_title('Adding Food Items')
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
        display_list(Food.query().order_by(Food.name).all(), symbol='.')

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
            for field in ['name', 'weight', 'calories', 'protein', 'fat', 'carbs']:
                value = input(f'{field.capitalize()} ({getattr(food, field)}): ')
                if value:
                    setattr(food, field, value)
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
        for food in to_delete:
            try:
                food.delete()
                print(f'Deleted food: {food.name}')
            except IntegrityError as e:
                if 'NOT NULL constraint field' in str(e):
                    print(f'Cannot delete food {food.name}: it is referenced by an entry. Skipping...')
                else:
                    raise e
