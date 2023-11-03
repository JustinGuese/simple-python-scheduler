import subprocess
import time
from datetime import datetime
from os import environ

from dotenv import load_dotenv

load_dotenv()
from croniter import croniter

from db import RunResult, Schedule, get_db

# first grab all schedules from db
BASE_FOLDER = environ[
    "BASE_FOLDER"
]  # the base folder of your project, where all the python scripts are. needs to be absolute path
PYTHON_PATH = environ[
    "PYTHON_PATH"
]  # the path to the python executable where requirements of your scripts are installed. unsure? type which python3 in your terminal
SLACK_ON_ERROR = environ.get("SLACK_ON_ERROR", "False") == "True"
print(f"logging to slack is {SLACK_ON_ERROR}")

PRINTLOGS = False
# tmp/bigtechmom.py

allSchedules = next(get_db()).query(Schedule).all()
print(f"found {len(allSchedules)} schedules")
allExecutions = []
today = datetime.utcnow().date()
for schedule in allSchedules:
    try:
        schd = croniter(schedule.cron_schedule, datetime.utcnow())
        next_execution = schd.get_next(datetime)
        while next_execution.date() == today:
            allExecutions.append((next_execution, schedule))
            next_execution = schd.get_next(datetime)
    except Exception as e:
        print(f"error with {schedule.bot_name}: {e}")
        continue
# sort by execution times, earliest first
allExecutions = sorted(allExecutions, key=lambda x: x[0])
print(f"found {len(allExecutions)} executions today, proceed to process.")


def send_slack_message(bot_name, errors):
    from slack_sdk.webhook import WebhookClient

    webhook = WebhookClient(environ["SLACK_WEBHOOK_URL"])
    response = webhook.send(text=f"Error {bot_name}: {errors}")
    assert response.status_code == 200
    assert response.body == "ok"


def run_script(schedule: Schedule):
    folder = schedule.folder
    file = schedule.file
    bot_name = schedule.bot_name
    # Run the script
    result = subprocess.run(
        [PYTHON_PATH, file],
        capture_output=True,
        cwd=BASE_FOLDER + folder,
        text=True,  # This will treat the output as text, for Python 3.7+ use 'universal_newlines=True'
    )

    # Capture the logs and errors
    logs = result.stdout
    errors = result.stderr
    success = result.returncode == 0

    if PRINTLOGS:
        if success:
            print("success")
            print(logs)
        else:
            print("!!failure")
            print(errors)
    if SLACK_ON_ERROR and not success:
        print("trying ot send error to slack")
        try:
            send_slack_message(bot_name, errors)
        except Exception as e:
            print(f"error sending slack message: {e}")

    # Check the return code to see if the script ran successfully
    rr = RunResult(
        bot_name=bot_name,
        success=success,
        error=str(errors) if not success else None,
        logs=str(logs),
    )
    db = next(get_db())
    db.add(rr)
    db.commit()
    return success


for timestamp, schedule in allExecutions:
    waitFor = timestamp - datetime.utcnow()
    if waitFor.total_seconds() < 0:
        print(
            f"{schedule.bot_name} is overdue with {round(waitFor.total_seconds()/60,2)} minutes"
        )
    else:
        print(
            f"waiting for {round(waitFor.total_seconds()/60,2)} minutes until next execution of {schedule.bot_name}"
        )
        time.sleep(waitFor.total_seconds())
    print(f"running {schedule.bot_name} now")

    success = run_script(schedule)
    if success:
        print("success for {schedule.bot_name}")
    else:
        print("failure for {schedule.bot_name}")
print("done")
