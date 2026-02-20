"""Event queue with debouncing and batching (Phase 8)."""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import json

from core.sync.base_providers import SyncEvent
from core.services.logging_manager import get_logger

logger = get_logger(__name__)


class EventQueue:
    """Debounce and batch external system events."""

    def __init__(
        self,
        debounce_seconds: int = 30,
        batch_size: int = 50,
        max_retries: int = 3,
    ):
        self.debounce_seconds = debounce_seconds
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.pending_events: Dict[str, List[SyncEvent]] = defaultdict(list)
        self.last_sync: Dict[str, datetime] = {}
        self.processing = False
        self.processors: Dict[str, Callable] = {}

    def register_processor(self, provider: str, processor: Callable):
        """Register an event processor for a provider."""
        self.processors[provider] = processor
        logger.info(f"Registered event processor for {provider}")

    async def enqueue(self, event: SyncEvent):
        """Add event to queue."""
        key = event.provider
        self.pending_events[key].append(event)
        logger.debug(f"Enqueued {event.event_type} event for {key}: {event.id}")

    async def _should_process(self, provider: str) -> bool:
        """Check if enough time has passed to process queued events."""
        if provider not in self.last_sync:
            return True

        elapsed = datetime.now() - self.last_sync[provider]
        return elapsed.total_seconds() >= self.debounce_seconds

    async def process_batch(self, provider: Optional[str] = None) -> Dict[str, any]:
        """Process queued events with debouncing and batching."""
        if self.processing:
            logger.debug("Processing already in progress, skipping")
            return {"status": "processing", "skipped": True}

        self.processing = True
        results = {}

        try:
            providers_to_process = (
                [provider] if provider else list(self.pending_events.keys())
            )

            for prov in providers_to_process:
                if not self.pending_events[prov]:
                    continue

                if not await self._should_process(prov):
                    logger.debug(
                        f"Debounce interval not met for {prov}, skipping batch"
                    )
                    continue

                logger.info(
                    f"Processing batch for {prov}: "
                    f"{len(self.pending_events[prov])} events"
                )

                # Get processor
                if prov not in self.processors:
                    logger.warning(f"No processor registered for {prov}")
                    continue

                processor = self.processors[prov]

                # Split into batches
                events = self.pending_events[prov]
                batches = [
                    events[i : i + self.batch_size]
                    for i in range(0, len(events), self.batch_size)
                ]

                batch_results = []
                for batch_idx, batch in enumerate(batches):
                    try:
                        batch_result = await processor(batch)
                        batch_results.append(
                            {
                                "batch": batch_idx,
                                "count": len(batch),
                                "status": "success",
                                "result": batch_result,
                            }
                        )
                        logger.info(
                            f"Processed batch {batch_idx + 1}/{len(batches)} "
                            f"for {prov} ({len(batch)} events)"
                        )
                    except Exception as e:
                        logger.error(f"Error processing batch {batch_idx}: {e}")
                        batch_results.append(
                            {
                                "batch": batch_idx,
                                "count": len(batch),
                                "status": "error",
                                "error": str(e),
                            }
                        )

                # Update last sync time and clear processed events
                self.last_sync[prov] = datetime.now()
                self.pending_events[prov] = []

                results[prov] = {
                    "status": "completed",
                    "total_events": sum(len(b) for b in batches),
                    "batches": batch_results,
                }

            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "providers": results,
            }

        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            self.processing = False

    async def get_queue_status(self) -> Dict[str, any]:
        """Get current queue status."""
        return {
            "processing": self.processing,
            "timestamp": datetime.now().isoformat(),
            "pending_events": {
                provider: len(events)
                for provider, events in self.pending_events.items()
                if events
            },
            "last_sync": {
                provider: sync_time.isoformat()
                for provider, sync_time in self.last_sync.items()
            },
            "debounce_seconds": self.debounce_seconds,
            "batch_size": self.batch_size,
        }

    def clear_queue(self, provider: Optional[str] = None):
        """Clear pending events (for testing or manual reset)."""
        if provider:
            self.pending_events[provider] = []
            logger.info(f"Cleared queue for {provider}")
        else:
            self.pending_events.clear()
            logger.info("Cleared all event queues")

    async def manual_process(self, events: List[SyncEvent]) -> Dict[str, any]:
        """Manually process a list of events (bypass queue)."""
        logger.info(f"Manual processing of {len(events)} events")

        try:
            # Group by provider
            by_provider = defaultdict(list)
            for event in events:
                by_provider[event.provider].append(event)

            results = {}
            for provider, prov_events in by_provider.items():
                if provider not in self.processors:
                    logger.warning(f"No processor for {provider}")
                    continue

                processor = self.processors[provider]
                result = await processor(prov_events)
                results[provider] = result

            return {
                "status": "success",
                "processed_count": len(events),
                "results": results,
            }
        except Exception as e:
            logger.error(f"Error in manual processing: {e}")
            return {"status": "error", "error": str(e)}
