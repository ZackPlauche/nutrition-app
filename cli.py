"""Command line interface for the nutrition tracking app."""
from db import Food, Entry
from utils import pad


print(pad('Nutrition App', '=', 10))

def main():
    options = {
        'Add Entries': Entry.add_entries,
        'View Today\'s Report': Entry.show_todays_entries_and_totals,
        'Add Foods': Food.add_foods,
        'Show Foods': Food.display_foods,
        'Update Foods': Food.update_foods,
        'Delete Foods': Food.delete_foods,
        'Delete Entries': Entry.delete_entries,
        'Show Entries': Entry.show_entries,
        'Exit': exit,
    }

    while True:
        print()
        for i, (option, _) in enumerate(options.items(), start=1):
            print(f'{i}) {option}')
        print()
        choice = input('Choice: ')
        try:
            choice = int(choice)
        except ValueError:
            print('Invalid choice. Enter a number.')
        else:
            if choice in range(1, len(options) + 1):
                _, func = list(options.items())[choice - 1]
                print()
                func()
            else:
                print('Invalid choice. Enter a number.')

if __name__ == '__main__':
    main()