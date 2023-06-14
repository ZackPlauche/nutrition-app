"""Command line interface for the nutrition tracking app."""
from db.models import Food, Entry
from utils import pad


def main():
    print(pad('Nutrition App', '=', 10))
    options = {
        'Add Entry': Entry.add_entries,
        'View Today\'s Totals': Entry.show_todays_entries_and_totals,
        'Preview Entry': Entry.preview_entry,
        'Show Entries': Entry.show_entries,
        'Delete Entries': Entry.delete_entries,
        'Add Foods': Food.add_foods,
        'Show Foods': Food.display_foods,
        'Edit Foods': Food.update_foods,
        'Delete Foods': Food.delete_foods,
        'Exit': exit,
    }

    while True:
        print()
        for i, option in enumerate(options.keys(), start=1):
            print(f'{i}) {option}')
        print()
        choice = input('Choice: ')
        try:
            choice = int(choice)
        except ValueError:
            print('Invalid choice. Enter a number.')
        else:
            if choice in range(1, len(options) + 1):
                print()
                func = list(options.values())[choice - 1]
                func()
            else:
                print('Invalid choice. Enter a number.')

if __name__ == '__main__':
    main()