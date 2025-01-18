import pytest
import os
from tools.core.terminal import TerminalOperations

# Create a temporary directory for testing file operations
@pytest.fixture(scope="module")
def temp_dir(tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp("test_file_ops")
    yield str(tmp_dir)

def test_list_directory(temp_dir):
    # Create some dummy files and directories
    os.makedirs(os.path.join(temp_dir, "subdir"), exist_ok=True)
    with open(os.path.join(temp_dir, "test_file.txt"), "w") as f:
        f.write("test content")

    contents = TerminalOperations.list_directory(temp_dir)
    assert "test_file.txt" in contents
    assert "subdir" in contents

def test_read_file(temp_dir):
    file_path = os.path.join(temp_dir, "read_test.txt")
    with open(file_path, "w") as f:
        f.write("content to read")

    content = TerminalOperations.read_file(file_path)
    assert content == "content to read"

def test_read_file_not_found(temp_dir):
    with pytest.raises(ValueError):
        TerminalOperations.read_file(os.path.join(temp_dir, "nonexistent.txt"))

def test_read_file_too_large(temp_dir):
    file_path = os.path.join(temp_dir, "large_file.txt")
    with open(file_path, "w") as f:
        f.write("a" * 2048)  # Create a file larger than the default max_size

    with pytest.raises(ValueError):
        TerminalOperations.read_file(file_path)

def test_write_file(temp_dir):
    file_path = os.path.join(temp_dir, "write_test.txt")
    TerminalOperations.write_file(file_path, "content to write")
    with open(file_path, "r") as f:
        assert f.read() == "content to write"

def test_write_file_overwrite(temp_dir):
    file_path = os.path.join(temp_dir, "overwrite_test.txt")
    with open(file_path, "w") as f:
        f.write("initial content")

    TerminalOperations.write_file(file_path, "new content", overwrite=True)
    with open(file_path, "r") as f:
        assert f.read() == "new content"

def test_write_file_no_overwrite(temp_dir):
    file_path = os.path.join(temp_dir, "no_overwrite_test.txt")
    with open(file_path, "w") as f:
        f.write("initial content")

    with pytest.raises(ValueError):
        TerminalOperations.write_file(file_path, "new content", overwrite=False)

def test_delete_file(temp_dir):
    file_path = os.path.join(temp_dir, "delete_test.txt")
    with open(file_path, "w") as f:
        f.write("to be deleted")

    TerminalOperations.delete_file(file_path)
    assert not os.path.exists(file_path)

def test_delete_file_not_found(temp_dir):
    with pytest.raises(ValueError):
        TerminalOperations.delete_file(os.path.join(temp_dir, "nonexistent.txt"))

def test_create_directory(temp_dir):
    new_dir_path = os.path.join(temp_dir, "new_directory")
    TerminalOperations.create_directory(new_dir_path)
    assert os.path.exists(new_dir_path)
    assert os.path.isdir(new_dir_path)

def test_create_directory_exists(temp_dir):
    new_dir_path = os.path.join(temp_dir, "existing_directory")
    os.makedirs(new_dir_path, exist_ok=True)
    with pytest.raises(ValueError):
        TerminalOperations.create_directory(new_dir_path)
