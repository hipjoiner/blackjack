from datetime import datetime


home_dir = 'C:/Users/John/blackjack'


def log(txt):
    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")} {txt}')
