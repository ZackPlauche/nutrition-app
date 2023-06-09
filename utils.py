def display_title(title):
    """Display a title with a line above and below."""
    print(title, '-' * len(title), sep='\n')

def display_list(list_, symbol=')'):
    """Display a list of items."""
    for i, item in enumerate(list_):
        print(f'{i+1}{symbol} {item}')

def pad(text, symbol, length):
    """Pad a string with spaces on the left and right."""
    return f'{symbol * length} {text} {symbol * length}'