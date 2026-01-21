"""
Binder Folder Structure Validation

Validates binder folder layout and reports issues.

**Required Structure:**
```
MyBinder/
  uDOS-table.db          # Required (can be empty)
```

**Optional Structure:**
```
MyBinder/
  binder.md              # Optional home/metadata
  .binder-config         # Optional metadata file
  imports/               # Optional source folder
  tables/                # Optional export folder
  scripts/               # Optional executable folder
  data/                  # Optional user data
```

**Validation Levels:**
- CRITICAL: Missing uDOS-table.db
- WARNING: Missing optional recommended folders
- INFO: Folder structure info
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for validation issues."""

    CRITICAL = "critical"  # Will prevent binder operation
    WARNING = "warning"  # Recommended but optional
    INFO = "info"  # Informational only


@dataclass
class ValidationIssue:
    """Single validation issue."""

    message: str
    severity: SeverityLevel
    location: Optional[str] = None  # e.g., "imports/"
    suggestion: Optional[str] = None  # How to fix


@dataclass
class ValidationReport:
    """Complete validation report for a binder."""

    is_valid: bool
    binder_path: Path
    issues: List[ValidationIssue] = field(default_factory=list)

    def has_critical(self) -> bool:
        """Check if any critical issues exist."""
        return any(i.severity == SeverityLevel.CRITICAL for i in self.issues)

    def has_warnings(self) -> bool:
        """Check if any warnings exist."""
        return any(i.severity == SeverityLevel.WARNING for i in self.issues)

    def summary(self) -> str:
        """Generate summary of issues.

        **Returns:**
            String summary of all issues with counts
        """
        critical = sum(1 for i in self.issues if i.severity == SeverityLevel.CRITICAL)
        warning = sum(1 for i in self.issues if i.severity == SeverityLevel.WARNING)
        info = sum(1 for i in self.issues if i.severity == SeverityLevel.INFO)

        lines = [f"Validation Report: {self.binder_path.name}"]
        lines.append(f"  Valid: {self.is_valid}")
        if critical > 0:
            lines.append(f"  Critical Issues: {critical}")
        if warning > 0:
            lines.append(f"  Warnings: {warning}")
        if info > 0:
            lines.append(f"  Info: {info}")

        if self.issues:
            lines.append("\nIssues:")
            for issue in self.issues:
                severity_str = issue.severity.value.upper()
                lines.append(f"  [{severity_str}] {issue.message}")
                if issue.location:
                    lines.append(f"    Location: {issue.location}")
                if issue.suggestion:
                    lines.append(f"    Fix: {issue.suggestion}")

        return "\n".join(lines)


class BinderValidator:
    """Validates binder folder structure."""

    # Required structure
    REQUIRED_FILES = ["uDOS-table.db"]

    # Optional but recommended folders
    RECOMMENDED_FOLDERS = ["imports", "tables", "scripts"]

    # Optional files
    OPTIONAL_FILES = ["binder.md", ".binder-config"]

    @staticmethod
    def validate(binder_path: Path) -> ValidationReport:
        """Validate binder folder structure.

        **Args:**
            binder_path: Path to binder folder

        **Returns:**
            ValidationReport with all issues found
        """
        binder_path = Path(binder_path)
        report = ValidationReport(is_valid=True, binder_path=binder_path)

        # Check folder exists
        if not binder_path.exists():
            report.is_valid = False
            report.issues.append(
                ValidationIssue(
                    message=f"Binder path does not exist: {binder_path}",
                    severity=SeverityLevel.CRITICAL,
                )
            )
            return report

        if not binder_path.is_dir():
            report.is_valid = False
            report.issues.append(
                ValidationIssue(
                    message=f"Binder path is not a folder: {binder_path}",
                    severity=SeverityLevel.CRITICAL,
                )
            )
            return report

        # Check required files
        for required_file in BinderValidator.REQUIRED_FILES:
            file_path = binder_path / required_file
            if not file_path.exists():
                report.is_valid = False
                report.issues.append(
                    ValidationIssue(
                        message=f"Missing required file: {required_file}",
                        severity=SeverityLevel.CRITICAL,
                        location=str(required_file),
                        suggestion=f"Create empty file: touch {binder_path / required_file}",
                    )
                )

        # Check recommended folders
        for recommended_folder in BinderValidator.RECOMMENDED_FOLDERS:
            folder_path = binder_path / recommended_folder
            if not folder_path.exists():
                report.issues.append(
                    ValidationIssue(
                        message=f"Missing recommended folder: {recommended_folder}/",
                        severity=SeverityLevel.WARNING,
                        location=str(recommended_folder),
                        suggestion=f"Create folder: mkdir -p {binder_path / recommended_folder}",
                    )
                )

        # Check optional files
        for optional_file in BinderValidator.OPTIONAL_FILES:
            file_path = binder_path / optional_file
            if file_path.exists():
                if optional_file == "binder.md":
                    # Check if binder.md is readable
                    try:
                        content = file_path.read_text()
                        if len(content) == 0:
                            report.issues.append(
                                ValidationIssue(
                                    message=f"Optional file is empty: {optional_file}",
                                    severity=SeverityLevel.INFO,
                                    location=str(optional_file),
                                )
                            )
                    except Exception as e:
                        report.issues.append(
                            ValidationIssue(
                                message=f"Cannot read optional file: {optional_file} ({e})",
                                severity=SeverityLevel.WARNING,
                                location=str(optional_file),
                            )
                        )

        return report

    @staticmethod
    def create_binder_structure(
        binder_path: Path, config: Optional[dict] = None
    ) -> ValidationReport:
        """Create standard binder folder structure.

        **Args:**
            binder_path: Path to create binder at
            config: Optional configuration dictionary to save

        **Returns:**
            ValidationReport after creation
        """
        binder_path = Path(binder_path)
        binder_path.mkdir(parents=True, exist_ok=True)

        # Create required files
        db_path = binder_path / "uDOS-table.db"
        if not db_path.exists():
            db_path.touch()

        # Create recommended folders
        for folder in BinderValidator.RECOMMENDED_FOLDERS:
            folder_path = binder_path / folder
            folder_path.mkdir(exist_ok=True)
            # Add .gitkeep to ensure folder is tracked
            (folder_path / ".gitkeep").touch()

        # Save config if provided
        if config:
            import json

            config_path = binder_path / ".binder-config"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

        # Validate and return report
        return BinderValidator.validate(binder_path)

    @staticmethod
    def discover_binders(root_path: Path) -> List[Path]:
        """Discover all valid binder folders under root path.

        Looks for folders containing uDOS-table.db

        **Args:**
            root_path: Path to search under (typically memory/binders/)

        **Returns:**
            List of discovered binder paths
        """
        root_path = Path(root_path)
        if not root_path.exists():
            return []

        binders = []
        for item in root_path.iterdir():
            if item.is_dir():
                db_path = item / "uDOS-table.db"
                if db_path.exists():
                    binders.append(item)

        return sorted(binders)
