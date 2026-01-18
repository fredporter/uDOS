#!/usr/bin/env python3
"""
MeshCore Protocol - Protocol definitions for mesh networking

Defines message formats, routing tables, acknowledgment/retry logic,
and other protocol-level components for MeshCore P2P communication.

Protocol Design:
- JSON-RPC style message format
- Hop-count based routing
- Automatic acknowledgment and retry
- Checksum validation

Version: v1.3.0
Author: Fred Porter
Date: December 24, 2025
"""

import json
import hashlib
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class MessageType(Enum):
    """Message types for mesh protocol."""
    # Control messages
    DISCOVERY = "discovery"       # Device discovery broadcast
    PAIR_REQUEST = "pair_req"     # Pairing request
    PAIR_RESPONSE = "pair_res"    # Pairing response
    UNPAIR = "unpair"             # Unpairing notification
    HEARTBEAT = "heartbeat"       # Keep-alive signal
    
    # Data messages
    DATA = "data"                 # User data payload
    BROADCAST = "broadcast"       # Broadcast to all
    
    # Routing messages
    ROUTE_REQUEST = "route_req"   # Route discovery
    ROUTE_RESPONSE = "route_res"  # Route information
    
    # Acknowledgment
    ACK = "ack"                   # Message acknowledgment
    NACK = "nack"                 # Negative acknowledgment


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class MeshMessage:
    """
    Mesh network message.
    
    Format follows JSON-RPC style with header and payload.
    """
    id: str                               # Unique message ID
    source: str                           # Source device ID
    target: str                           # Target device ID (or "*" for broadcast)
    msg_type: MessageType                 # Message type
    payload: str                          # Message content
    timestamp: float                      # Unix timestamp
    ttl: int = 10                         # Time-to-live (hop count)
    priority: MessagePriority = MessagePriority.NORMAL
    sequence: int = 0                     # Sequence number for ordering
    checksum: str = ""                    # Payload checksum
    route: List[str] = field(default_factory=list)  # Route taken
    
    def __post_init__(self):
        """Calculate checksum if not provided."""
        if not self.checksum:
            self.checksum = self._compute_checksum()
    
    def _compute_checksum(self) -> str:
        """Compute SHA-256 checksum of payload."""
        return hashlib.sha256(self.payload.encode()).hexdigest()[:16]
    
    def validate(self) -> bool:
        """Validate message checksum."""
        return self.checksum == self._compute_checksum()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'type': self.msg_type.value,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'priority': self.priority.value,
            'sequence': self.sequence,
            'checksum': self.checksum,
            'route': self.route
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeshMessage':
        """Create message from dictionary."""
        return cls(
            id=data['id'],
            source=data['source'],
            target=data['target'],
            msg_type=MessageType(data['type']),
            payload=data['payload'],
            timestamp=data['timestamp'],
            ttl=data.get('ttl', 10),
            priority=MessagePriority(data.get('priority', 1)),
            sequence=data.get('sequence', 0),
            checksum=data.get('checksum', ''),
            route=data.get('route', [])
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MeshMessage':
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))


def create_message(
    source: str,
    target: str,
    payload: str,
    msg_type: MessageType = MessageType.DATA,
    priority: MessagePriority = MessagePriority.NORMAL,
    ttl: int = 10
) -> MeshMessage:
    """
    Create a new mesh message.
    
    Args:
        source: Source device ID
        target: Target device ID
        payload: Message content
        msg_type: Message type
        priority: Message priority
        ttl: Time-to-live (hop count)
        
    Returns:
        New MeshMessage instance
    """
    return MeshMessage(
        id=str(uuid.uuid4()),
        source=source,
        target=target,
        msg_type=msg_type,
        payload=payload,
        timestamp=time.time(),
        ttl=ttl,
        priority=priority,
        route=[source]
    )


def parse_message(data: bytes) -> Optional[MeshMessage]:
    """
    Parse message from bytes.
    
    Args:
        data: Raw message bytes
        
    Returns:
        Parsed message or None if invalid
    """
    try:
        json_str = data.decode('utf-8')
        message = MeshMessage.from_json(json_str)
        
        if message.validate():
            return message
        else:
            return None
            
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


# ─────────────────────────────────────────────────────────────
# Routing Table
# ─────────────────────────────────────────────────────────────

@dataclass
class RouteEntry:
    """Route table entry."""
    target: str           # Target device ID
    next_hop: str         # Next hop device ID
    hop_count: int        # Number of hops
    signal: int           # Signal quality (0-100)
    latency_ms: float     # Estimated latency
    last_updated: float   # Last update timestamp
    active: bool = True   # Route is active


class RoutingTable:
    """
    Network routing table.
    
    Manages routes between devices with hop count and signal quality metrics.
    Uses Dijkstra-style shortest path algorithm.
    """
    
    def __init__(self):
        """Initialize routing table."""
        # routes[source][target] = RouteEntry
        self.routes: Dict[str, Dict[str, RouteEntry]] = defaultdict(dict)
        
        # Direct connections (adjacency list)
        # adjacency[device] = [(neighbor, signal), ...]
        self.adjacency: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
    
    def add_direct_route(self, source: str, target: str, signal: int = 100) -> None:
        """
        Add a direct connection between devices.
        
        Args:
            source: Source device ID
            target: Target device ID  
            signal: Signal strength (0-100)
        """
        # Add bidirectional adjacency
        if (target, signal) not in self.adjacency[source]:
            self.adjacency[source].append((target, signal))
        if (source, signal) not in self.adjacency[target]:
            self.adjacency[target].append((source, signal))
        
        # Update route entries
        self.routes[source][target] = RouteEntry(
            target=target,
            next_hop=target,
            hop_count=1,
            signal=signal,
            latency_ms=10.0,  # Estimated
            last_updated=time.time()
        )
        
        self.routes[target][source] = RouteEntry(
            target=source,
            next_hop=source,
            hop_count=1,
            signal=signal,
            latency_ms=10.0,
            last_updated=time.time()
        )
    
    def remove_route(self, source: str, target: str) -> None:
        """
        Remove route between devices.
        
        Args:
            source: Source device ID
            target: Target device ID
        """
        # Remove adjacency
        self.adjacency[source] = [(n, s) for n, s in self.adjacency[source] if n != target]
        self.adjacency[target] = [(n, s) for n, s in self.adjacency[target] if n != source]
        
        # Remove route entries
        if target in self.routes[source]:
            del self.routes[source][target]
        if source in self.routes[target]:
            del self.routes[target][source]
    
    def find_route(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find route between source and target.
        
        Uses Dijkstra's algorithm with signal quality as weight.
        
        Args:
            source: Source device ID
            target: Target device ID
            
        Returns:
            List of device IDs in route, or None if no route exists
        """
        if source == target:
            return [source]
        
        # Check for direct route
        if target in self.routes[source] and self.routes[source][target].active:
            return [source, target]
        
        # Dijkstra's algorithm
        import heapq
        
        # Priority queue: (cost, device, path)
        # Cost = inverse of signal quality (lower is better)
        pq = [(0, source, [source])]
        visited = set()
        
        while pq:
            cost, current, path = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == target:
                return path
            
            for neighbor, signal in self.adjacency[current]:
                if neighbor not in visited:
                    # Cost = 100 - signal (so higher signal = lower cost)
                    neighbor_cost = cost + (100 - signal)
                    heapq.heappush(pq, (neighbor_cost, neighbor, path + [neighbor]))
        
        return None
    
    def get_all_routes(self, source: str) -> Dict[str, RouteEntry]:
        """
        Get all routes from a source device.
        
        Args:
            source: Source device ID
            
        Returns:
            Dictionary of target -> RouteEntry
        """
        return dict(self.routes[source])
    
    def update_route_signal(self, source: str, target: str, signal: int) -> None:
        """
        Update signal strength for a route.
        
        Args:
            source: Source device ID
            target: Target device ID
            signal: New signal strength
        """
        if target in self.routes[source]:
            self.routes[source][target].signal = signal
            self.routes[source][target].last_updated = time.time()
        
        # Update adjacency
        for i, (n, s) in enumerate(self.adjacency[source]):
            if n == target:
                self.adjacency[source][i] = (target, signal)
                break
    
    def prune_stale_routes(self, max_age_seconds: float = 300.0) -> int:
        """
        Remove routes older than max age.
        
        Args:
            max_age_seconds: Maximum route age
            
        Returns:
            Number of routes pruned
        """
        now = time.time()
        pruned = 0
        
        for source in list(self.routes.keys()):
            for target in list(self.routes[source].keys()):
                entry = self.routes[source][target]
                if now - entry.last_updated > max_age_seconds:
                    self.remove_route(source, target)
                    pruned += 1
        
        return pruned
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize routing table to dictionary."""
        routes_dict = {}
        for source, targets in self.routes.items():
            routes_dict[source] = {
                target: {
                    'target': entry.target,
                    'next_hop': entry.next_hop,
                    'hop_count': entry.hop_count,
                    'signal': entry.signal,
                    'latency_ms': entry.latency_ms,
                    'last_updated': entry.last_updated,
                    'active': entry.active
                }
                for target, entry in targets.items()
            }
        
        adjacency_dict = {k: list(v) for k, v in self.adjacency.items()}
        
        return {
            'routes': routes_dict,
            'adjacency': adjacency_dict
        }
    
    def load(self, data: Dict[str, Any]) -> None:
        """Load routing table from dictionary."""
        self.routes.clear()
        self.adjacency.clear()
        
        for source, targets in data.get('routes', {}).items():
            for target, entry_data in targets.items():
                self.routes[source][target] = RouteEntry(**entry_data)
        
        for device, neighbors in data.get('adjacency', {}).items():
            self.adjacency[device] = [tuple(n) for n in neighbors]


# ─────────────────────────────────────────────────────────────
# Acknowledgment / Retry Logic
# ─────────────────────────────────────────────────────────────

@dataclass
class PendingAck:
    """Pending acknowledgment entry."""
    message: MeshMessage
    sent_time: float
    retry_count: int = 0
    max_retries: int = 3
    timeout_ms: float = 5000.0


class AckManager:
    """
    Manages message acknowledgments and retries.
    
    Tracks sent messages waiting for ACK and handles retransmission.
    """
    
    def __init__(self, max_retries: int = 3, timeout_ms: float = 5000.0):
        """
        Initialize ACK manager.
        
        Args:
            max_retries: Maximum retry attempts
            timeout_ms: ACK timeout in milliseconds
        """
        self.max_retries = max_retries
        self.timeout_ms = timeout_ms
        
        # Pending messages: message_id -> PendingAck
        self.pending: Dict[str, PendingAck] = {}
    
    def track(self, message: MeshMessage) -> None:
        """
        Start tracking a sent message for ACK.
        
        Args:
            message: Sent message to track
        """
        self.pending[message.id] = PendingAck(
            message=message,
            sent_time=time.time(),
            max_retries=self.max_retries,
            timeout_ms=self.timeout_ms
        )
    
    def acknowledge(self, message_id: str) -> bool:
        """
        Mark message as acknowledged.
        
        Args:
            message_id: Message ID to acknowledge
            
        Returns:
            True if message was pending
        """
        if message_id in self.pending:
            del self.pending[message_id]
            return True
        return False
    
    def get_timed_out(self) -> List[PendingAck]:
        """
        Get messages that have timed out.
        
        Returns:
            List of timed out pending messages
        """
        now = time.time()
        timed_out = []
        
        for msg_id, pending in list(self.pending.items()):
            elapsed_ms = (now - pending.sent_time) * 1000
            
            if elapsed_ms > pending.timeout_ms:
                if pending.retry_count >= pending.max_retries:
                    # Max retries exceeded - remove
                    del self.pending[msg_id]
                else:
                    timed_out.append(pending)
        
        return timed_out
    
    def mark_retry(self, message_id: str) -> bool:
        """
        Mark message for retry.
        
        Args:
            message_id: Message ID to retry
            
        Returns:
            True if retry is allowed
        """
        if message_id in self.pending:
            pending = self.pending[message_id]
            pending.retry_count += 1
            pending.sent_time = time.time()
            return pending.retry_count <= pending.max_retries
        return False
    
    def clear(self) -> None:
        """Clear all pending acknowledgments."""
        self.pending.clear()


# ─────────────────────────────────────────────────────────────
# Rate Limiting
# ─────────────────────────────────────────────────────────────

class RateLimiter:
    """
    Token bucket rate limiter for network messages.
    """
    
    def __init__(self, rate: float = 10.0, burst: int = 20):
        """
        Initialize rate limiter.
        
        Args:
            rate: Messages per second
            burst: Maximum burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
    
    def allow(self) -> bool:
        """
        Check if a message is allowed.
        
        Returns:
            True if message is allowed
        """
        now = time.time()
        
        # Refill tokens
        elapsed = now - self.last_update
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        
        return False
    
    def wait_time(self) -> float:
        """
        Get time to wait before next message is allowed.
        
        Returns:
            Wait time in seconds
        """
        if self.tokens >= 1:
            return 0.0
        
        return (1 - self.tokens) / self.rate
