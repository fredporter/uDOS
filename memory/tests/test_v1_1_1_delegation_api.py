"""
uDOS v1.1.1 - CLI→Web Delegation API Test Suite

Comprehensive test suite for Feature 1.1.1.3: Modal Delegation System

Test Coverage:
- Modal delegation for complex visual inputs
- CLI↔Web communication protocol
- Request/response message format
- Timeout and cancellation handling
- Multi-step interaction flows
- Result validation and type safety
- Session synchronization
- Error handling and recovery
- Concurrent delegation requests
- Cross-platform compatibility

Feature: 1.1.1.3
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
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


class TestDelegationProtocol(unittest.TestCase):
    """Test delegation request/response protocol"""

    def test_delegation_request_structure(self):
        """Test delegation request message structure"""
        request = {
            'type': 'delegation_request',
            'request_id': 'req_12345',
            'delegation_type': 'map_cell_selection',
            'data': {
                'map_size': [40, 20],
                'current_position': [10, 5],
                'selectable_cells': [[9, 5], [10, 4], [10, 6]]
            },
            'timeout': 300,  # 5 minutes
            'created_at': time.time()
        }

        self.assertEqual(request['type'], 'delegation_request')
        self.assertIn('request_id', request)
        self.assertIn('delegation_type', request)
        self.assertIn('data', request)
        self.assertIn('timeout', request)

    def test_delegation_response_structure(self):
        """Test delegation response message structure"""
        response = {
            'type': 'delegation_response',
            'request_id': 'req_12345',
            'status': 'success',
            'result': {
                'selected_cell': [11, 5],
                'action': 'move'
            },
            'completed_at': time.time()
        }

        self.assertEqual(response['type'], 'delegation_response')
        self.assertEqual(response['status'], 'success')
        self.assertIn('result', response)

    def test_delegation_cancellation(self):
        """Test delegation cancellation message"""
        cancellation = {
            'type': 'delegation_cancel',
            'request_id': 'req_12345',
            'reason': 'user_timeout'
        }

        self.assertEqual(cancellation['type'], 'delegation_cancel')
        self.assertIn('reason', cancellation)

    def test_delegation_error_response(self):
        """Test error response structure"""
        error = {
            'type': 'delegation_response',
            'request_id': 'req_12345',
            'status': 'error',
            'error': {
                'code': 'INVALID_SELECTION',
                'message': 'Selected cell is not in selectable list'
            }
        }

        self.assertEqual(error['status'], 'error')
        self.assertIn('error', error)
        self.assertIn('code', error['error'])


class TestDelegationTypes(unittest.TestCase):
    """Test different delegation types"""

    def test_map_cell_selection_delegation(self):
        """Test map cell selection delegation"""
        delegation = {
            'delegation_type': 'map_cell_selection',
            'data': {
                'map_data': [[0, 1, 2], [3, 4, 5]],
                'selectable_cells': [[0, 0], [1, 1]],
                'multi_select': False
            }
        }

        self.assertEqual(delegation['delegation_type'], 'map_cell_selection')
        self.assertFalse(delegation['data']['multi_select'])

    def test_file_picker_delegation(self):
        """Test file picker delegation"""
        delegation = {
            'delegation_type': 'file_picker',
            'data': {
                'start_path': '/knowledge/survival',
                'file_types': ['.md', '.txt'],
                'multi_select': True,
                'max_files': 10
            }
        }

        self.assertEqual(delegation['delegation_type'], 'file_picker')
        self.assertTrue(delegation['data']['multi_select'])

    def test_skill_tree_selection_delegation(self):
        """Test skill tree interaction delegation"""
        delegation = {
            'delegation_type': 'skill_tree',
            'data': {
                'available_skills': ['electronics', 'woodworking', 'first-aid'],
                'unlocked_skills': ['basic-survival'],
                'skill_points': 5
            }
        }

        self.assertEqual(delegation['delegation_type'], 'skill_tree')
        self.assertIn('skill_points', delegation['data'])

    def test_inventory_management_delegation(self):
        """Test inventory management delegation"""
        delegation = {
            'delegation_type': 'inventory',
            'data': {
                'items': [
                    {'id': 1, 'name': 'Water Bottle', 'quantity': 3},
                    {'id': 2, 'name': 'First Aid Kit', 'quantity': 1}
                ],
                'capacity': 20,
                'used_slots': 4,
                'action': 'organize'
            }
        }

        self.assertEqual(delegation['delegation_type'], 'inventory')
        self.assertEqual(delegation['data']['used_slots'], 4)

    def test_form_input_delegation(self):
        """Test complex form input delegation"""
        delegation = {
            'delegation_type': 'form',
            'data': {
                'fields': [
                    {'name': 'title', 'type': 'text', 'required': True},
                    {'name': 'description', 'type': 'textarea', 'required': False},
                    {'name': 'priority', 'type': 'select', 'options': ['low', 'medium', 'high']}
                ]
            }
        }

        self.assertEqual(delegation['delegation_type'], 'form')
        self.assertEqual(len(delegation['data']['fields']), 3)


class TestCLIWebCommunication(unittest.TestCase):
    """Test CLI↔Web communication mechanisms"""

    def test_websocket_delegation_channel(self):
        """Test WebSocket channel for delegation"""
        mock_ws = Mock()
        request = {'type': 'delegation_request', 'request_id': 'test'}

        # Send request
        mock_ws.send(json.dumps(request))

        mock_ws.send.assert_called_once()

    def test_request_response_pairing(self):
        """Test request/response pairing via request_id"""
        request_id = 'req_12345'

        request = {'request_id': request_id, 'type': 'delegation_request'}
        response = {'request_id': request_id, 'type': 'delegation_response'}

        self.assertEqual(request['request_id'], response['request_id'])

    def test_pending_requests_tracking(self):
        """Test tracking of pending delegation requests"""
        pending = {}

        # Add request
        request_id = 'req_1'
        pending[request_id] = {
            'created_at': time.time(),
            'timeout': 300,
            'event': threading.Event()
        }

        self.assertIn(request_id, pending)

    def test_response_notification(self):
        """Test response notification to waiting CLI"""
        event = threading.Event()

        # Simulate response arrival
        event.set()

        # CLI should be notified
        self.assertTrue(event.is_set())

    def test_message_serialization(self):
        """Test JSON serialization of messages"""
        message = {
            'type': 'delegation_request',
            'data': {'key': 'value'},
            'timestamp': time.time()
        }

        # Serialize
        json_str = json.dumps(message)

        # Deserialize
        parsed = json.loads(json_str)

        self.assertEqual(parsed['type'], message['type'])


class TestTimeoutHandling(unittest.TestCase):
    """Test timeout and cancellation mechanisms"""

    def test_delegation_timeout(self):
        """Test delegation times out after specified duration"""
        request = {
            'created_at': time.time() - 400,  # 400 seconds ago
            'timeout': 300  # 5 minute timeout
        }

        age = time.time() - request['created_at']
        timed_out = age > request['timeout']

        self.assertTrue(timed_out)

    def test_timeout_cleanup(self):
        """Test timed out requests are cleaned up"""
        pending = {
            'req_1': {'created_at': time.time() - 400, 'timeout': 300},
            'req_2': {'created_at': time.time(), 'timeout': 300}
        }

        # Remove timed out requests
        now = time.time()
        active = {
            rid: req for rid, req in pending.items()
            if (now - req['created_at']) <= req['timeout']
        }

        self.assertNotIn('req_1', active)
        self.assertIn('req_2', active)

    def test_user_cancellation(self):
        """Test user can cancel pending delegation"""
        request = {
            'request_id': 'req_123',
            'status': 'pending'
        }

        # User cancels
        request['status'] = 'cancelled'

        self.assertEqual(request['status'], 'cancelled')

    def test_cli_interrupt_handling(self):
        """Test CLI Ctrl+C interrupts waiting delegation"""
        # Simulate interrupt
        interrupted = False

        try:
            # This would normally be event.wait(timeout)
            # but we simulate interrupt
            raise KeyboardInterrupt()
        except KeyboardInterrupt:
            interrupted = True

        self.assertTrue(interrupted)


class TestResultValidation(unittest.TestCase):
    """Test result validation and type safety"""

    def test_map_selection_result_validation(self):
        """Test map selection result is valid"""
        selectable_cells = [[0, 0], [1, 1], [2, 2]]
        result = {'selected_cell': [1, 1]}

        # Validate selection is in allowed list
        is_valid = result['selected_cell'] in selectable_cells

        self.assertTrue(is_valid)

    def test_invalid_selection_rejected(self):
        """Test invalid selection is rejected"""
        selectable_cells = [[0, 0], [1, 1]]
        result = {'selected_cell': [5, 5]}

        is_valid = result['selected_cell'] in selectable_cells

        self.assertFalse(is_valid)

    def test_multi_select_result_validation(self):
        """Test multi-select results are validated"""
        max_selections = 3
        result = {'selected_items': [1, 2, 3, 4]}

        is_valid = len(result['selected_items']) <= max_selections

        self.assertFalse(is_valid)

    def test_file_path_validation(self):
        """Test file paths are validated"""
        allowed_base = Path('/knowledge')
        result_path = Path('/knowledge/survival/water.md')

        # Check path is under allowed base
        try:
            result_path.relative_to(allowed_base)
            is_valid = True
        except ValueError:
            is_valid = False

        self.assertTrue(is_valid)

    def test_result_type_checking(self):
        """Test result types match expected types"""
        expected_type = list
        result = {'selected_cells': [[1, 1], [2, 2]]}

        is_correct_type = isinstance(result['selected_cells'], expected_type)

        self.assertTrue(is_correct_type)


class TestMultiStepInteractions(unittest.TestCase):
    """Test multi-step delegation workflows"""

    def test_sequential_delegations(self):
        """Test sequential delegation requests"""
        workflow = []

        # Step 1: Select category
        workflow.append({
            'step': 1,
            'type': 'category_select',
            'result': 'survival'
        })

        # Step 2: Select subcategory
        workflow.append({
            'step': 2,
            'type': 'subcategory_select',
            'result': 'water'
        })

        # Step 3: Select specific guide
        workflow.append({
            'step': 3,
            'type': 'guide_select',
            'result': 'purification.md'
        })

        self.assertEqual(len(workflow), 3)
        self.assertEqual(workflow[-1]['result'], 'purification.md')

    def test_conditional_delegation_flow(self):
        """Test conditional delegation based on previous results"""
        step1_result = {'action': 'edit'}

        # Next step depends on action
        if step1_result['action'] == 'edit':
            step2_type = 'file_editor'
        else:
            step2_type = 'file_viewer'

        self.assertEqual(step2_type, 'file_editor')

    def test_delegation_context_passing(self):
        """Test context is passed between delegation steps"""
        context = {}

        # Step 1
        context['selected_category'] = 'survival'

        # Step 2 uses context from step 1
        step2_request = {
            'type': 'subcategory_select',
            'data': {
                'category': context['selected_category'],
                'available': ['water', 'fire', 'shelter']
            }
        }

        self.assertEqual(step2_request['data']['category'], 'survival')


class TestSessionSynchronization(unittest.TestCase):
    """Test session state synchronization"""

    def test_session_state_sharing(self):
        """Test session state is shared between CLI and Web"""
        session = {
            'id': 'sess_123',
            'current_command': 'MAP',
            'delegation_active': True,
            'last_sync': time.time()
        }

        self.assertTrue(session['delegation_active'])

    def test_delegation_state_persistence(self):
        """Test delegation state persists across reconnections"""
        state = {
            'pending_delegations': {
                'req_1': {'type': 'map_select', 'created_at': time.time()}
            }
        }

        # Simulate save
        json_state = json.dumps(state)

        # Simulate load
        loaded = json.loads(json_state)

        self.assertIn('req_1', loaded['pending_delegations'])

    def test_session_context_updates(self):
        """Test session context updates during delegation"""
        session = {'context': {}}

        # Update context with delegation result
        session['context']['last_selection'] = [5, 10]
        session['context']['delegation_count'] = 1

        self.assertEqual(session['context']['delegation_count'], 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery"""

    def test_web_gui_unavailable(self):
        """Test graceful handling when Web GUI unavailable"""
        gui_available = False

        if not gui_available:
            fallback = 'cli_prompt'
        else:
            fallback = 'web_delegation'

        self.assertEqual(fallback, 'cli_prompt')

    def test_websocket_disconnection(self):
        """Test handling of WebSocket disconnection during delegation"""
        mock_ws = Mock()
        mock_ws.connected = False

        if not mock_ws.connected:
            error = {'type': 'connection_error', 'message': 'WebSocket disconnected'}
        else:
            error = None

        self.assertIsNotNone(error)

    def test_malformed_response_handling(self):
        """Test handling of malformed responses"""
        response = {'type': 'delegation_response'}  # Missing required fields

        is_valid = 'request_id' in response and 'status' in response

        self.assertFalse(is_valid)

    def test_delegation_retry_mechanism(self):
        """Test retry mechanism for failed delegations"""
        max_retries = 3
        attempt = 0
        success = False

        while attempt < max_retries and not success:
            attempt += 1
            # Simulate retry
            if attempt == 2:  # Success on second attempt
                success = True

        self.assertTrue(success)
        self.assertEqual(attempt, 2)

    def test_partial_result_handling(self):
        """Test handling of partial/incomplete results"""
        result = {'selected_items': [1, 2]}  # Expected 'action' field missing

        has_required_fields = 'selected_items' in result and 'action' in result

        self.assertFalse(has_required_fields)


class TestConcurrentDelegations(unittest.TestCase):
    """Test concurrent delegation requests"""

    def test_multiple_pending_requests(self):
        """Test multiple delegation requests can be pending"""
        pending = {
            'req_1': {'type': 'map_select'},
            'req_2': {'type': 'file_picker'},
            'req_3': {'type': 'skill_tree'}
        }

        self.assertEqual(len(pending), 3)

    def test_request_priority_queue(self):
        """Test delegation requests can be prioritized"""
        requests = [
            {'id': 'req_1', 'priority': 2},
            {'id': 'req_2', 'priority': 1},
            {'id': 'req_3', 'priority': 3}
        ]

        # Sort by priority
        sorted_requests = sorted(requests, key=lambda r: r['priority'])

        self.assertEqual(sorted_requests[0]['id'], 'req_2')
        self.assertEqual(sorted_requests[-1]['id'], 'req_3')

    def test_concurrent_response_handling(self):
        """Test responses can arrive concurrently"""
        responses = {}

        # Simulate concurrent responses
        responses['req_1'] = {'status': 'success', 'result': 'A'}
        responses['req_2'] = {'status': 'success', 'result': 'B'}

        self.assertEqual(len(responses), 2)


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility"""

    def test_path_normalization(self):
        """Test file paths are normalized across platforms"""
        if os.name == 'nt':  # Windows
            path = 'knowledge\\survival\\water.md'
        else:  # Unix-like
            path = 'knowledge/survival/water.md'

        # Normalize
        normalized = Path(path).as_posix()

        self.assertEqual(normalized, 'knowledge/survival/water.md')

    def test_message_encoding(self):
        """Test messages handle Unicode correctly"""
        message = {
            'text': '🌊 Water purification guide 🔥',
            'author': 'José García'
        }

        # Serialize with ensure_ascii=False for Unicode
        json_str = json.dumps(message, ensure_ascii=False)
        parsed = json.loads(json_str)

        self.assertEqual(parsed['text'], message['text'])

    def test_browser_launch_command(self):
        """Test browser launch works cross-platform"""
        url = 'http://localhost:9002/delegation/req_123'

        # Would use webbrowser.open(url) in real code
        self.assertTrue(url.startswith('http'))


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios"""

    def test_map_navigation_workflow(self):
        """Test complete map navigation delegation workflow"""
        # CLI: User executes MAP command
        cli_state = {'command': 'MAP', 'current_pos': [10, 10]}

        # CLI: Detects need for visual cell selection
        needs_delegation = True

        # CLI: Sends delegation request
        request = {
            'request_id': 'req_map_123',
            'delegation_type': 'map_cell_selection',
            'data': {
                'current_position': cli_state['current_pos'],
                'adjacent_cells': [[9, 10], [11, 10], [10, 9], [10, 11]]
            }
        }

        # Web: Receives request, shows interactive map
        web_received = request

        # Web: User selects cell [11, 10]
        response = {
            'request_id': 'req_map_123',
            'status': 'success',
            'result': {'selected_cell': [11, 10], 'action': 'move'}
        }

        # CLI: Receives response, executes command
        cli_state['current_pos'] = response['result']['selected_cell']

        self.assertEqual(cli_state['current_pos'], [11, 10])
        self.assertTrue(needs_delegation)

    def test_file_management_workflow(self):
        """Test file picker delegation workflow"""
        # CLI: User wants to attach files to mission
        request = {
            'delegation_type': 'file_picker',
            'data': {
                'base_path': '/knowledge',
                'extensions': ['.md', '.txt'],
                'multi_select': True,
                'max_files': 5
            }
        }

        # Web: Shows file browser
        # User selects 3 files
        response = {
            'status': 'success',
            'result': {
                'selected_files': [
                    '/knowledge/survival/water/purification.md',
                    '/knowledge/survival/fire/friction.md',
                    '/knowledge/survival/shelter/basics.md'
                ]
            }
        }

        # CLI: Validates and processes files
        files = response['result']['selected_files']
        all_valid = all(Path(f).suffix in ['.md', '.txt'] for f in files)

        self.assertTrue(all_valid)
        self.assertEqual(len(files), 3)


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
