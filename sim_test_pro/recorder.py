"""Recorder module for recording flight data using SimVars."""

import asyncio
import datetime
import logging
import time
from contextlib import suppress

from simconnect import SimConnect, SimVar


class Recorder:
    """Recorder class to record flight data using SimVars."""

    def __init__(self, simconnect: SimConnect) -> None:
        """Initialize the recorder."""
        self._simconnect = simconnect
        self._recording = False

        self._recorded_vars: list[SimVar] = []
        self._recorded_values: list[tuple[SimVar, list[str]]] = []

        self._start_time: float = 0.0
        self._recorded_time: list[float] = []

    def record_variable(self, var: SimVar) -> None:
        """Record a simvar."""
        if self._recording:
            msg = f"Recording is already in progress. Cannot record {var}."
            raise RuntimeError(msg)

        if var not in self._recorded_vars:
            self._recorded_vars.append(var)

    def _record_raw_variable(self, value: str, index: int | None) -> None:
        """Record a raw simvar from name and optional index."""
        if value == "TIME":
            return
        self.record_variable(SimVar(value, index))

    def record_from_config(self, graphs: dict) -> None:
        """Record flight data from the given configuration."""

        def _handle_value(value: str | dict) -> None:
            """Handle the value of a graph axis."""
            if isinstance(value, str):
                return self._record_raw_variable(value, None)
            if isinstance(value, dict):
                return self._record_raw_variable(value["name"], value["index"])

            msg = f"Invalid value type: {type(value)}"
            raise ValueError(msg)

        for graph in graphs:
            if any(graph[axis] is None for axis in ["x", "y"]):
                msg = f"Graph {graph['name']} missing axis"
                raise ValueError(msg)

            # X Axis
            x_value = graph["x"]
            _handle_value(x_value)

            # Y Axis
            y_value = graph["y"]
            if isinstance(y_value, str):
                _handle_value(y_value)
            else:
                for pair in y_value:
                    _handle_value(pair)

    def clear_recorded_vars(self) -> None:
        """Clear the recorded variables."""
        if self._recording:
            msg = "Recording is in progress. Cannot clear recorded variables."
            raise RuntimeError(msg)

        self._recorded_vars.clear()
        self._recorded_values.clear()
        self._recorded_time.clear()
        self._start_time = 0.0

    def _is_in_recorded_values(self, var: SimVar) -> bool:
        """Check if a variable is in the recorded values."""
        return any(var_values[0] == var for var_values in self._recorded_values)

    async def _start(self, delay: datetime.timedelta) -> None:
        """Run the recorder."""
        try:
            logging.info("Recording flight data with %d variables.", len(self._recorded_vars))
            while not self._stop_event.is_set():
                # Record variables
                data = []
                try:
                    data = self._simconnect.get_multiple(self._recorded_vars)
                except Exception:
                    logging.exception("Error while recording data, skipping frame.")
                    continue

                for var in data:
                    if self._is_in_recorded_values(var):
                        recorded_values = next(value[1] for value in self._recorded_values if value[0] == var)  # Find the values list for var
                        recorded_values.append(data[var])
                    else:
                        self._recorded_values.append((var, [data[var]]))

                # Record time
                self._recorded_time.append(time.time() - self._start_time)

                # Wait for next iteration
                await asyncio.sleep(delay.total_seconds())
        finally:
            logging.info("Recording stopped. It lasted %.2f seconds.", self._recorded_time[-1])
            self._recording = False
            self._stop_event = None

    def start(self, delay: datetime.timedelta, stop_event: asyncio.Event) -> asyncio.Task:
        """Start recording flight data."""
        if self._recording:
            msg = "Recording is already in progress."
            raise RuntimeError(msg)

        self._recording = True
        self._recorded_values = []
        self._recorded_time = []
        self._start_time = time.time()

        stop_event.clear()
        self._stop_event = stop_event

        return asyncio.create_task(self._start(delay))

    def get_results(self) -> tuple[list[tuple[SimVar, list[str]]], list[float]]:
        """Stop recording flight data and return the recorded values."""
        if self._recording:
            msg = "Recording is still in progress. Stop it before getting results."
            raise RuntimeError(msg)

        return self._recorded_values, self._recorded_time
