"""Tree structure generation utilities for Wizard tooling."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Set

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root


class TreeStructureService:
    """Generate structure.txt snapshots for the repo and its submodules."""

    ROOT_EXCLUDES: Set[str] = {
        "__pycache__",
        ".git",
        ".vscode",
        ".idea",
        "node_modules",
        ".cache",
        ".tmp",
        "venv",
        ".venv",
    }

    SUBMODULE_EXCLUDES: Set[str] = {
        "__pycache__",
        ".git",
        ".vscode",
        ".idea",
        "node_modules",
        ".cache",
        ".tmp",
        "venv",
        ".venv",
    }

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root or get_repo_root())
        self.logger = get_logger("wizard-tree-service")
        self.gitignore_patterns = self._load_gitignore(self.repo_root)
        self.submodule_paths = self._load_submodule_paths()
        self._submodule_abs_paths = {path.resolve() for path in self.submodule_paths.values()}

    def generate_all_structure_files(self, depth: int = 2) -> Dict[str, object]:
        """Generate structure.txt snapshots for root, memory, knowledge, and submodules."""
        results: Dict[str, object] = {}
        root_tree = ""

        try:
            root_tree = self.generate_root_tree(depth)
            root_path = self.repo_root / "structure.txt"
            root_path.write_text(root_tree, encoding="utf-8")
            results["root"] = f"✅ {root_path}"
        except Exception as exc:  # pragma: no cover - defensive
            results["root"] = f"❌ Error: {exc}"

        try:
            memory_tree = self.generate_memory_tree()
            memory_file = self.repo_root / "memory" / "structure.txt"
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            memory_file.write_text(memory_tree, encoding="utf-8")
            results["memory"] = f"✅ {memory_file}"
        except FileNotFoundError as exc:
            results["memory"] = f"⚠️ {exc}"
        except Exception as exc:  # pragma: no cover - defensive
            results["memory"] = f"❌ Error: {exc}"

        try:
            knowledge_tree = self.generate_knowledge_tree()
            knowledge_file = self.repo_root / "knowledge" / "structure.txt"
            knowledge_file.parent.mkdir(parents=True, exist_ok=True)
            knowledge_file.write_text(knowledge_tree, encoding="utf-8")
            results["knowledge"] = f"✅ {knowledge_file}"
        except FileNotFoundError as exc:
            results["knowledge"] = f"⚠️ {exc}"
        except Exception as exc:  # pragma: no cover - defensive
            results["knowledge"] = f"❌ Error: {exc}"

        results["submodules"] = self._generate_submodule_files(depth)

        return {
            "root_tree": root_tree,
            "results": results,
        }

    def generate_root_tree(self, depth: int = 2) -> str:
        """Return the repository tree (excluding submodule contents)."""
        tag = self._get_gitignore_tag(self.repo_root, self.repo_root, self.gitignore_patterns)
        lines: List[str] = [f"{self.repo_root.name}/{tag}"]
        lines.extend(
            self._generate_tree(
                self.repo_root,
                max_depth=depth,
                exclude_folders=self.ROOT_EXCLUDES,
                respect_gitignore=True,
                git_base_path=self.repo_root,
                gitignore_patterns=self.gitignore_patterns,
                annotate_gitignored=True,
                exclude_submodules=True,
            )
        )
        return "\n".join(lines)

    def generate_memory_tree(self, depth: int = 8) -> str:
        """Return the memory/ tree (including local-only markers)."""
        memory_path = self.repo_root / "memory"
        if not memory_path.exists():
            raise FileNotFoundError("memory/ directory not found")

        rel_label = memory_path.relative_to(self.repo_root).as_posix()
        tag = self._get_gitignore_tag(memory_path, self.repo_root, self.gitignore_patterns)
        lines: List[str] = [f"{rel_label}/{tag}"]
        lines.extend(
            self._generate_tree(
                memory_path,
                max_depth=depth,
                exclude_folders={"logs", "__pycache__"},
                respect_gitignore=False,
                git_base_path=self.repo_root,
                gitignore_patterns=self.gitignore_patterns,
                annotate_gitignored=True,
            )
        )
        return "\n".join(lines)

    def generate_knowledge_tree(self, depth: int = 8) -> str:
        """Return the knowledge/ tree (mostly tracked but tagged if local)."""
        knowledge_path = self.repo_root / "knowledge"
        if not knowledge_path.exists():
            raise FileNotFoundError("knowledge/ directory not found")

        tag = self._get_gitignore_tag(knowledge_path, self.repo_root, self.gitignore_patterns)
        lines: List[str] = [f"knowledge/{tag}"]
        lines.extend(
            self._generate_tree(
                knowledge_path,
                max_depth=depth,
                exclude_folders={"__pycache__"},
                respect_gitignore=False,
                git_base_path=self.repo_root,
                gitignore_patterns=self.gitignore_patterns,
                annotate_gitignored=True,
            )
        )
        return "\n".join(lines)

    def _generate_submodule_files(self, depth: int) -> Dict[str, str]:
        statuses: Dict[str, str] = {}
        for rel_path, abs_path in self.submodule_paths.items():
            try:
                if not abs_path.exists():
                    statuses[rel_path] = f"⚠️ Missing path: {abs_path}"
                    continue
                tree_text = self._build_submodule_tree(rel_path, abs_path, depth)
                output_file = abs_path / "structure.txt"
                output_file.write_text(tree_text, encoding="utf-8")
                statuses[rel_path] = f"✅ {output_file}"
            except Exception as exc:  # pragma: no cover - defensive
                statuses[rel_path] = f"❌ Error: {exc}"
        return statuses

    def _build_submodule_tree(self, rel_path: str, abs_path: Path, depth: int) -> str:
        patterns = self._load_gitignore(abs_path)
        header = rel_path.rstrip("/")
        tag = self._get_gitignore_tag(abs_path, abs_path, patterns)
        lines: List[str] = [f"{header}/{tag}"]
        lines.extend(
            self._generate_tree(
                abs_path,
                max_depth=depth,
                exclude_folders=self.SUBMODULE_EXCLUDES,
                respect_gitignore=False,
                git_base_path=abs_path,
                gitignore_patterns=patterns,
                annotate_gitignored=True,
                exclude_submodules=False,
            )
        )
        return "\n".join(lines)

    def _generate_tree(
        self,
        directory: Path,
        *,
        max_depth: int,
        exclude_folders: Set[str],
        respect_gitignore: bool,
        git_base_path: Path,
        gitignore_patterns: List[str],
        annotate_gitignored: bool,
        exclude_submodules: bool = False,
        current_depth: int = 0,
        prefix: str = "",
    ) -> List[str]:
        if current_depth >= max_depth:
            return []

        try:
            entries = sorted(
                directory.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower())
            )
        except (FileNotFoundError, PermissionError, OSError):
            return []

        visible: List[Path] = []
        for item in entries:
            if item.name in exclude_folders:
                continue
            if respect_gitignore and self._matches_gitignore_pattern(item, git_base_path, gitignore_patterns):
                continue
            visible.append(item)

        lines: List[str] = []
        for index, item in enumerate(visible):
            is_last = index == len(visible) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "

            tag = (
                self._get_gitignore_tag(item, git_base_path, gitignore_patterns)
                if annotate_gitignored
                else ""
            )

            if item.is_dir():
                suffix = "/"
                if exclude_submodules and self._is_submodule_root(item):
                    lines.append(f"{prefix}{connector}{item.name}{suffix} [submodule]{tag}")
                    continue
                lines.append(f"{prefix}{connector}{item.name}{suffix}{tag}")
                sub_lines = self._generate_tree(
                    item,
                    max_depth=max_depth,
                    exclude_folders=exclude_folders,
                    respect_gitignore=respect_gitignore,
                    git_base_path=git_base_path,
                    gitignore_patterns=gitignore_patterns,
                    annotate_gitignored=annotate_gitignored,
                    exclude_submodules=exclude_submodules,
                    current_depth=current_depth + 1,
                    prefix=prefix + extension,
                )
                lines.extend(sub_lines)
            else:
                lines.append(f"{prefix}{connector}{item.name}{tag}")

        return lines

    def _load_gitignore(self, repo_path: Path) -> List[str]:
        gitignore = repo_path / ".gitignore"
        if not gitignore.exists():
            return []
        patterns: List[str] = []
        with gitignore.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
        return patterns

    def _load_submodule_paths(self) -> Dict[str, Path]:
        gitmodules = self.repo_root / ".gitmodules"
        if not gitmodules.exists():
            return {}

        submodules: Dict[str, Path] = {}
        current_path: Optional[str] = None

        with gitmodules.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[submodule"):
                    current_path = None
                    continue
                if line.startswith("path ="):
                    current_path = line.split("=", 1)[1].strip()
                    submodules[current_path] = (self.repo_root / current_path).resolve()
        return submodules

    def _is_submodule_root(self, path: Path) -> bool:
        try:
            resolved = path.resolve()
        except FileNotFoundError:
            return False
        return resolved in self._submodule_abs_paths

    def _matches_gitignore_pattern(
        self,
        path: Path,
        base: Path,
        patterns: List[str],
    ) -> bool:
        if not patterns:
            return False
        try:
            rel_path = path.relative_to(base)
        except ValueError:
            return False

        rel_str = rel_path.as_posix()
        rel_posix = PurePosixPath(rel_str)

        for pattern in patterns:
            normalized = pattern.replace("\\", "/").strip()
            if not normalized:
                continue
            is_dir_pattern = normalized.endswith("/")
            candidate = normalized.rstrip("/") if is_dir_pattern else normalized

            if is_dir_pattern:
                if not path.is_dir():
                    continue
                if rel_posix.match(candidate) or rel_str.startswith(f"{candidate}/") or path.name == candidate:
                    return True
                continue

            if rel_posix.match(candidate) or fnmatch.fnmatch(rel_str, candidate) or fnmatch.fnmatch(path.name, candidate):
                return True
        return False

    def _get_gitignore_tag(
        self,
        path: Path,
        base: Path,
        patterns: List[str],
    ) -> str:
        try:
            path.relative_to(base)
        except ValueError:
            return ""

        is_ignored = self._matches_gitignore_pattern(path, base, patterns)
        if not path.is_dir():
            return " --local only" if is_ignored else ""

        if is_ignored:
            return " --local only"

        has_ignored = False
        has_tracked = False
        try:
            for child in path.iterdir():
                if self._matches_gitignore_pattern(child, base, patterns):
                    has_ignored = True
                else:
                    has_tracked = True
                if has_ignored and has_tracked:
                    return " --part local only"
        except (PermissionError, OSError):
            return ""

        return ""
