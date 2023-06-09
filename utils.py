def display_title(title):
    """Display a title with a line above and below."""
    print(title, '-' * len(title), sep='\n')

def display_list(list_, numbered=True, symbol=')'):
    """Display a list of items."""
    for i, item in enumerate(list_):
        string = ''
        if numbered:
            string += f'{i+1}'
        if symbol:
            string += symbol
        if len(string) > 0:
            string += ' '
        string += str(item)
        print(string)

def pad(text, symbol, length):
    """Pad a string with spaces on the left and right."""
    return f'{symbol * length} {text} {symbol * length}'


def format_number(num):
    """Remove trailining decimals or zeros from a number."""""
    if num == int(num):
        return str(int(num))  # Convert the number to an integer and return as string
    else:
        return f'{num:.2f}'  # Return the original number as string