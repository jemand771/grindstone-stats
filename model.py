from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

id_type = str

@dataclass
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

