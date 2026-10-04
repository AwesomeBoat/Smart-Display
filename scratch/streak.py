from datetime import datetime, timedelta
def streak(dates: list[datetime]):
    if not dates:
        return 0

    # convert into date objects and get rid of dulicates
    unique_dates = {d.date() if isinstance(d, datetime) else d for d in dates}

    # Sort dates
    ordered_dates = sorted(list(unique_dates))

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # if the last day isn't today or yesterday, no streak
    last_date = ordered_dates[-1]
    if last_date != today and last_date != yesterday:
        return 0

    # Count streak
    streak_count = 1

    for i in range(len(ordered_dates) -1, 0, -1):

        if ordered_dates[i] - ordered_dates[i-1] == timedelta(days=1):
            streak_count += 1
        else:
            break
    return streak_count

dates = []
today = datetime.now().date()
for i in range(40):
    if i == 15:
        continue
    dates.append(today-timedelta(days=i))
print(dates)
print(streak(dates))

