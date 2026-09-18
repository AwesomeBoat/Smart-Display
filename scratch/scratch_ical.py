from datetime import datetime

def test_reading_ical_format():
    with open ("scratch/sample.ics",'r') as file:
        for line in file.readlines():
            if line.startswith("SUMMARY:"):
                print(line.strip())


def regroup_ical_events(file_path):
    event_list=[]
    with open(file_path, "r") as f :
        for line in f.readlines():
            line = line.strip()
            print(line)

            if line =="BEGIN:VCALENDAR":
                continue

            if line =="END:VCALENDAR":
                return event_list

            elif line == "BEGIN:VEVENT":
                new_event = {}

            elif line == "END:VEVENT":
                event_list.append(new_event)

            else:
                key, value = line.split(":")
                new_event[key] = value


def parse_event_with_date(file_path):
    curr_and_future_events = []

    with open ("data/calendar.txt", "r") as f:
        for line in f.readlines:
            pass

date_ics = "20260918T090000"

date_in_py = datetime.strptime(date_ics, "%Y%m%dT%H%M%S")

print(datetime.now().date() >= date_in_py.date())
print(date_in_py)