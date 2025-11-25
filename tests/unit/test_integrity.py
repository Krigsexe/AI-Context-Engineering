# =============================================================================
# ODIN v7.0 - Unit Tests: Integrity Module
# =============================================================================

import tempfile
from pathlib import Path
import pytest

from agents.shared.integrity import (
    sha256_bytes,
    sha256_file,
    is_python,
    normalize_python_ast,
    semantic_hash_file,
    walk_files,
    project_sih,
    compare_sih,
    compute_project_hash,
    IntegrityMonitor,
)


class TestHashFunctions:
    """Test basic hash functions."""

    def test_sha256_bytes(self):
        """Test SHA-256 hash of bytes."""
        result = sha256_bytes(b"hello world")
        assert len(result) == 64
        assert result == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_sha256_file(self, tmp_path):
        """Test SHA-256 hash of file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        result = sha256_file(test_file)
        assert len(result) == 64


class TestPythonDetection:
    """Test Python file detection."""

    def test_is_python_true(self):
        """Test Python file detection - positive."""
        assert is_python(Path("test.py")) is True
        assert is_python(Path("/path/to/module.py")) is True

    def test_is_python_false(self):
        """Test Python file detection - negative."""
        assert is_python(Path("test.js")) is False
        assert is_python(Path("test.txt")) is False
        assert is_python(Path("test")) is False


class TestASTNormalization:
    """Test Python AST normalization."""

    def test_normalize_simple_function(self):
        """Test normalization of simple function."""
        code = '''
def hello():
    print("hello")
'''
        result = normalize_python_ast(code)
        assert "FunctionDef" in result
        assert "hello" in result

    def test_normalize_removes_whitespace_differences(self):
        """Test that whitespace differences are normalized."""
        code1 = "def f():\n    return 1"
        code2 = "def f():\n        return 1"

        # Both should produce same AST
        result1 = normalize_python_ast(code1)
        result2 = normalize_python_ast(code2)
        assert result1 == result2

    def test_normalize_syntax_error(self):
        """Test handling of syntax errors."""
        with pytest.raises(SyntaxError):
            normalize_python_ast("def f(")


class TestSemanticHash:
    """Test semantic hashing."""

    def test_semantic_hash_python_file(self, tmp_path):
        """Test semantic hash of Python file."""
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello():\n    return 42")

        result = semantic_hash_file(py_file)
        assert len(result) == 64

    def test_semantic_hash_non_python(self, tmp_path):
        """Test hash of non-Python file."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello world")

        result = semantic_hash_file(txt_file)
        assert len(result) == 64

    def test_semantic_hash_invalid_python(self, tmp_path):
        """Test fallback for invalid Python."""
        py_file = tmp_path / "invalid.py"
        py_file.write_text("def f(")  # Invalid syntax

        # Should fall back to raw hash
        result = semantic_hash_file(py_file)
        assert len(result) == 64


class TestWalkFiles:
    """Test directory walking."""

    def test_walk_files_basic(self, tmp_path):
        """Test basic file walking."""
        # Create test structure
        (tmp_path / "file1.py").write_text("# test")
        (tmp_path / "file2.txt").write_text("test")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.py").write_text("# test")

        files = walk_files(tmp_path)
        assert len(files) == 3

    def test_walk_files_ignores_git(self, tmp_path):
        """Test that .git is ignored."""
        (tmp_path / "file1.py").write_text("# test")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("test")

        files = walk_files(tmp_path)
        assert len(files) == 1
        assert all(".git" not in str(f) for f in files)

    def test_walk_files_ignores_pycache(self, tmp_path):
        """Test that __pycache__ is ignored."""
        (tmp_path / "file1.py").write_text("# test")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "file.pyc").write_text("test")

        files = walk_files(tmp_path)
        assert len(files) == 1


class TestProjectSIH:
    """Test project-wide SIH."""

    def test_project_sih_basic(self, tmp_path):
        """Test basic project SIH."""
        (tmp_path / "file1.py").write_text("def f(): pass")
        (tmp_path / "file2.py").write_text("def g(): pass")

        sih = project_sih(tmp_path)
        assert len(sih) == 2
        assert "file1.py" in sih
        assert "file2.py" in sih


class TestCompareSIH:
    """Test SIH comparison."""

    def test_compare_no_changes(self):
        """Test comparison with no changes."""
        sih = {"a.py": "hash1", "b.py": "hash2"}
        result = compare_sih(sih, sih)

        assert result["added"] == []
        assert result["removed"] == []
        assert result["modified"] == []
        assert len(result["unchanged"]) == 2

    def test_compare_added_file(self):
        """Test detection of added file."""
        old = {"a.py": "hash1"}
        new = {"a.py": "hash1", "b.py": "hash2"}

        result = compare_sih(old, new)
        assert result["added"] == ["b.py"]

    def test_compare_removed_file(self):
        """Test detection of removed file."""
        old = {"a.py": "hash1", "b.py": "hash2"}
        new = {"a.py": "hash1"}

        result = compare_sih(old, new)
        assert result["removed"] == ["b.py"]

    def test_compare_modified_file(self):
        """Test detection of modified file."""
        old = {"a.py": "hash1"}
        new = {"a.py": "hash2"}

        result = compare_sih(old, new)
        assert result["modified"] == ["a.py"]


class TestComputeProjectHash:
    """Test combined project hash."""

    def test_compute_project_hash(self):
        """Test computing combined hash."""
        sih = {"a.py": "hash1", "b.py": "hash2"}
        result = compute_project_hash(sih)

        assert len(result) == 64

    def test_compute_project_hash_deterministic(self):
        """Test that hash is deterministic."""
        sih = {"b.py": "hash2", "a.py": "hash1"}
        result1 = compute_project_hash(sih)
        result2 = compute_project_hash(sih)

        assert result1 == result2


class TestIntegrityMonitor:
    """Test IntegrityMonitor class."""

    def test_capture_baseline(self, tmp_path):
        """Test baseline capture."""
        (tmp_path / "test.py").write_text("def f(): pass")

        monitor = IntegrityMonitor(tmp_path)
        baseline = monitor.capture_baseline()

        assert "test.py" in baseline
        assert monitor.baseline is not None

    def test_check_drift_no_changes(self, tmp_path):
        """Test drift check with no changes."""
        (tmp_path / "test.py").write_text("def f(): pass")

        monitor = IntegrityMonitor(tmp_path)
        monitor.capture_baseline()

        drift = monitor.check_drift()
        assert not monitor.has_changes()

    def test_check_drift_with_modification(self, tmp_path):
        """Test drift check with modification."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def f(): pass")

        monitor = IntegrityMonitor(tmp_path)
        monitor.capture_baseline()

        # Modify file
        test_file.write_text("def f(): return 42")

        drift = monitor.check_drift()
        assert monitor.has_changes()
        assert "test.py" in drift["modified"]

    def test_check_drift_without_baseline(self, tmp_path):
        """Test drift check without baseline raises error."""
        monitor = IntegrityMonitor(tmp_path)

        with pytest.raises(ValueError):
            monitor.check_drift()
