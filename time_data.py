from datetime import datetime, date
from time import localtime

today = date.today()
formatted_cur_date = f'{today.strftime("%a")}, {today.strftime("%b")} {today.strftime("%d")}'
current_time = datetime.now().strftime("%H:%M:%S")

print(formatted_cur_date, current_time)