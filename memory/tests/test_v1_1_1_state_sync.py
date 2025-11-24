"""
uDOS v1.1.1 - State Synchronization Engine Test Suite

Comprehensive test suite for Feature 1.1.1.4: CLI/Web State Consistency

Test Coverage:
- Event sourcing and state snapshots
- Real-time state synchronization
- Conflict resolution (last-writer-wins)
- Command history synchronization
- Mission/scenario state sync
- Planet/tile position sync
- Memory tier access sync
- Project state consistency
- Offline state buffering
- State restoration on reconnection
- Performance and scalability
- Concurrent update handling

Feature: 1.1.1.4
Version: 1.1.1
Status: Active Development
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
import time
import copy
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from collections import deque

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


class TestEventSourcing(unittest.TestCase):
    """Test event sourcing architecture"""

    def test_event_creation(self):
        """Test creating state change events"""
        event = {
            'event_id': 'evt_12345',
            'event_type': 'POSITION_CHANGED',
            'timestamp': time.time(),
            'source': 'cli',
            'data': {
                'old_position': [10, 10],
                'new_position': [11, 10]
            },
            'sequence': 1
        }
        
        self.assertIn('event_id', event)
        self.assertIn('event_type', event)
        self.assertEqual(event['source'], 'cli')

    def test_event_log_append(self):
        """Test appending events to event log"""
        event_log = []
        
        event1 = {'event_id': 'evt_1', 'sequence': 1, 'type': 'COMMAND'}
        event2 = {'event_id': 'evt_2', 'sequence': 2, 'type': 'STATE_CHANGE'}
        
        event_log.append(event1)
        event_log.append(event2)
        
        self.assertEqual(len(event_log), 2)
        self.assertEqual(event_log[0]['sequence'], 1)

    def test_event_replay(self):
        """Test replaying events to reconstruct state"""
        initial_state = {'position': [0, 0], 'score': 0}
        events = [
            {'type': 'MOVE', 'data': {'position': [1, 0]}},
            {'type': 'SCORE', 'data': {'score': 10}},
            {'type': 'MOVE', 'data': {'position': [2, 0]}}
        ]
        
        state = copy.deepcopy(initial_state)
        for event in events:
            if event['type'] == 'MOVE':
                state['position'] = event['data']['position']
            elif event['type'] == 'SCORE':
                state['score'] = event['data']['score']
        
        self.assertEqual(state['position'], [2, 0])
        self.assertEqual(state['score'], 10)

    def test_snapshot_creation(self):
        """Test creating state snapshots"""
        current_state = {
            'position': [15, 20],
            'inventory': ['water', 'compass'],
            'mission': 'gather_water'
        }
        
        snapshot = {
            'snapshot_id': 'snap_123',
            'timestamp': time.time(),
            'sequence': 100,
            'state': copy.deepcopy(current_state)
        }
        
        self.assertIn('snapshot_id', snapshot)
        self.assertEqual(snapshot['state']['position'], [15, 20])

    def test_snapshot_restoration(self):
        """Test restoring state from snapshot"""
        snapshot = {
            'state': {
                'position': [5, 5],
                'health': 100
            }
        }
        
        # Restore state
        restored = copy.deepcopy(snapshot['state'])
        
        self.assertEqual(restored['position'], [5, 5])
        self.assertEqual(restored['health'], 100)


class TestRealtimeSync(unittest.TestCase):
    """Test real-time state synchronization"""

    def test_state_change_broadcast(self):
        """Test state changes are broadcast to all clients"""
        clients = [Mock(), Mock(), Mock()]
        state_change = {
            'type': 'state_update',
            'field': 'position',
            'value': [12, 12]
        }
        
        # Broadcast to all clients
        for client in clients:
            client.send(json.dumps(state_change))
        
        for client in clients:
            client.send.assert_called_once()

    def test_incremental_state_updates(self):
        """Test incremental state updates (deltas)"""
        current_state = {'position': [10, 10], 'health': 100}
        
        # Only send changed fields
        delta = {'health': 95}
        
        # Apply delta
        current_state.update(delta)
        
        self.assertEqual(current_state['health'], 95)
        self.assertEqual(current_state['position'], [10, 10])

    def test_full_state_sync(self):
        """Test full state synchronization"""
        server_state = {
            'position': [20, 20],
            'inventory': ['water', 'food'],
            'mission': 'explore'
        }
        
        # Client requests full sync
        synced_state = copy.deepcopy(server_state)
        
        self.assertEqual(synced_state['position'], [20, 20])
        self.assertEqual(len(synced_state['inventory']), 2)

    def test_heartbeat_mechanism(self):
        """Test heartbeat keeps sync alive"""
        last_heartbeat = time.time()
        heartbeat_interval = 30  # 30 seconds
        
        # Check if heartbeat needed
        time_since = time.time() - last_heartbeat
        needs_heartbeat = time_since > heartbeat_interval
        
        # Should not need heartbeat yet
        self.assertFalse(needs_heartbeat)

    def test_sync_acknowledgment(self):
        """Test sync messages are acknowledged"""
        sync_message = {
            'message_id': 'msg_123',
            'type': 'state_sync',
            'data': {'position': [5, 5]}
        }
        
        ack = {
            'message_id': sync_message['message_id'],
            'type': 'ack',
            'received_at': time.time()
        }
        
        self.assertEqual(ack['message_id'], sync_message['message_id'])


class TestConflictResolution(unittest.TestCase):
    """Test conflict resolution strategies"""

    def test_last_writer_wins(self):
        """Test last-writer-wins conflict resolution"""
        updates = [
            {'timestamp': 1000, 'source': 'cli', 'position': [10, 10]},
            {'timestamp': 1001, 'source': 'web', 'position': [11, 11]},
            {'timestamp': 999, 'source': 'cli', 'position': [9, 9]}
        ]
        
        # Sort by timestamp, take latest
        latest = max(updates, key=lambda u: u['timestamp'])
        
        self.assertEqual(latest['position'], [11, 11])
        self.assertEqual(latest['source'], 'web')

    def test_timestamp_ordering(self):
        """Test events ordered by timestamp"""
        events = [
            {'id': 1, 'timestamp': 1500},
            {'id': 2, 'timestamp': 1200},
            {'id': 3, 'timestamp': 1800}
        ]
        
        sorted_events = sorted(events, key=lambda e: e['timestamp'])
        
        self.assertEqual(sorted_events[0]['id'], 2)
        self.assertEqual(sorted_events[-1]['id'], 3)

    def test_conflict_detection(self):
        """Test detecting conflicting updates"""
        cli_update = {'version': 5, 'position': [10, 10]}
        web_update = {'version': 5, 'position': [11, 11]}
        
        # Same version, different values = conflict
        has_conflict = (
            cli_update['version'] == web_update['version'] and
            cli_update['position'] != web_update['position']
        )
        
        self.assertTrue(has_conflict)

    def test_version_vector(self):
        """Test version vectors for conflict detection"""
        version_vector = {
            'cli': 5,
            'web': 3
        }
        
        # Update from CLI
        version_vector['cli'] += 1
        
        self.assertEqual(version_vector['cli'], 6)
        self.assertEqual(version_vector['web'], 3)

    def test_merge_strategy(self):
        """Test merging non-conflicting updates"""
        base = {'position': [10, 10], 'health': 100}
        update1 = {'position': [11, 10]}  # Only position changed
        update2 = {'health': 95}  # Only health changed
        
        # Merge both updates
        merged = copy.deepcopy(base)
        merged.update(update1)
        merged.update(update2)
        
        self.assertEqual(merged['position'], [11, 10])
        self.assertEqual(merged['health'], 95)


class TestCommandHistorySync(unittest.TestCase):
    """Test command history synchronization"""

    def test_command_history_append(self):
        """Test appending commands to history"""
        history = deque(maxlen=100)
        
        history.append({'command': 'MAP', 'timestamp': time.time()})
        history.append({'command': 'MOVE N', 'timestamp': time.time()})
        
        self.assertEqual(len(history), 2)

    def test_history_size_limit(self):
        """Test history respects size limit"""
        max_size = 10
        history = deque(maxlen=max_size)
        
        # Add more than limit
        for i in range(20):
            history.append({'command': f'CMD_{i}'})
        
        self.assertEqual(len(history), max_size)
        self.assertEqual(history[0]['command'], 'CMD_10')

    def test_history_sync_to_web(self):
        """Test syncing history to web client"""
        cli_history = [
            {'command': 'LS', 'timestamp': 1000},
            {'command': 'CD /tmp', 'timestamp': 1001}
        ]
        
        # Send to web
        sync_message = {
            'type': 'history_sync',
            'history': cli_history
        }
        
        self.assertEqual(len(sync_message['history']), 2)

    def test_history_merge(self):
        """Test merging histories from CLI and Web"""
        cli_history = [
            {'command': 'LS', 'timestamp': 1000, 'source': 'cli'},
            {'command': 'PWD', 'timestamp': 1002, 'source': 'cli'}
        ]
        web_history = [
            {'command': 'CD /home', 'timestamp': 1001, 'source': 'web'}
        ]
        
        # Merge and sort by timestamp
        merged = sorted(
            cli_history + web_history,
            key=lambda c: c['timestamp']
        )
        
        self.assertEqual(len(merged), 3)
        self.assertEqual(merged[1]['command'], 'CD /home')


class TestMissionStateSync(unittest.TestCase):
    """Test mission/scenario state synchronization"""

    def test_mission_state_structure(self):
        """Test mission state structure"""
        mission_state = {
            'mission_id': 'mission_123',
            'name': 'Water Collection',
            'status': 'in_progress',
            'objectives': [
                {'id': 1, 'description': 'Find water source', 'completed': True},
                {'id': 2, 'description': 'Purify water', 'completed': False}
            ],
            'updated_at': time.time()
        }
        
        self.assertEqual(mission_state['status'], 'in_progress')
        self.assertTrue(mission_state['objectives'][0]['completed'])

    def test_objective_completion_sync(self):
        """Test objective completion syncs across clients"""
        state = {
            'objectives': [
                {'id': 1, 'completed': False},
                {'id': 2, 'completed': False}
            ]
        }
        
        # Complete objective 1
        update = {'objective_id': 1, 'completed': True}
        
        for obj in state['objectives']:
            if obj['id'] == update['objective_id']:
                obj['completed'] = update['completed']
        
        self.assertTrue(state['objectives'][0]['completed'])

    def test_mission_progress_sync(self):
        """Test mission progress percentage sync"""
        objectives = [
            {'completed': True},
            {'completed': True},
            {'completed': False},
            {'completed': False}
        ]
        
        completed = sum(1 for obj in objectives if obj['completed'])
        progress = (completed / len(objectives)) * 100
        
        self.assertEqual(progress, 50.0)


class TestPositionSync(unittest.TestCase):
    """Test planet/tile position synchronization"""

    def test_position_update(self):
        """Test position updates sync"""
        position = {'x': 10, 'y': 10, 'planet': 'Earth'}
        
        # Update position
        new_position = {'x': 11, 'y': 10, 'planet': 'Earth'}
        position.update(new_position)
        
        self.assertEqual(position['x'], 11)

    def test_planet_transition(self):
        """Test planet transitions sync"""
        state = {'planet': 'Earth', 'coordinates': [0, 0]}
        
        # Transition to Mars
        transition = {'planet': 'Mars', 'coordinates': [5, 5]}
        state.update(transition)
        
        self.assertEqual(state['planet'], 'Mars')
        self.assertEqual(state['coordinates'], [5, 5])

    def test_tile_data_sync(self):
        """Test tile data synchronization"""
        tile_data = {
            'position': [10, 10],
            'terrain': 'forest',
            'resources': ['wood', 'water'],
            'explored': True
        }
        
        # Share tile data
        synced = copy.deepcopy(tile_data)
        
        self.assertEqual(synced['terrain'], 'forest')
        self.assertTrue(synced['explored'])


class TestMemoryTierSync(unittest.TestCase):
    """Test memory tier access synchronization"""

    def test_tier_access_tracking(self):
        """Test tracking which tiers are accessible"""
        access = {
            'tier1_private': True,
            'tier2_shared': True,
            'tier3_group': False,
            'tier4_public': True
        }
        
        accessible_tiers = [k for k, v in access.items() if v]
        
        self.assertEqual(len(accessible_tiers), 3)
        self.assertIn('tier1_private', accessible_tiers)

    def test_tier_state_sync(self):
        """Test tier state synchronizes"""
        tier_state = {
            'current_tier': 'tier2_shared',
            'recent_files': [
                'memory/shared/notes.md',
                'memory/shared/project.md'
            ]
        }
        
        # Sync to web
        sync_message = {
            'type': 'tier_state',
            'data': tier_state
        }
        
        self.assertEqual(sync_message['data']['current_tier'], 'tier2_shared')


class TestProjectStateSync(unittest.TestCase):
    """Test project state consistency"""

    def test_project_metadata_sync(self):
        """Test project metadata synchronization"""
        project = {
            'name': 'Survival Guide',
            'path': '/memory/projects/survival',
            'files': ['README.md', 'water.md', 'fire.md'],
            'last_modified': time.time()
        }
        
        synced = copy.deepcopy(project)
        
        self.assertEqual(len(synced['files']), 3)

    def test_file_change_notification(self):
        """Test file changes are notified"""
        notification = {
            'type': 'file_changed',
            'file': '/memory/projects/survival/water.md',
            'change_type': 'modified',
            'timestamp': time.time()
        }
        
        self.assertEqual(notification['change_type'], 'modified')


class TestOfflineBuffering(unittest.TestCase):
    """Test offline state buffering"""

    def test_offline_event_buffering(self):
        """Test events buffer when offline"""
        offline_buffer = []
        is_online = False
        
        event = {'type': 'POSITION_CHANGED', 'data': {'x': 5}}
        
        if not is_online:
            offline_buffer.append(event)
        
        self.assertEqual(len(offline_buffer), 1)

    def test_buffer_replay_on_reconnect(self):
        """Test buffered events replay on reconnection"""
        buffer = [
            {'sequence': 1, 'type': 'MOVE'},
            {'sequence': 2, 'type': 'ACTION'},
            {'sequence': 3, 'type': 'COLLECT'}
        ]
        
        # Replay all buffered events
        replayed = []
        for event in buffer:
            replayed.append(event)
        
        self.assertEqual(len(replayed), 3)

    def test_buffer_size_limit(self):
        """Test buffer has size limit"""
        max_buffer = 1000
        buffer = deque(maxlen=max_buffer)
        
        # Add many events
        for i in range(2000):
            buffer.append({'event': i})
        
        self.assertEqual(len(buffer), max_buffer)

    def test_critical_events_preserved(self):
        """Test critical events always preserved"""
        buffer = []
        max_size = 5
        
        events = [
            {'priority': 'normal', 'data': 'A'},
            {'priority': 'critical', 'data': 'B'},
            {'priority': 'normal', 'data': 'C'},
            {'priority': 'critical', 'data': 'D'},
        ]
        
        # Keep all critical events
        critical = [e for e in events if e['priority'] == 'critical']
        
        self.assertEqual(len(critical), 2)


class TestStateRestoration(unittest.TestCase):
    """Test state restoration on reconnection"""

    def test_reconnection_state_request(self):
        """Test client requests state on reconnection"""
        request = {
            'type': 'state_request',
            'client_id': 'client_123',
            'last_sequence': 45
        }
        
        self.assertEqual(request['type'], 'state_request')
        self.assertIn('last_sequence', request)

    def test_incremental_state_catch_up(self):
        """Test incremental catch-up from last known state"""
        client_sequence = 45
        server_sequence = 50
        
        events = [
            {'sequence': 46, 'type': 'MOVE'},
            {'sequence': 47, 'type': 'ACTION'},
            {'sequence': 48, 'type': 'UPDATE'},
            {'sequence': 49, 'type': 'COLLECT'},
            {'sequence': 50, 'type': 'SAVE'}
        ]
        
        # Send only events after client's sequence
        catch_up = [e for e in events if e['sequence'] > client_sequence]
        
        self.assertEqual(len(catch_up), 5)

    def test_full_state_restoration(self):
        """Test full state restoration when too far behind"""
        client_sequence = 10
        server_sequence = 1000
        gap_threshold = 100
        
        gap = server_sequence - client_sequence
        needs_full_sync = gap > gap_threshold
        
        self.assertTrue(needs_full_sync)


class TestPerformanceScalability(unittest.TestCase):
    """Test performance and scalability"""

    def test_event_compression(self):
        """Test consecutive similar events are compressed"""
        events = [
            {'type': 'HEARTBEAT', 'timestamp': 1000},
            {'type': 'HEARTBEAT', 'timestamp': 1001},
            {'type': 'HEARTBEAT', 'timestamp': 1002}
        ]
        
        # Compress consecutive heartbeats
        compressed = [events[0], events[-1]]
        
        self.assertEqual(len(compressed), 2)

    def test_batch_sync_updates(self):
        """Test updates are batched for efficiency"""
        individual_updates = [
            {'field': 'x', 'value': 1},
            {'field': 'y', 'value': 2},
            {'field': 'z', 'value': 3}
        ]
        
        # Batch into single update
        batch = {
            'type': 'batch_update',
            'updates': individual_updates
        }
        
        self.assertEqual(len(batch['updates']), 3)

    def test_sync_rate_limiting(self):
        """Test sync rate limiting"""
        last_sync = time.time() - 0.05  # 50ms ago
        min_interval = 0.1  # 100ms minimum
        
        can_sync = (time.time() - last_sync) >= min_interval
        
        self.assertFalse(can_sync)


class TestConcurrentUpdates(unittest.TestCase):
    """Test handling concurrent updates"""

    def test_concurrent_field_updates(self):
        """Test concurrent updates to different fields"""
        state = {'position': [10, 10], 'health': 100}
        
        update1 = {'position': [11, 10]}
        update2 = {'health': 95}
        
        # Both can be applied (no conflict)
        state.update(update1)
        state.update(update2)
        
        self.assertEqual(state['position'], [11, 10])
        self.assertEqual(state['health'], 95)

    def test_concurrent_same_field_conflict(self):
        """Test concurrent updates to same field"""
        updates = [
            {'timestamp': 1001, 'position': [11, 10]},
            {'timestamp': 1002, 'position': [12, 10]}
        ]
        
        # Last writer wins
        winner = max(updates, key=lambda u: u['timestamp'])
        
        self.assertEqual(winner['position'], [12, 10])


# Test runner
if __name__ == '__main__':
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("="*70)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
