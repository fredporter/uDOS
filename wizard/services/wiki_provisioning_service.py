"""
Wiki Provisioning Service - Setup and Manage Public Wiki

Provides wiki structure, provisioning, and content management.
Serves public documentation that falls outside core uDOS.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class WikiCategory:
    """Wiki documentation category."""

    slug: str  # "hardware", "network", "installation", etc.
    title: str
    description: str
    icon: str = "📄"
    order: int = 0
    pages: List[str] = None  # List of page slugs

    def __post_init__(self):
        if self.pages is None:
            self.pages = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WikiPage:
    """Single wiki page."""

    slug: str  # "alpine-disk-setup", "vnc-remote-desktop", etc.
    title: str
    category: str  # "hardware", "network", etc.
    description: str
    status: str  # "draft", "published", "archived"
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WikiStructure:
    """Complete wiki structure and metadata."""

    title: str
    description: str
    version: str
    categories: List[WikiCategory]
    pages: List[WikiPage]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "version": self.version,
            "categories": [c.to_dict() for c in self.categories],
            "pages": [p.to_dict() for p in self.pages],
        }


class WikiProvisioningService:
    """Manages wiki structure and provisioning."""

    def __init__(self, wiki_root: Path):
        """Initialize wiki provisioning service."""
        self.wiki_root = wiki_root
        self.index_path = wiki_root / "INDEX.json"
        self.structure = self._load_or_create_structure()

    def _load_or_create_structure(self) -> WikiStructure:
        """Load wiki structure from INDEX.json or create default."""
        if self.index_path.exists():
            try:
                with open(self.index_path) as f:
                    data = json.load(f)
                    return self._parse_structure(data)
            except Exception as e:
                print(f"Warning: Failed to load wiki index: {e}")

        # Create default structure
        return self._create_default_structure()

    def _parse_structure(self, data: Dict[str, Any]) -> WikiStructure:
        """Parse wiki structure from JSON data."""
        categories = [WikiCategory(**cat) for cat in data.get("categories", [])]
        pages = [WikiPage(**page) for page in data.get("pages", [])]

        return WikiStructure(
            title=data.get("title", "uDOS Wiki"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            categories=categories,
            pages=pages,
        )

    def _create_default_structure(self) -> WikiStructure:
        """Create default wiki structure."""
        return WikiStructure(
            title="uDOS Wiki",
            description="Public documentation for uDOS setup, configuration, and hardware integration",
            version="1.0.0",
            categories=[
                WikiCategory(
                    slug="getting-started",
                    title="Getting Started",
                    description="Initial setup and installation guides",
                    icon="🚀",
                    order=1,
                    pages=["alpine-installation", "first-run-setup", "basic-commands"],
                ),
                WikiCategory(
                    slug="hardware",
                    title="Hardware Setup",
                    description="Device configuration, partitioning, and disk management",
                    icon="💾",
                    order=2,
                    pages=[
                        "disk-partitioning",
                        "disk-formatting",
                        "usb-boot-media",
                        "storage-expansion",
                        "hardware-requirements",
                    ],
                ),
                WikiCategory(
                    slug="network",
                    title="Network Configuration",
                    description="Networking, VNC, remote access, and connectivity",
                    icon="🌐",
                    order=3,
                    pages=[
                        "ethernet-setup",
                        "wifi-configuration",
                        "vpn-setup",
                        "vnc-remote-desktop",
                        "ssh-access",
                        "meshcore-networking",
                    ],
                ),
                WikiCategory(
                    slug="devices",
                    title="Device Integration",
                    description="Sonic, Bluetooth, NFC, and other device flashing/pairing",
                    icon="🔧",
                    order=4,
                    pages=[
                        "sonic-device-setup",
                        "sonic-firmware-flashing",
                        "bluetooth-pairing",
                        "nfc-setup",
                        "device-discovery",
                    ],
                ),
                WikiCategory(
                    slug="integrations",
                    title="Integrations & Plugins",
                    description="Third-party services, containers, and library management",
                    icon="🔌",
                    order=5,
                    pages=[
                        "ollama-local-ai",
                        "mistral-vibe-setup",
                        "meshcore-deployment",
                        "plugin-installation",
                        "library-management",
                    ],
                ),
                WikiCategory(
                    slug="troubleshooting",
                    title="Troubleshooting",
                    description="Common issues, debugging, and recovery procedures",
                    icon="🔍",
                    order=6,
                    pages=[
                        "disk-issues",
                        "network-issues",
                        "boot-problems",
                        "system-recovery",
                        "getting-help",
                    ],
                ),
                WikiCategory(
                    slug="reference",
                    title="Reference",
                    description="Technical specifications and reference material",
                    icon="📚",
                    order=7,
                    pages=[
                        "alpine-packages",
                        "command-reference",
                        "file-structure",
                        "glossary",
                    ],
                ),
            ],
            pages=[
                # Getting Started
                WikiPage(
                    slug="alpine-installation",
                    title="Installing Alpine Linux",
                    category="getting-started",
                    description="Complete guide to installing Alpine on your device",
                    status="draft",
                ),
                WikiPage(
                    slug="first-run-setup",
                    title="First Run Setup",
                    category="getting-started",
                    description="Initial configuration after Alpine installation",
                    status="draft",
                ),
                WikiPage(
                    slug="basic-commands",
                    title="Basic Commands",
                    category="getting-started",
                    description="Essential uDOS commands for beginners",
                    status="draft",
                ),
                # Hardware
                WikiPage(
                    slug="disk-partitioning",
                    title="Disk Partitioning",
                    category="hardware",
                    description="How to partition drives for Alpine Linux",
                    status="draft",
                ),
                WikiPage(
                    slug="disk-formatting",
                    title="Disk Formatting",
                    category="hardware",
                    description="Formatting partitions for ext4 and other filesystems",
                    status="draft",
                ),
                WikiPage(
                    slug="usb-boot-media",
                    title="Creating USB Boot Media",
                    category="hardware",
                    description="Creating bootable USB drives with Alpine ISO",
                    status="draft",
                ),
                WikiPage(
                    slug="storage-expansion",
                    title="Storage Expansion",
                    category="hardware",
                    description="Adding external storage and managing disk space",
                    status="draft",
                ),
                WikiPage(
                    slug="hardware-requirements",
                    title="Hardware Requirements",
                    category="hardware",
                    description="Minimum and recommended hardware specs",
                    status="draft",
                ),
                # Network
                WikiPage(
                    slug="ethernet-setup",
                    title="Ethernet Configuration",
                    category="network",
                    description="Setting up wired network connections",
                    status="draft",
                ),
                WikiPage(
                    slug="wifi-configuration",
                    title="WiFi Configuration",
                    category="network",
                    description="Connecting to WiFi networks on Alpine",
                    status="draft",
                ),
                WikiPage(
                    slug="vpn-setup",
                    title="VPN Setup",
                    category="network",
                    description="Configuring VPN connections",
                    status="draft",
                ),
                WikiPage(
                    slug="vnc-remote-desktop",
                    title="VNC Remote Desktop",
                    category="network",
                    description="Setting up VNC for remote GUI access",
                    status="draft",
                ),
                WikiPage(
                    slug="ssh-access",
                    title="SSH Remote Access",
                    category="network",
                    description="Enabling and securing SSH access",
                    status="draft",
                ),
                WikiPage(
                    slug="meshcore-networking",
                    title="MeshCore Networking",
                    category="network",
                    description="Setting up peer-to-peer mesh networks",
                    status="draft",
                ),
                # Devices
                WikiPage(
                    slug="sonic-device-setup",
                    title="Sonic Device Setup",
                    category="devices",
                    description="Initial Sonic device configuration",
                    status="draft",
                ),
                WikiPage(
                    slug="sonic-firmware-flashing",
                    title="Sonic Firmware Flashing",
                    category="devices",
                    description="Flashing custom firmware to Sonic devices",
                    status="draft",
                ),
                WikiPage(
                    slug="bluetooth-pairing",
                    title="Bluetooth Pairing",
                    category="devices",
                    description="Pairing Bluetooth devices and peripherals",
                    status="draft",
                ),
                WikiPage(
                    slug="nfc-setup",
                    title="NFC Setup",
                    category="devices",
                    description="Setting up NFC readers and configuration",
                    status="draft",
                ),
                WikiPage(
                    slug="device-discovery",
                    title="Device Discovery",
                    category="devices",
                    description="Finding and discovering network devices",
                    status="draft",
                ),
                # Integrations
                WikiPage(
                    slug="ollama-local-ai",
                    title="Ollama Local AI",
                    category="integrations",
                    description="Setting up Ollama for local AI models",
                    status="draft",
                ),
                WikiPage(
                    slug="mistral-vibe-setup",
                    title="Mistral Vibe Setup",
                    category="integrations",
                    description="Configuring Mistral Vibe for offline AI",
                    status="draft",
                ),
                WikiPage(
                    slug="meshcore-deployment",
                    title="MeshCore Deployment",
                    category="integrations",
                    description="Deploying and running MeshCore",
                    status="draft",
                ),
                WikiPage(
                    slug="plugin-installation",
                    title="Plugin Installation",
                    category="integrations",
                    description="Installing and managing plugins",
                    status="draft",
                ),
                WikiPage(
                    slug="library-management",
                    title="Library Management",
                    category="integrations",
                    description="Managing local /library integrations",
                    status="draft",
                ),
                # Troubleshooting
                WikiPage(
                    slug="disk-issues",
                    title="Disk Issues",
                    category="troubleshooting",
                    description="Diagnosing and fixing disk-related problems",
                    status="draft",
                ),
                WikiPage(
                    slug="network-issues",
                    title="Network Issues",
                    category="troubleshooting",
                    description="Troubleshooting network connectivity problems",
                    status="draft",
                ),
                WikiPage(
                    slug="boot-problems",
                    title="Boot Problems",
                    category="troubleshooting",
                    description="Recovering from boot failures",
                    status="draft",
                ),
                WikiPage(
                    slug="system-recovery",
                    title="System Recovery",
                    category="troubleshooting",
                    description="Advanced recovery and repair procedures",
                    status="draft",
                ),
                WikiPage(
                    slug="getting-help",
                    title="Getting Help",
                    category="troubleshooting",
                    description="Resources for asking questions and reporting issues",
                    status="draft",
                ),
                # Reference
                WikiPage(
                    slug="alpine-packages",
                    title="Alpine Packages",
                    category="reference",
                    description="Common Alpine APK packages and their usage",
                    status="draft",
                ),
                WikiPage(
                    slug="command-reference",
                    title="Command Reference",
                    category="reference",
                    description="Complete reference of uDOS commands",
                    status="draft",
                ),
                WikiPage(
                    slug="file-structure",
                    title="File Structure",
                    category="reference",
                    description="Overview of uDOS file and directory structure",
                    status="draft",
                ),
                WikiPage(
                    slug="glossary",
                    title="Glossary",
                    category="reference",
                    description="Terms and definitions used in uDOS",
                    status="draft",
                ),
            ],
        )

    def save_structure(self):
        """Save wiki structure to INDEX.json."""
        self.wiki_root.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "w") as f:
            json.dump(self.structure.to_dict(), f, indent=2)

    def provision(self):
        """
        Provision wiki directories and create INDEX.json.

        Creates:
        - wiki/INDEX.json (structure and metadata)
        - wiki/categories/ (one dir per category)
        - wiki/pages/ (stub markdown files)
        """
        # Create wiki root
        self.wiki_root.mkdir(parents=True, exist_ok=True)

        # Save INDEX.json
        self.save_structure()

        # Create category directories
        categories_dir = self.wiki_root / "categories"
        categories_dir.mkdir(exist_ok=True)

        for category in self.structure.categories:
            cat_dir = categories_dir / category.slug
            cat_dir.mkdir(exist_ok=True)

            # Create category README
            category_readme = cat_dir / "README.md"
            if not category_readme.exists():
                category_readme.write_text(
                    f"# {category.title}\n\n{category.description}\n\n"
                    f"See [Wiki Index](../INDEX.md) for complete documentation.\n"
                )

        # Create pages directory
        pages_dir = self.wiki_root / "pages"
        pages_dir.mkdir(exist_ok=True)

        for page in self.structure.pages:
            page_file = pages_dir / f"{page.slug}.md"
            if not page_file.exists():
                page_file.write_text(
                    f"# {page.title}\n\n"
                    f"**Status:** {page.status}\n"
                    f"**Category:** {page.category}\n\n"
                    f"{page.description}\n\n"
                    f"---\n\n"
                    f"*This page is a stub and needs to be written.*\n"
                )

        # Create INDEX.md (human-readable index)
        index_md = self.wiki_root / "INDEX.md"
        if not index_md.exists():
            index_md.write_text(self._generate_index_md())

    def _generate_index_md(self) -> str:
        """Generate human-readable INDEX.md from structure."""
        lines = [
            "# uDOS Wiki",
            "",
            self.structure.description,
            "",
            "---",
            "",
        ]

        for category in sorted(self.structure.categories, key=lambda c: c.order):
            lines.append(f"## {category.icon} {category.title}")
            lines.append("")
            lines.append(category.description)
            lines.append("")

            category_pages = [
                p for p in self.structure.pages if p.category == category.slug
            ]
            for page in sorted(category_pages, key=lambda p: p.order or 0):
                status_badge = {
                    "draft": "📝",
                    "published": "✅",
                    "archived": "🗂️",
                }.get(page.status, "")
                lines.append(f"- {status_badge} [{page.title}](pages/{page.slug}.md)")

            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "_Wiki structure auto-generated by WikiProvisioningService_",
                "_For core documentation, see [docs/](../docs/)_",
            ]
        )

        return "\n".join(lines)

    def get_structure(self) -> Dict[str, Any]:
        """Get wiki structure as dictionary."""
        return self.structure.to_dict()

    def get_category(self, slug: str) -> Optional[WikiCategory]:
        """Get category by slug."""
        return next((c for c in self.structure.categories if c.slug == slug), None)

    def get_page(self, slug: str) -> Optional[WikiPage]:
        """Get page by slug."""
        return next((p for p in self.structure.pages if p.slug == slug), None)

    def get_pages_by_category(self, category_slug: str) -> List[WikiPage]:
        """Get all pages in a category."""
        return [p for p in self.structure.pages if p.category == category_slug]


def get_wiki_service(wiki_root: Optional[Path] = None) -> WikiProvisioningService:
    """Get singleton instance of WikiProvisioningService."""
    if wiki_root is None:
        import os
        from wizard.services.path_utils import get_repo_root

        env_root = os.getenv("UDOS_ROOT")
        base_root = Path(env_root).expanduser() if env_root else get_repo_root()
        wiki_root = base_root / "wiki"

    return WikiProvisioningService(wiki_root)
