from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class PlayerId:
    """Value object for a player identity.

    Fields:
        value: Unique UUID for the player.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise TypeError("PlayerId value must be a UUID.")
        if self.value.int == 0:
            raise ValueError("PlayerId value must not be the nil UUID.")


@dataclass(frozen=True)
class TimeSlot:
    """Value object for a booking time window.

    Fields:
        start_time: Start of the booking window.
        end_time: End of the booking window.
    """

    start_time: datetime
    end_time: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.start_time, datetime) or not isinstance(self.end_time, datetime):
            raise TypeError("TimeSlot start_time and end_time must be datetime values.")
        if self.start_time >= self.end_time:
            raise ValueError("TimeSlot start_time must be before end_time.")

    def is_premium(self) -> bool:
        """Return True when start_time begins within the premium window (18-22)."""

        return 18 <= self.start_time.hour < 22

    def is_overlapping(self, other: "TimeSlot") -> bool:
        """Return True when this slot overlaps another slot."""

        return self.start_time < other.end_time and other.start_time < self.end_time

