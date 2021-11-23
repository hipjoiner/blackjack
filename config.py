from datetime import datetime


cache = 'C:/Users/John/OneDrive/blackjack'
data = 'C:/Users/John/blackjack'


def log(txt):
    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")} {txt}')
