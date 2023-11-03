from croniter import croniter

from db import Schedule, get_db

botname = input("Bot name: ")
schedule = input("Cron schedule: ")
if not croniter.is_valid(schedule):
    raise ValueError("Invalid cron schedule: " + schedule)
folder = input("Folder: ")
file = input("File: ")

schedule = Schedule(bot_name=botname, cron_schedule=schedule, folder=folder, file=file)
db = next(get_db())
db.add(schedule)
db.commit()
print("success")
