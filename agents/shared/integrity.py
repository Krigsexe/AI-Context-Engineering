# =============================================================================
# ODIN v7.0 - Semantic Integrity Hashing (SIH)
# =============================================================================
# Language-agnostic semantic hashing for drift detection
# Migrated and enhanced from v6.1
# =============================================================================

from __future__ import annotations
import ast
import hashlib
import os
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)

# Directories to ignore during integrity scanning
DEFAULT_IGNORES: Set[str] = {
    ".git", ".odin", "backups", "__pycache__",
    "node_modules", ".venv", "venv", ".env",
    "dist", "build", "target", ".next", ".nuxt",
    "coverage", ".pytest_cache", ".mypy_cache",
}


def sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    return sha256_bytes(path.read_bytes())


def is_python(path: Path) -> bool:
    """Check if file is Python source."""
    return path.suffix == ".py"


def is_javascript(path: Path) -> bool:
    """Check if file is JavaScript/TypeScript source."""
    return path.suffix in {".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}


def is_go(path: Path) -> bool:
    """Check if file is Go source."""
    return path.suffix == ".go"


def normalize_python_ast(source: str) -> str:
    """
    Normalize Python source to AST representation.

    This removes:
    - Comments
    - Whitespace variations
    - String formatting differences

    Preserving only structural semantics.
    """
    # Only dedent and strip leading/trailing whitespace, preserving internal indentation
    source = textwrap.dedent(source).strip()
    tree = ast.parse(source)
    return ast.dump(tree, annotate_fields=True, include_attributes=False)


def normalize_javascript(source: str) -> str:
    """
    Basic JavaScript normalization.

    For full semantic normalization, consider using
    a proper JS parser like esprima or acorn.
    """
    # Remove single-line comments
    source = re.sub(r'//.*$', '', source, flags=re.MULTILINE)
    # Remove multi-line comments
    source = re.sub(r'/\*[\s\S]*?\*/', '', source)
    # Normalize whitespace
    source = re.sub(r'\s+', ' ', source)
    return source.strip()


def normalize_go(source: str) -> str:
    """
    Basic Go normalization.

    For full semantic normalization, consider using
    go/parser package via subprocess.
    """
    # Remove single-line comments
    source = re.sub(r'//.*$', '', source, flags=re.MULTILINE)
    # Remove multi-line comments
    source = re.sub(r'/\*[\s\S]*?\*/', '', source)
    # Normalize whitespace
    source = re.sub(r'\s+', ' ', source)
    return source.strip()


def semantic_hash_file(path: Path) -> str:
    """
    Compute semantic hash of a file.

    Uses language-specific normalization when available,
    falls back to raw content hash otherwise.

    Args:
        path: Path to the file

    Returns:
        SHA-256 hash string
    """
    try:
        content = path.read_text(encoding="utf-8")

        if is_python(path):
            try:
                normalized = normalize_python_ast(content)
                return sha256_bytes(normalized.encode("utf-8"))
            except SyntaxError:
                logger.debug(f"Python syntax error in {path}, using raw hash")

        elif is_javascript(path):
            try:
                normalized = normalize_javascript(content)
                return sha256_bytes(normalized.encode("utf-8"))
            except Exception:
                logger.debug(f"JS normalization failed for {path}, using raw hash")

        elif is_go(path):
            try:
                normalized = normalize_go(content)
                return sha256_bytes(normalized.encode("utf-8"))
            except Exception:
                logger.debug(f"Go normalization failed for {path}, using raw hash")

    except UnicodeDecodeError:
        # Binary file - use raw hash
        pass
    except Exception as e:
        logger.warning(f"Error processing {path}: {e}")

    # Fallback: raw content hash
    return sha256_file(path)


def walk_files(
    root: Path,
    ignores: Optional[Set[str]] = None
) -> List[Path]:
    """
    Walk directory tree and collect files.

    Args:
        root: Root directory to walk
        ignores: Set of directory/file names to ignore

    Returns:
        Sorted list of file paths
    """
    ignores = ignores or DEFAULT_IGNORES
    files = []

    for base, dirs, filenames in os.walk(root):
        base_path = Path(base)

        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignores]

        for filename in filenames:
            filepath = base_path / filename

            # Skip if any part of path is in ignores
            if any(part in ignores for part in filepath.parts):
                continue

            files.append(filepath)

    return sorted(files)


def project_sih(
    root: Path,
    ignores: Optional[Set[str]] = None
) -> Dict[str, str]:
    """
    Compute Semantic Integrity Hash for entire project.

    Args:
        root: Project root directory
        ignores: Optional set of paths to ignore

    Returns:
        Dict mapping relative paths to their semantic hashes
    """
    return {
        str(path.relative_to(root)): semantic_hash_file(path)
        for path in walk_files(root, ignores)
    }


def compare_sih(
    old_sih: Dict[str, str],
    new_sih: Dict[str, str]
) -> Dict[str, List[str]]:
    """
    Compare two SIH snapshots and identify changes.

    Args:
        old_sih: Previous snapshot
        new_sih: Current snapshot

    Returns:
        Dict with keys:
            - added: New files
            - removed: Deleted files
            - modified: Changed files (different hash)
            - unchanged: Same hash
    """
    old_files = set(old_sih.keys())
    new_files = set(new_sih.keys())

    added = list(new_files - old_files)
    removed = list(old_files - new_files)

    common = old_files & new_files
    modified = [f for f in common if old_sih[f] != new_sih[f]]
    unchanged = [f for f in common if old_sih[f] == new_sih[f]]

    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "modified": sorted(modified),
        "unchanged": sorted(unchanged),
    }


def compute_project_hash(sih: Dict[str, str]) -> str:
    """
    Compute a single hash representing entire project state.

    Args:
        sih: Project SIH dict

    Returns:
        Combined hash string
    """
    # Sort by path for deterministic ordering
    combined = "".join(
        f"{path}:{hash_val}"
        for path, hash_val in sorted(sih.items())
    )
    return sha256_bytes(combined.encode("utf-8"))


class IntegrityMonitor:
    """
    Monitors project integrity over time.

    Provides drift detection and change tracking.
    """

    def __init__(
        self,
        root: Path,
        ignores: Optional[Set[str]] = None
    ):
        self.root = root
        self.ignores = ignores or DEFAULT_IGNORES
        self._baseline: Optional[Dict[str, str]] = None

    def capture_baseline(self) -> Dict[str, str]:
        """Capture current state as baseline."""
        self._baseline = project_sih(self.root, self.ignores)
        return self._baseline

    def check_drift(self) -> Dict[str, List[str]]:
        """
        Check for drift from baseline.

        Returns:
            Change summary dict

        Raises:
            ValueError: If no baseline captured
        """
        if self._baseline is None:
            raise ValueError("No baseline captured. Call capture_baseline() first.")

        current = project_sih(self.root, self.ignores)
        return compare_sih(self._baseline, current)

    def has_changes(self) -> bool:
        """Check if any changes detected since baseline."""
        drift = self.check_drift()
        return bool(drift["added"] or drift["removed"] or drift["modified"])

    @property
    def baseline(self) -> Optional[Dict[str, str]]:
        """Get current baseline."""
        return self._baseline

    @baseline.setter
    def baseline(self, sih: Dict[str, str]):
        """Set baseline from external source."""
        self._baseline = sih
