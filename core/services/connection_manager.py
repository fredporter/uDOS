# uDOS v1.0.0 - Connection Awareness System

import socket
import urllib.request
import urllib.error

class ConnectionMonitor:
    """
    Monitors internet connectivity and determines operational mode.
    """

    def __init__(self):
        self.is_online = False
        self.last_check = None
        self.connectivity_status = {}

    def check_internet_connection(self, timeout=3):
        """
        Check if internet connection is available.

        Args:
            timeout (int): Connection timeout in seconds

        Returns:
            dict: Connection status with details
        """
        status = {
            'online': False,
            'dns_resolves': False,
            'http_accessible': False,
            'git_accessible': False,
            'api_accessible': False
        }

        # Test 1: DNS resolution
        try:
            socket.gethostbyname('google.com')
            status['dns_resolves'] = True
        except socket.gaierror:
            return status

        # Test 2: HTTP connectivity
        try:
            urllib.request.urlopen('http://google.com', timeout=timeout)
            status['http_accessible'] = True
            status['online'] = True
        except (urllib.error.URLError, socket.timeout):
            pass

        # Test 3: GitHub accessibility (for git operations)
        if status['online']:
            try:
                urllib.request.urlopen('https://github.com', timeout=timeout)
                status['git_accessible'] = True
            except (urllib.error.URLError, socket.timeout):
                pass

        # Test 4: Gemini API accessibility
        if status['online']:
            try:
                urllib.request.urlopen('https://generativelanguage.googleapis.com', timeout=timeout)
                status['api_accessible'] = True
            except (urllib.error.URLError, socket.timeout):
                pass

        self.is_online = status['online']
        self.connectivity_status = status

        return status

    def has_internet(self):
        """Check if internet connection is available.

        Returns:
            bool: True if online, False otherwise
        """
        return self.is_online

    def get_mode(self):
        """
        Determine operational mode based on connectivity.

        Returns:
            str: 'ONLINE', 'OFFLINE', or 'LIMITED'
        """
        if not self.is_online:
            return 'OFFLINE'

        if self.connectivity_status.get('api_accessible'):
            return 'ONLINE'

        return 'LIMITED'  # Internet but APIs not accessible

    def get_capabilities(self):
        """
        Return available capabilities based on connection status.

        Returns:
            dict: Available features
        """
        capabilities = {
            'ai_commands': False,
            'git_operations': False,
            'web_browsing': False,
            'local_operations': True,
            'offline_ai': True
        }

        if self.is_online:
            capabilities['web_browsing'] = True

            if self.connectivity_status.get('git_accessible'):
                capabilities['git_operations'] = True

            if self.connectivity_status.get('api_accessible'):
                capabilities['ai_commands'] = True

        return capabilities

    def format_status_report(self):
        """
        Generate a human-readable status report.

        Returns:
            str: Formatted status message
        """
        mode = self.get_mode()
        capabilities = self.get_capabilities()

        report = f"🌐 Connection Mode: {mode}\n"
        report += "\nCapabilities:\n"

        if capabilities['ai_commands']:
            report += "  ✅ AI Commands (Gemini)\n"
        else:
            report += "  ⚠️  AI Commands (Offline mode)\n"

        if capabilities['git_operations']:
            report += "  ✅ Git Operations\n"
        else:
            report += "  ❌ Git Operations (No connection)\n"

        if capabilities['web_browsing']:
            report += "  ✅ Web Browsing\n"
        else:
            report += "  ❌ Web Browsing (No connection)\n"

        report += "  ✅ Local File Operations\n"
        report += "  ✅ Offline Logic Engine\n"

        return report
