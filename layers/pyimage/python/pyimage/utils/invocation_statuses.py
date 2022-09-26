from enum import Enum


class InvocationStatus(Enum):
    """Invocation Statuses Values"""

    STARTED = "STARTED"
    RUNNING = "RUNNING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    FAILED = "FAILED"
