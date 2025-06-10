from typing import Any


class TaskContext:
    """Object allowing task context pass to task functions."""

    def __init__(
            self,
            *,
            params: dict | None = None,
            last_result: dict | None = None,
            obj: Any = None
    ):
        """
        :param params: Task parameters.
        :param last_result: Task result from the last (previous) run.
        :param obj: Raw task object (if provided by a backend).
        """
        self.params = params or {}
        self.result = None
        self.last_result = last_result or {}
        self.obj = obj
