from datetime import datetime
from sqlalchemy import Column, Integer, Enum, CheckConstraint, Boolean

from .base import BaseModel
from .food import Food
from .entry import Entry
from utils import display_title, display_list




class Goal(BaseModel):
    __tablename__ = 'goals'

    field = Column(Enum('calories', 'protein', 'fat', 'carbs', name='field_enum'), nullable=False)
    value = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint('value > 0', name='value_positive'),
    )

    def __str__(self):
        return f'{self.field}: {self.value}'
    
    @property
    def details(self):
        return f'{self.field.title()} ({self.active}): {self.value}'
    
    def __repr__(self):
        return f'<Goal {self.field}: {self.value}>'
    
    def toggle(self):
        """Toggle the active status of a goal."""
        self.active = not self.active
        self.save()

    @classmethod
    def from_input(self):
        """Create a Goal object from user input."""
        field = input('Field (calories, protein, fat, carbs): ')
        value = int(input('Value: '))
        active = input('Active (y/n): ').lower() == 'y'
        return Goal(field=field, value=value, active=active)

    def how_to_reach(self, food: Food):
        """Calculate how much of a food item is needed to reach the goal."""
        food_value = getattr(food, self.field)
        quantity = (self.value * food.weight) / food_value
        return quantity

    @staticmethod
    def select():
        """Select a goal from a list."""
        print('Select a goal:', end='\n')
        goals = Goal.query().order_by(Goal.active.desc()).all()
        display_list([goal.details for goal in goals])
        print()  # Linebreak
        while True:
            choice = input('Enter the number of the goal: ')
            try:
                goal = goals[int(choice) - 1]
                return goal
            except:
                print('Invalid choice.')
                continue
    
    @staticmethod
    def display_goals():
        """Display all goals."""
        goals = Goal.query().sort_by().all()
        
        print()

    @staticmethod
    def display_progress(date=None):
        """Display the progress of all goals."""
        display_title('Goal Progress')
        if not date:
            date = datetime.now().date()
        active_goals = Goal.query().filter_by(active=True).all()
        totals = Entry.get_totals(date)
        for goal in active_goals:
            f'{goal.field.title()}: {goal.value - totals[goal.field]} remaining'

    

    @staticmethod
    def toggle_goals():
        """Toggle the active status of a goal."""
        Goal.display_goals()
        goal_id = int(input('Goal ID: '))
        goal = Goal.query().get(goal_id)
        goal.toggle()
        print(f'Goal {goal} toggled.')
        print()
