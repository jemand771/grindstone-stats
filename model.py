from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, date
import functools
from typing import Optional

id_type = str

@dataclass(eq=True, frozen=True)
class WorkItem:
    gid: id_type
    name: str
    completed: Optional[datetime] = None

    def to_grindstone(self):
        return {
            "i": self.gid,
            "n": self.name
        }


@dataclass
class TimeSlice:
    gid: id_type
    work_item: WorkItem
    start: datetime
    end: datetime

    @property
    def duration(self):
        pass

    def to_grindstone(self):
        return {
            "i": self.gid,
            "t": self.work_item.gid,
            "s": unparse_date(self.start),
            "e": unparse_date(self.end)
        }


@dataclass
class GrindstoneDatabase:

    time_slices: dict[id_type, TimeSlice]
    work_items: dict[id_type, WorkItem]

    @classmethod
    def from_grindstone(cls, obj):
        # parse work items
        work_items = {}
        for entry in obj["f"]["t"]:
            item = WorkItem(gid=entry["i"], name=entry["n"])
            completions = [c for c in obj["f"]["i"] if c["i"] == item.gid]
            if completions:
                item.completed = parse_date(completions[0]["c"])
            work_items[item.gid] = item
        # parse time slices
        time_slices = {
            entry["i"]: TimeSlice(
                gid=entry["i"],
                work_item=work_items[entry["t"]],
                start=parse_date(entry["s"]),
                end=parse_date(entry["e"])
            ) for entry in obj["f"]["r"]
        }
        return cls(
            time_slices=time_slices,
            work_items=work_items
        )

    def to_grindstone(self):
        return {
            "f": {
                "t": [item.to_grindstone() for item in self.work_items.values()],
                "i": [{
                    "i": item.gid,
                    "c": unparse_date(item.completed)
                } for item in self.work_items.values() if item.completed is not None],
                "r": [item.to_grindstone() for item in self.time_slices.values()],
            }
        }


def parse_date(str_: str) -> datetime:
    return datetime.fromisoformat(str_.replace("Z", "+00:00"))


def unparse_date(datetime_: datetime) -> str:
    return datetime_.isoformat().replace("+00:00", "Z")


@dataclass
class Analytics:

    db: GrindstoneDatabase
    # TODO implement analytics

    def total_time(self):
        return 0

    @property
    def daliy_workitems(self):
        data = {}
        for slice in self.db.time_slices.values():
            day = slice.end.date()
            data.setdefault(day, {})
            data[day].setdefault(slice.work_item, timedelta())
            data[day][slice.work_item] += slice.end - slice.start

        for day, work in data.items():
            for item, delta in work.items():
                work[item] = self.round_timedelta(delta, timedelta(minutes=5))

        return data

    @property
    def daily_work_total(self):
        return self.daily_work_filtered(work_items=self.db.work_items.values())

    def daily_work_filtered(self, work_items=()):
        return {
            item: sum(
                (
                    delta for item, delta
                    in work.items()
                    if item in work_items
                ),
                start=timedelta()
            )
            for item, work in self.daliy_workitems.items()
        }

    @property
    def weeks_in_db(self):
        return list(sorted({
            (day.isocalendar().year, day.isocalendar().week)
            for day in self.daily_work_total
        }))

    @property
    def weeks_in_db_filled(self):
        first_year = self.weeks_in_db[0][0]
        last_year = self.weeks_in_db[-1][0]
        all_weeks = []
        for year in range(first_year, last_year + 1):
            all_weeks.extend(self.generate_weeks_from_year(year))
        return all_weeks

    @staticmethod
    def generate_weeks_from_year(year):
        first = datetime(year, 1, 4).date().isocalendar().week
        last = datetime(year, 12, 31).date().isocalendar().week
        # this is still wrong because I'm _probably_ missing an entire week. oh well
        return [
            (year, week)
            for week
            in range(first, last + 1)
        ]

    @staticmethod
    def group_daily_by_calweek(data: dict[date, dict[WorkItem, timedelta]], relevant_weeks: list[tuple]):
        week_data = {}
        for year, week in sorted(relevant_weeks):
            week_days = [datetime.strptime(f"{year} {week} {day}", "%G %V %w").date() for day in range(1, 6)]
            week_data[(year, week)] = [data.get(day) for day in week_days]
        return week_data
    
    @staticmethod
    def week_groups_add_sum(data: dict[str, list[timedelta]]):
        return {
            week: [*times, sum([t for t in times if t], start=timedelta())]
            for week, times
            in data.items()
        }

    @staticmethod
    def make_rolling(day_times, reset_before_dates=(date(2022, 6, 27),)):
        rolling = timedelta()
        rolling_times = {}
        for day, day_time in day_times.items():
            if day in reset_before_dates:
                rolling = timedelta()
            rolling += day_time
            # TODO some people don't work 40h
            rolling -= timedelta(hours=8)
            rolling_times[day] = timedelta(seconds=rolling.total_seconds())
        return rolling_times

    @staticmethod
    def round_timedelta(delta, to_closest):
        return timedelta(seconds=int(
            to_closest.total_seconds() * round(
                delta.total_seconds() / to_closest.total_seconds()
            )
        ))

    @staticmethod
    def format_timedelta(delta: timedelta, split_days=False):
        if delta is None:
            return ""
        p = ModuloPopper(abs(delta.total_seconds()))
        seconds = p.pop(60)
        minutes = p.pop(60)
        if split_days:
            hours = p.pop(24)
            days = p.value
            daystr = f"{days}d " if days else ""
        else:
            hours = p.value
            daystr = ""
        secstr = f":{seconds:02}" if seconds else ""
        sign = "-" if delta.total_seconds() < 0 else " "
        return f"{sign}{daystr}{hours:02}:{minutes:02}{secstr}"


class ModuloPopper:

    def __init__(self, value) -> None:
        self.value = int(value)

    def pop(self, factor):
        try:
            return self.value % factor
        finally:
            self.value //= factor
