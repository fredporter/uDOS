"""
Graphics Service - Python Bridge to Node.js Renderer
Version: 1.2.15

Provides Python interface to the Node.js graphics rendering service.
Handles all 5 graphics formats: ASCII, Teletext, SVG, Sequence, Flow.
"""

import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GraphicsServiceError(Exception):
    """Graphics service specific errors"""
    pass


class GraphicsService:
    """
    Python bridge to Node.js graphics renderer.
    
    Manages communication with the graphics-renderer extension service
    running on port 5555.
    """
    
    def __init__(self, host: str = "localhost", port: int = 5555):
        """
        Initialize graphics service connection.
        
        Args:
            host: Renderer service hostname
            port: Renderer service port (default: 5555)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = 30  # seconds
        
    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to renderer service.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST)
            data: Request payload for POST
            
        Returns:
            JSON response from service
            
        Raises:
            GraphicsServiceError: If service is unreachable or returns error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise GraphicsServiceError(
                f"Cannot connect to graphics renderer at {self.base_url}. "
                "Ensure the service is running: cd extensions/core/graphics-renderer && npm start"
            )
        except requests.exceptions.Timeout:
            raise GraphicsServiceError(f"Request to {url} timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise GraphicsServiceError(f"HTTP request failed: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if graphics renderer service is healthy.
        
        Returns:
            Service health status and metadata
        """
        return self._request("/health")
    
    def is_available(self) -> bool:
        """
        Check if graphics renderer is available.
        
        Returns:
            True if service is running and healthy
        """
        try:
            health = self.health_check()
            return health.get("status") == "healthy"
        except GraphicsServiceError:
            return False
    
    # ASCII rendering
    def render_ascii(self, template: str, data: Optional[Dict] = None, 
                    options: Optional[Dict] = None) -> str:
        """
        Render ASCII diagram from template.
        
        Args:
            template: Template name (without .txt extension)
            data: Variable substitutions
            options: Rendering options (width, border, etc.)
            
        Returns:
            Rendered ASCII diagram
        """
        payload = {
            "template": template,
            "data": data or {},
            "options": options or {}
        }
        result = self._request("/render/ascii", "POST", payload)
        
        if not result.get("success"):
            raise GraphicsServiceError(f"ASCII render failed: {result.get('error')}")
        
        return result.get("output", "")
    
    # Teletext rendering
    def render_teletext(self, content: str, palette: str = "classic",
                       options: Optional[Dict] = None) -> str:
        """
        Render teletext page with 8-color palette.
        
        Args:
            content: Page content with color tags
            palette: Palette name (classic, earth, terminal, amber)
            options: Rendering options (width, height, background)
            
        Returns:
            Rendered teletext page with ANSI colors
        """
        payload = {
            "content": content,
            "palette": palette,
            "options": options or {}
        }
        result = self._request("/render/teletext", "POST", payload)
        
        if not result.get("success"):
            raise GraphicsServiceError(f"Teletext render failed: {result.get('error')}")
        
        return result.get("output", "")
    
    # SVG rendering
    def render_svg(self, description: str, style: str = "technical",
                  options: Optional[Dict] = None) -> str:
        """
        Render SVG diagram (AI-assisted).
        
        Args:
            description: Natural language diagram description
            style: Style name (technical, simple, detailed)
            options: Rendering options (width, height)
            
        Returns:
            SVG markup
        """
        payload = {
            "description": description,
            "style": style,
            "options": options or {}
        }
        result = self._request("/render/svg", "POST", payload)
        
        if not result.get("success"):
            raise GraphicsServiceError(f"SVG render failed: {result.get('error')}")
        
        return result.get("output", "")
    
    # Sequence diagram rendering
    def render_sequence(self, source: str, options: Optional[Dict] = None) -> str:
        """
        Render sequence diagram using js-sequence syntax.
        
        Args:
            source: Sequence diagram source (template name or full syntax)
            options: Rendering options (theme)
            
        Returns:
            SVG markup
        """
        payload = {
            "source": source,
            "options": options or {}
        }
        result = self._request("/render/sequence", "POST", payload)
        
        if not result.get("success"):
            raise GraphicsServiceError(f"Sequence render failed: {result.get('error')}")
        
        return result.get("output", "")
    
    # Flowchart rendering
    def render_flow(self, source: str, options: Optional[Dict] = None) -> str:
        """
        Render flowchart using flowchart.js syntax.
        
        Args:
            source: Flowchart source (template name or full syntax)
            options: Rendering options (lineWidth, fontSize, colors)
            
        Returns:
            SVG markup
        """
        payload = {
            "source": source,
            "options": options or {}
        }
        result = self._request("/render/flow", "POST", payload)
        
        if not result.get("success"):
            raise GraphicsServiceError(f"Flow render failed: {result.get('error')}")
        
        return result.get("output", "")
    
    # Unified rendering
    def render(self, format: str, **kwargs) -> str:
        """
        Unified rendering interface for all formats.
        
        Args:
            format: Graphics format (ascii, teletext, svg, sequence, flow)
            **kwargs: Format-specific parameters
            
        Returns:
            Rendered output
        """
        format_map = {
            "ascii": self.render_ascii,
            "teletext": self.render_teletext,
            "svg": self.render_svg,
            "sequence": self.render_sequence,
            "flow": self.render_flow
        }
        
        renderer = format_map.get(format)
        if not renderer:
            raise GraphicsServiceError(
                f"Unsupported format: {format}. "
                f"Supported: {', '.join(format_map.keys())}"
            )
        
        return renderer(**kwargs)
    
    # Template/palette/style listing
    def list_templates(self, format: str) -> List[str]:
        """
        List available templates for a format.
        
        Args:
            format: Format name (ascii, teletext, svg, sequence, flow)
            
        Returns:
            List of template names
        """
        result = self._request(f"/templates/{format}")
        
        if not result.get("success"):
            raise GraphicsServiceError(f"Failed to list {format} templates")
        
        return result.get("templates", [])
    
    def get_catalog(self) -> Dict[str, Any]:
        """
        Get complete template catalog.
        
        Returns:
            Full catalog with all formats, templates, styles
        """
        catalog_path = Path(__file__).parent.parent.parent / "data" / "diagrams" / "catalog.json"
        
        if not catalog_path.exists():
            raise GraphicsServiceError(f"Catalog not found: {catalog_path}")
        
        with open(catalog_path, 'r') as f:
            return json.load(f)


# Singleton instance
_graphics_service = None


def get_graphics_service(host: str = "localhost", port: int = 5555) -> GraphicsService:
    """
    Get singleton graphics service instance.
    
    Args:
        host: Renderer service hostname
        port: Renderer service port
        
    Returns:
        GraphicsService instance
    """
    global _graphics_service
    
    if _graphics_service is None:
        _graphics_service = GraphicsService(host, port)
    
    return _graphics_service
