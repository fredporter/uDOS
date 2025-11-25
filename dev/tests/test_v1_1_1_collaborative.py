"""
Test Suite for v1.1.1.8 - Collaborative Features
Tests: WebRTC, operational transforms, CRDTs, real-time collaboration

Test Coverage (60 tests total):
- WebRTC Connection: 10 tests
- Operational Transforms: 12 tests
- CRDTs: 12 tests
- Barter Negotiation: 10 tests
- Mission Planning: 8 tests
- Conflict Resolution: 8 tests

Author: uDOS Development Team
Version: 1.1.1.8
Date: 2025-11-24
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import json
from datetime import datetime
from typing import Dict, List, Any

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))


class Operation:
    """Represents an operational transform operation"""

    def __init__(self, op_type: str, position: int, content: str, user_id: str, timestamp: float):
        self.op_type = op_type  # 'insert' or 'delete'
        self.position = position
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'type': self.op_type,
            'position': self.position,
            'content': self.content,
            'user_id': self.user_id,
            'timestamp': self.timestamp
        }


class OperationalTransform:
    """Operational Transform engine for concurrent text editing"""

    def __init__(self):
        self.document = ""
        self.history = []

    def apply(self, operation: Operation) -> bool:
        """Apply an operation to the document"""
        try:
            if operation.op_type == 'insert':
                # Validate position
                if operation.position < 0 or operation.position > len(self.document):
                    return False
                self.document = (
                    self.document[:operation.position] +
                    operation.content +
                    self.document[operation.position:]
                )
            elif operation.op_type == 'delete':
                end_pos = operation.position + len(operation.content)
                # Validate position and range
                if operation.position < 0 or end_pos > len(self.document):
                    return False
                self.document = (
                    self.document[:operation.position] +
                    self.document[end_pos:]
                )
            else:
                return False
            self.history.append(operation)
            return True
        except Exception:
            return False

    def transform(self, op1: Operation, op2: Operation) -> Operation:
        """Transform op1 against op2 (both applied concurrently)"""
        if op2.op_type == 'insert':
            if op1.position >= op2.position:
                # Shift op1 position to account for op2's insertion
                return Operation(
                    op1.op_type,
                    op1.position + len(op2.content),
                    op1.content,
                    op1.user_id,
                    op1.timestamp
                )
        elif op2.op_type == 'delete':
            if op1.position >= op2.position + len(op2.content):
                # Shift op1 position to account for op2's deletion
                return Operation(
                    op1.op_type,
                    op1.position - len(op2.content),
                    op1.content,
                    op1.user_id,
                    op1.timestamp
                )
        return op1


class GCounter:
    """Grow-only counter CRDT"""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts = {node_id: 0}

    def increment(self, amount: int = 1):
        """Increment local counter"""
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + amount

    def merge(self, other: 'GCounter'):
        """Merge with another GCounter"""
        for node_id, count in other.counts.items():
            self.counts[node_id] = max(self.counts.get(node_id, 0), count)

    def value(self) -> int:
        """Get total count"""
        return sum(self.counts.values())


class LWWRegister:
    """Last-Writer-Wins Register CRDT"""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.value = None
        self.timestamp = 0
        self.writer = None

    def set(self, value: Any, timestamp: float = None):
        """Set value with timestamp"""
        ts = timestamp or datetime.now().timestamp()
        if ts > self.timestamp:
            self.value = value
            self.timestamp = ts
            self.writer = self.node_id

    def merge(self, other: 'LWWRegister'):
        """Merge with another register (last writer wins)"""
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp
            self.writer = other.writer

    def get(self) -> Any:
        """Get current value"""
        return self.value


class GSet:
    """Grow-only Set CRDT"""

    def __init__(self):
        self.elements = set()

    def add(self, element: Any):
        """Add element to set"""
        self.elements.add(element)

    def merge(self, other: 'GSet'):
        """Merge with another GSet"""
        self.elements.update(other.elements)

    def contains(self, element: Any) -> bool:
        """Check if element exists"""
        return element in self.elements

    def to_list(self) -> list:
        """Convert to list"""
        return list(self.elements)


class WebRTCConnection:
    """Simulated WebRTC connection for P2P communication"""

    def __init__(self, local_id: str):
        self.local_id = local_id
        self.peer_id = None
        self.state = 'new'  # new, connecting, connected, disconnected, failed
        self.data_channel = None
        self.ice_candidates = []
        self.remote_description = None
        self.local_description = None

    def create_offer(self) -> Dict:
        """Create SDP offer"""
        self.local_description = {'type': 'offer', 'sdp': f'offer-{self.local_id}'}
        return self.local_description

    def create_answer(self) -> Dict:
        """Create SDP answer"""
        self.local_description = {'type': 'answer', 'sdp': f'answer-{self.local_id}'}
        return self.local_description

    def set_remote_description(self, description: Dict):
        """Set remote peer's SDP"""
        self.remote_description = description
        self.state = 'connecting'

    def add_ice_candidate(self, candidate: Dict):
        """Add ICE candidate"""
        self.ice_candidates.append(candidate)

    def create_data_channel(self, label: str) -> Dict:
        """Create data channel for sending data"""
        self.data_channel = {'label': label, 'state': 'open', 'messages': []}
        return self.data_channel

    def send(self, data: Any):
        """Send data through channel"""
        if self.data_channel and self.data_channel['state'] == 'open':
            self.data_channel['messages'].append(data)
            return True
        return False

    def connect(self, peer_id: str):
        """Simulate connection establishment"""
        self.peer_id = peer_id
        self.state = 'connected'


class BarterNegotiation:
    """Real-time barter negotiation session"""

    def __init__(self, session_id: str, participants: List[str]):
        self.session_id = session_id
        self.participants = participants
        self.offers = {}  # {user_id: offer_data}
        self.counter_offers = []
        self.messages = []
        self.status = 'active'  # active, accepted, rejected, cancelled

    def add_offer(self, user_id: str, offer: Dict):
        """Add or update offer"""
        self.offers[user_id] = {
            'offer': offer,
            'timestamp': datetime.now().timestamp()
        }

    def add_counter_offer(self, from_user: str, to_user: str, terms: Dict):
        """Add counter-offer"""
        self.counter_offers.append({
            'from': from_user,
            'to': to_user,
            'terms': terms,
            'timestamp': datetime.now().timestamp()
        })

    def send_message(self, user_id: str, message: str):
        """Send chat message"""
        self.messages.append({
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now().timestamp()
        })

    def accept(self, user_id: str):
        """Accept negotiation"""
        if user_id in self.participants:
            self.status = 'accepted'
            return True
        return False

    def reject(self, user_id: str):
        """Reject negotiation"""
        if user_id in self.participants:
            self.status = 'rejected'
            return True
        return False


class MissionPlanningSession:
    """Collaborative mission planning"""

    def __init__(self, mission_id: str, owner: str):
        self.mission_id = mission_id
        self.owner = owner
        self.collaborators = set()
        self.objectives = GSet()
        self.resources = {}
        self.assignments = {}
        self.timeline = []
        self.notes = OperationalTransform()

    def add_collaborator(self, user_id: str):
        """Add collaborator to mission"""
        self.collaborators.add(user_id)

    def add_objective(self, objective: str):
        """Add mission objective (CRDT)"""
        self.objectives.add(objective)

    def assign_task(self, task: str, user_id: str):
        """Assign task to user"""
        self.assignments[task] = user_id

    def add_resource(self, resource: str, quantity: int):
        """Add resource requirement"""
        if resource not in self.resources:
            self.resources[resource] = GCounter(self.owner)
        self.resources[resource].increment(quantity)

    def add_timeline_event(self, event: Dict):
        """Add event to timeline"""
        self.timeline.append({
            **event,
            'timestamp': datetime.now().timestamp()
        })


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestWebRTCConnection(unittest.TestCase):
    """Test WebRTC connection establishment (10 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.peer1 = WebRTCConnection('peer1')
        self.peer2 = WebRTCConnection('peer2')

    def test_connection_initialization(self):
        """Test WebRTC connection initialization"""
        self.assertEqual(self.peer1.state, 'new')
        self.assertIsNone(self.peer1.peer_id)
        self.assertIsNone(self.peer1.data_channel)

    def test_create_offer(self):
        """Test SDP offer creation"""
        offer = self.peer1.create_offer()
        self.assertEqual(offer['type'], 'offer')
        self.assertIn('peer1', offer['sdp'])

    def test_create_answer(self):
        """Test SDP answer creation"""
        answer = self.peer2.create_answer()
        self.assertEqual(answer['type'], 'answer')
        self.assertIn('peer2', answer['sdp'])

    def test_set_remote_description(self):
        """Test setting remote SDP description"""
        offer = self.peer1.create_offer()
        self.peer2.set_remote_description(offer)
        self.assertEqual(self.peer2.remote_description, offer)
        self.assertEqual(self.peer2.state, 'connecting')

    def test_ice_candidate_exchange(self):
        """Test ICE candidate addition"""
        candidate = {'candidate': 'test-candidate', 'sdpMid': '0'}
        self.peer1.add_ice_candidate(candidate)
        self.assertIn(candidate, self.peer1.ice_candidates)

    def test_data_channel_creation(self):
        """Test data channel creation"""
        channel = self.peer1.create_data_channel('collaboration')
        self.assertEqual(channel['label'], 'collaboration')
        self.assertEqual(channel['state'], 'open')

    def test_send_data(self):
        """Test sending data through channel"""
        self.peer1.create_data_channel('test')
        result = self.peer1.send({'type': 'message', 'data': 'hello'})
        self.assertTrue(result)
        self.assertEqual(len(self.peer1.data_channel['messages']), 1)

    def test_send_without_channel(self):
        """Test sending data without channel fails gracefully"""
        result = self.peer1.send({'data': 'test'})
        self.assertFalse(result)

    def test_connection_establishment(self):
        """Test full connection flow"""
        self.peer1.connect('peer2')
        self.assertEqual(self.peer1.state, 'connected')
        self.assertEqual(self.peer1.peer_id, 'peer2')

    def test_bidirectional_setup(self):
        """Test bidirectional connection setup"""
        offer = self.peer1.create_offer()
        self.peer2.set_remote_description(offer)
        answer = self.peer2.create_answer()
        self.peer1.set_remote_description(answer)

        self.assertIsNotNone(self.peer1.remote_description)
        self.assertIsNotNone(self.peer2.remote_description)


class TestOperationalTransforms(unittest.TestCase):
    """Test operational transform engine (12 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.ot = OperationalTransform()
        self.timestamp = datetime.now().timestamp()

    def test_insert_operation(self):
        """Test inserting text"""
        op = Operation('insert', 0, 'Hello', 'user1', self.timestamp)
        result = self.ot.apply(op)
        self.assertTrue(result)
        self.assertEqual(self.ot.document, 'Hello')

    def test_delete_operation(self):
        """Test deleting text"""
        self.ot.document = 'Hello World'
        op = Operation('delete', 6, 'World', 'user1', self.timestamp)
        result = self.ot.apply(op)
        self.assertTrue(result)
        self.assertEqual(self.ot.document, 'Hello ')

    def test_multiple_inserts(self):
        """Test multiple sequential insertions"""
        op1 = Operation('insert', 0, 'Hello', 'user1', self.timestamp)
        op2 = Operation('insert', 5, ' World', 'user1', self.timestamp + 1)

        self.ot.apply(op1)
        self.ot.apply(op2)
        self.assertEqual(self.ot.document, 'Hello World')

    def test_insert_middle(self):
        """Test inserting in the middle"""
        self.ot.document = 'HelloWorld'
        op = Operation('insert', 5, ' ', 'user1', self.timestamp)
        self.ot.apply(op)
        self.assertEqual(self.ot.document, 'Hello World')

    def test_transform_concurrent_inserts(self):
        """Test transforming concurrent insertions"""
        op1 = Operation('insert', 5, 'A', 'user1', self.timestamp)
        op2 = Operation('insert', 5, 'B', 'user2', self.timestamp)

        transformed = self.ot.transform(op1, op2)
        self.assertEqual(transformed.position, 6)  # Shifted by op2

    def test_transform_insert_after_delete(self):
        """Test transforming insert after delete"""
        op1 = Operation('insert', 10, 'text', 'user1', self.timestamp)
        op2 = Operation('delete', 5, 'abc', 'user2', self.timestamp)

        transformed = self.ot.transform(op1, op2)
        self.assertEqual(transformed.position, 7)  # 10 - 3

    def test_operation_history(self):
        """Test operation history tracking"""
        op1 = Operation('insert', 0, 'A', 'user1', self.timestamp)
        op2 = Operation('insert', 1, 'B', 'user1', self.timestamp + 1)

        self.ot.apply(op1)
        self.ot.apply(op2)
        self.assertEqual(len(self.ot.history), 2)

    def test_concurrent_edits_same_position(self):
        """Test concurrent edits at same position"""
        self.ot.document = 'Start'

        op1 = Operation('insert', 5, ' A', 'user1', self.timestamp)
        op2 = Operation('insert', 5, ' B', 'user2', self.timestamp)

        self.ot.apply(op1)
        # Transform op2 against op1
        op2_transformed = self.ot.transform(op2, op1)
        self.ot.apply(op2_transformed)

        self.assertIn('A', self.ot.document)
        self.assertIn('B', self.ot.document)

    def test_delete_entire_document(self):
        """Test deleting entire document"""
        self.ot.document = 'Delete me'
        op = Operation('delete', 0, 'Delete me', 'user1', self.timestamp)
        self.ot.apply(op)
        self.assertEqual(self.ot.document, '')

    def test_operation_serialization(self):
        """Test operation serialization"""
        op = Operation('insert', 5, 'text', 'user1', self.timestamp)
        data = op.to_dict()

        self.assertEqual(data['type'], 'insert')
        self.assertEqual(data['position'], 5)
        self.assertEqual(data['content'], 'text')
        self.assertEqual(data['user_id'], 'user1')

    def test_invalid_operation(self):
        """Test handling invalid operations"""
        op = Operation('delete', 100, 'invalid', 'user1', self.timestamp)
        result = self.ot.apply(op)
        self.assertFalse(result)

    def test_transform_no_conflict(self):
        """Test transform when operations don't conflict"""
        op1 = Operation('insert', 0, 'A', 'user1', self.timestamp)
        op2 = Operation('insert', 10, 'B', 'user2', self.timestamp)

        transformed = self.ot.transform(op1, op2)
        self.assertEqual(transformed.position, op1.position)


class TestCRDTs(unittest.TestCase):
    """Test Conflict-free Replicated Data Types (12 tests)"""

    def test_gcounter_increment(self):
        """Test GCounter increment operation"""
        counter = GCounter('node1')
        counter.increment(5)
        self.assertEqual(counter.value(), 5)

    def test_gcounter_merge(self):
        """Test GCounter merge operation"""
        counter1 = GCounter('node1')
        counter2 = GCounter('node2')

        counter1.increment(3)
        counter2.increment(7)

        counter1.merge(counter2)
        self.assertEqual(counter1.value(), 10)

    def test_gcounter_merge_same_node(self):
        """Test GCounter merge with same node (max wins)"""
        counter1 = GCounter('node1')
        counter2 = GCounter('node1')

        counter1.increment(5)
        counter2.increment(3)

        counter1.merge(counter2)
        self.assertEqual(counter1.value(), 5)  # Max of 5 and 3

    def test_lww_register_set(self):
        """Test LWW Register set operation"""
        register = LWWRegister('node1')
        register.set('value1', 100)

        self.assertEqual(register.get(), 'value1')
        self.assertEqual(register.timestamp, 100)

    def test_lww_register_merge_later_wins(self):
        """Test LWW Register merge (later timestamp wins)"""
        reg1 = LWWRegister('node1')
        reg2 = LWWRegister('node2')

        reg1.set('old', 100)
        reg2.set('new', 200)

        reg1.merge(reg2)
        self.assertEqual(reg1.get(), 'new')

    def test_lww_register_merge_earlier_ignored(self):
        """Test LWW Register merge (earlier timestamp ignored)"""
        reg1 = LWWRegister('node1')
        reg2 = LWWRegister('node2')

        reg1.set('new', 200)
        reg2.set('old', 100)

        reg1.merge(reg2)
        self.assertEqual(reg1.get(), 'new')

    def test_gset_add(self):
        """Test GSet add operation"""
        gset = GSet()
        gset.add('element1')
        gset.add('element2')

        self.assertTrue(gset.contains('element1'))
        self.assertTrue(gset.contains('element2'))

    def test_gset_add_duplicate(self):
        """Test GSet add duplicate (idempotent)"""
        gset = GSet()
        gset.add('item')
        gset.add('item')

        elements = gset.to_list()
        self.assertEqual(len(elements), 1)

    def test_gset_merge(self):
        """Test GSet merge operation"""
        set1 = GSet()
        set2 = GSet()

        set1.add('A')
        set1.add('B')
        set2.add('C')
        set2.add('D')

        set1.merge(set2)
        self.assertEqual(len(set1.to_list()), 4)

    def test_gset_merge_overlap(self):
        """Test GSet merge with overlapping elements"""
        set1 = GSet()
        set2 = GSet()

        set1.add('A')
        set1.add('B')
        set2.add('B')
        set2.add('C')

        set1.merge(set2)
        elements = set1.to_list()
        self.assertEqual(len(elements), 3)  # A, B, C

    def test_gcounter_multiple_nodes(self):
        """Test GCounter with multiple nodes"""
        counter1 = GCounter('node1')
        counter2 = GCounter('node2')
        counter3 = GCounter('node3')

        counter1.increment(1)
        counter2.increment(2)
        counter3.increment(3)

        counter1.merge(counter2)
        counter1.merge(counter3)

        self.assertEqual(counter1.value(), 6)

    def test_lww_register_writer_tracking(self):
        """Test LWW Register tracks last writer"""
        reg = LWWRegister('node1')
        reg.set('value', 100)

        self.assertEqual(reg.writer, 'node1')


class TestBarterNegotiation(unittest.TestCase):
    """Test real-time barter negotiation (10 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.negotiation = BarterNegotiation('session1', ['user1', 'user2'])

    def test_negotiation_initialization(self):
        """Test negotiation session creation"""
        self.assertEqual(self.negotiation.session_id, 'session1')
        self.assertEqual(len(self.negotiation.participants), 2)
        self.assertEqual(self.negotiation.status, 'active')

    def test_add_offer(self):
        """Test adding offer to negotiation"""
        offer = {'item': 'Solar Panel', 'quantity': 1}
        self.negotiation.add_offer('user1', offer)

        self.assertIn('user1', self.negotiation.offers)
        self.assertEqual(self.negotiation.offers['user1']['offer'], offer)

    def test_update_offer(self):
        """Test updating existing offer"""
        offer1 = {'item': 'Tool', 'quantity': 1}
        offer2 = {'item': 'Tool', 'quantity': 2}

        self.negotiation.add_offer('user1', offer1)
        self.negotiation.add_offer('user1', offer2)

        self.assertEqual(self.negotiation.offers['user1']['offer']['quantity'], 2)

    def test_add_counter_offer(self):
        """Test adding counter-offer"""
        terms = {'item': 'Water Filter', 'plus': 'Manual'}
        self.negotiation.add_counter_offer('user1', 'user2', terms)

        self.assertEqual(len(self.negotiation.counter_offers), 1)
        self.assertEqual(self.negotiation.counter_offers[0]['from'], 'user1')

    def test_send_message(self):
        """Test sending chat message"""
        self.negotiation.send_message('user1', 'What about tools?')

        self.assertEqual(len(self.negotiation.messages), 1)
        self.assertEqual(self.negotiation.messages[0]['message'], 'What about tools?')

    def test_accept_negotiation(self):
        """Test accepting negotiation"""
        result = self.negotiation.accept('user1')

        self.assertTrue(result)
        self.assertEqual(self.negotiation.status, 'accepted')

    def test_reject_negotiation(self):
        """Test rejecting negotiation"""
        result = self.negotiation.reject('user2')

        self.assertTrue(result)
        self.assertEqual(self.negotiation.status, 'rejected')

    def test_invalid_participant_accept(self):
        """Test accept from non-participant fails"""
        result = self.negotiation.accept('user3')
        self.assertFalse(result)

    def test_multiple_messages(self):
        """Test multiple chat messages"""
        self.negotiation.send_message('user1', 'Message 1')
        self.negotiation.send_message('user2', 'Message 2')
        self.negotiation.send_message('user1', 'Message 3')

        self.assertEqual(len(self.negotiation.messages), 3)

    def test_complex_negotiation_flow(self):
        """Test complex negotiation workflow"""
        # Initial offers
        self.negotiation.add_offer('user1', {'item': 'Seeds', 'qty': 100})
        self.negotiation.add_offer('user2', {'item': 'Tools', 'qty': 5})

        # Counter-offer
        self.negotiation.add_counter_offer('user1', 'user2',
                                          {'item': 'Tools', 'qty': 7})

        # Chat
        self.negotiation.send_message('user2', 'Can do 6 tools')

        # Accept
        self.negotiation.accept('user1')

        self.assertEqual(len(self.negotiation.offers), 2)
        self.assertEqual(len(self.negotiation.counter_offers), 1)
        self.assertEqual(len(self.negotiation.messages), 1)
        self.assertEqual(self.negotiation.status, 'accepted')


class TestMissionPlanning(unittest.TestCase):
    """Test collaborative mission planning (8 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.mission = MissionPlanningSession('mission1', 'user1')

    def test_mission_initialization(self):
        """Test mission planning session creation"""
        self.assertEqual(self.mission.mission_id, 'mission1')
        self.assertEqual(self.mission.owner, 'user1')
        self.assertEqual(len(self.mission.collaborators), 0)

    def test_add_collaborator(self):
        """Test adding collaborators"""
        self.mission.add_collaborator('user2')
        self.mission.add_collaborator('user3')

        self.assertEqual(len(self.mission.collaborators), 2)
        self.assertIn('user2', self.mission.collaborators)

    def test_add_objective(self):
        """Test adding mission objectives (CRDT)"""
        self.mission.add_objective('Secure water source')
        self.mission.add_objective('Build shelter')

        objectives = self.mission.objectives.to_list()
        self.assertEqual(len(objectives), 2)

    def test_assign_task(self):
        """Test task assignment"""
        self.mission.assign_task('Scout location', 'user2')
        self.mission.assign_task('Gather supplies', 'user3')

        self.assertEqual(self.mission.assignments['Scout location'], 'user2')
        self.assertEqual(len(self.mission.assignments), 2)

    def test_add_resource(self):
        """Test adding resources (CRDT counter)"""
        self.mission.add_resource('Water', 10)
        self.mission.add_resource('Food', 5)

        self.assertEqual(self.mission.resources['Water'].value(), 10)
        self.assertEqual(self.mission.resources['Food'].value(), 5)

    def test_add_timeline_event(self):
        """Test adding timeline events"""
        event1 = {'type': 'milestone', 'description': 'Day 1 complete'}
        event2 = {'type': 'checkpoint', 'description': 'Resources secured'}

        self.mission.add_timeline_event(event1)
        self.mission.add_timeline_event(event2)

        self.assertEqual(len(self.mission.timeline), 2)
        self.assertEqual(self.mission.timeline[0]['type'], 'milestone')

    def test_collaborative_notes(self):
        """Test collaborative notes (OT)"""
        op1 = Operation('insert', 0, 'Mission: ', 'user1',
                       datetime.now().timestamp())
        op2 = Operation('insert', 9, 'Find shelter', 'user1',
                       datetime.now().timestamp())

        self.mission.notes.apply(op1)
        self.mission.notes.apply(op2)

        self.assertEqual(self.mission.notes.document, 'Mission: Find shelter')

    def test_full_mission_workflow(self):
        """Test complete mission planning workflow"""
        # Add collaborators
        self.mission.add_collaborator('user2')
        self.mission.add_collaborator('user3')

        # Add objectives (CRDT GSet)
        self.mission.add_objective('Water')
        self.mission.add_objective('Shelter')
        self.mission.add_objective('Food')

        # Assign tasks
        self.mission.assign_task('Water scout', 'user2')
        self.mission.assign_task('Shelter build', 'user3')

        # Add resources (CRDT GCounter)
        self.mission.add_resource('Tools', 5)
        self.mission.add_resource('Materials', 20)

        # Timeline
        self.mission.add_timeline_event({
            'type': 'start',
            'description': 'Mission begins'
        })

        # Verify
        self.assertEqual(len(self.mission.collaborators), 2)
        self.assertEqual(len(self.mission.objectives.to_list()), 3)
        self.assertEqual(len(self.mission.assignments), 2)
        self.assertEqual(self.mission.resources['Tools'].value(), 5)
        self.assertEqual(len(self.mission.timeline), 1)


class TestConflictResolution(unittest.TestCase):
    """Test conflict resolution strategies (8 tests)"""

    def test_lww_conflict_resolution(self):
        """Test last-writer-wins conflict resolution"""
        reg1 = LWWRegister('node1')
        reg2 = LWWRegister('node2')

        # Concurrent writes
        reg1.set('value_a', 100)
        reg2.set('value_b', 101)  # Later timestamp

        # Merge - later wins
        reg1.merge(reg2)
        self.assertEqual(reg1.get(), 'value_b')

    def test_crdt_counter_convergence(self):
        """Test CRDT counter convergence"""
        c1 = GCounter('node1')
        c2 = GCounter('node2')
        c3 = GCounter('node3')

        # Each node increments
        c1.increment(1)
        c2.increment(2)
        c3.increment(3)

        # Merge all
        c1.merge(c2)
        c1.merge(c3)

        c2.merge(c1)
        c3.merge(c1)

        # All should converge to same value
        self.assertEqual(c1.value(), 6)
        self.assertEqual(c2.value(), 6)
        self.assertEqual(c3.value(), 6)

    def test_ot_concurrent_edits(self):
        """Test OT handles concurrent edits"""
        doc1 = OperationalTransform()
        doc2 = OperationalTransform()

        # Both start with same doc
        doc1.document = doc2.document = 'Hello'

        ts = datetime.now().timestamp()

        # Concurrent operations
        op1 = Operation('insert', 5, ' World', 'user1', ts)
        op2 = Operation('insert', 0, 'Say ', 'user2', ts)

        # Apply to respective docs
        doc1.apply(op1)
        doc2.apply(op2)

        # Transform and apply opposite operations
        op1_transformed = doc2.transform(op1, op2)
        op2_transformed = doc1.transform(op2, op1)

        doc1.apply(op2_transformed)
        doc2.apply(op1_transformed)

        # Both should converge
        self.assertEqual(doc1.document, doc2.document)

    def test_gset_merge_idempotent(self):
        """Test GSet merge is idempotent"""
        set1 = GSet()
        set2 = GSet()

        set1.add('A')
        set2.add('B')

        # Merge multiple times
        set1.merge(set2)
        set1.merge(set2)
        set1.merge(set2)

        # Should still have 2 elements
        self.assertEqual(len(set1.to_list()), 2)

    def test_commutative_merge(self):
        """Test CRDT merge is commutative"""
        c1 = GCounter('n1')
        c2 = GCounter('n2')
        c1_copy = GCounter('n1')
        c2_copy = GCounter('n2')

        c1.increment(3)
        c2.increment(5)
        c1_copy.increment(3)
        c2_copy.increment(5)

        # Merge in different orders
        c1.merge(c2)
        c2_copy.merge(c1_copy)

        # Should get same result
        self.assertEqual(c1.value(), c2_copy.value())

    def test_associative_merge(self):
        """Test CRDT merge is associative"""
        c1 = GCounter('n1')
        c2 = GCounter('n2')
        c3 = GCounter('n3')

        c1.increment(1)
        c2.increment(2)
        c3.increment(3)

        # (c1 ∪ c2) ∪ c3
        temp = GCounter('temp')
        temp.counts = c1.counts.copy()
        temp.merge(c2)
        temp.merge(c3)
        result1 = temp.value()

        # c1 ∪ (c2 ∪ c3)
        temp2 = GCounter('temp2')
        temp2.counts = c2.counts.copy()
        temp2.merge(c3)

        temp3 = GCounter('temp3')
        temp3.counts = c1.counts.copy()
        temp3.merge(temp2)
        result2 = temp3.value()

        # Should be equal
        self.assertEqual(result1, result2)

    def test_mission_resource_conflict(self):
        """Test mission resource conflict resolution"""
        mission1 = MissionPlanningSession('m1', 'user1')
        mission2 = MissionPlanningSession('m1', 'user2')

        # Both add resources concurrently
        mission1.add_resource('Water', 10)
        mission2.add_resource('Water', 5)

        # Merge counters
        mission1.resources['Water'].merge(mission2.resources['Water'])

        # Should sum (CRDT GCounter)
        self.assertEqual(mission1.resources['Water'].value(), 15)

    def test_negotiation_timestamp_ordering(self):
        """Test negotiation uses timestamp for ordering"""
        neg = BarterNegotiation('s1', ['u1', 'u2'])

        import time

        neg.add_offer('u1', {'item': 'A'})
        time.sleep(0.001)
        neg.add_offer('u2', {'item': 'B'})

        # Check timestamps are ordered
        ts1 = neg.offers['u1']['timestamp']
        ts2 = neg.offers['u2']['timestamp']

        self.assertLess(ts1, ts2)


def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebRTCConnection))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationalTransforms))
    suite.addTests(loader.loadTestsFromTestCase(TestCRDTs))
    suite.addTests(loader.loadTestsFromTestCase(TestBarterNegotiation))
    suite.addTests(loader.loadTestsFromTestCase(TestMissionPlanning))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictResolution))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
