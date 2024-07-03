import asyncio
import logging
import threading
from typing import List, Optional

from .events.client import AsyncEventsClient, EventsClient
from .types import CreateEventRequestBody

DEFAULT_BUFFER_MAX_SIZE = 10 * 1024  # 10KB
DEFAULT_EVENT_BUFFER_PERIOD = 5  # 5 seconds


class EventBuffer:
    def __init__(
        self,
        events_api: EventsClient,
        logger: logging.Logger,
        period: Optional[int] = None,
    ):
        self.current_size = 0
        self.events: List[CreateEventRequestBody] = []
        self.events_api = events_api
        self.interval = period or DEFAULT_EVENT_BUFFER_PERIOD
        self.logger = logger
        self.max_size = DEFAULT_BUFFER_MAX_SIZE
        self.flush_lock = threading.Lock()
        self.push_lock = threading.Lock()
        self.shutdown = threading.Event()
        self.stopped = False

        # Start periodic flushing thread
        self.flush_thread = threading.Thread(target=self._periodic_flush)
        self.flush_thread.daemon = True
        self.flush_thread.start()

    def _flush(self):
        with self.flush_lock:
            if not self.events:
                return

            events = [event for event in self.events if event is not None]
            try:
                self.events_api.create_event_batch(events=events)
            except Exception as e:
                self.logger.error(e)

            self.events.clear()
            self.current_size = 0

    def _periodic_flush(self):
        while not self.shutdown.is_set():
            self._flush()
            self.shutdown.wait(timeout=self.interval)

    def push(self, event: CreateEventRequestBody):
        if self.stopped:
            self.logger.error("Event buffer is stopped, not accepting new events")
            return

        with self.push_lock:
            event_size = event.__sizeof__()
            if self.current_size + event_size > self.max_size:
                self._flush()

            self.events.append(event)
            self.current_size += event_size

    def stop(self):
        try:
            self.stopped = True
            self.shutdown.set()
            self.flush_thread.join(timeout=5)
        except Exception as e:
            self.logger.error(f"Panic occurred while closing client: {e}")


class AsyncEventBuffer:
    def __init__(
        self,
        events_api: AsyncEventsClient,
        logger: logging.Logger,
        period: Optional[int] = None,
    ):
        self.current_size = 0
        self.events: List[CreateEventRequestBody] = []
        self.events_api = events_api
        self.interval = period or DEFAULT_EVENT_BUFFER_PERIOD
        self.logger = logger
        self.max_size = DEFAULT_BUFFER_MAX_SIZE
        self.shutdown_event = asyncio.Event()
        self.stopped = False
        self.flush_lock = asyncio.Lock()
        self.push_lock = asyncio.Lock()

        # Start periodic flushing task
        self.flush_task = asyncio.create_task(self._periodic_flush())

    async def _flush(self):
        async with self.flush_lock:
            if not self.events:
                return

            events = [event for event in self.events if event is not None]
            try:
                await self.events_api.create_event_batch(events=events)
            except Exception as e:
                self.logger.error(e)

            self.events.clear()
            self.current_size = 0

    async def _periodic_flush(self):
        while not self.shutdown_event.is_set():
            await self._flush()
            try:
                await asyncio.wait_for(
                    self.shutdown_event.wait(), timeout=self.interval
                )
            except asyncio.TimeoutError:
                pass

    async def push(self, event: CreateEventRequestBody):
        if self.stopped:
            self.logger.error("Event buffer is stopped, not accepting new events")
            return

        async with self.push_lock:
            event_size = event.__sizeof__()
            if self.current_size + event_size > self.max_size:
                await self._flush()

            self.events.append(event)
            self.current_size += event_size

    async def stop(self):
        try:
            self.stopped = True
            self.shutdown_event.set()
            await self.flush_task
        except Exception as e:
            self.logger.error(f"Panic occurred while closing client: {e}")
