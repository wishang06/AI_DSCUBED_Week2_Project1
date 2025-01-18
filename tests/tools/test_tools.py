import pytest
from tools.calculator import Calculator
from tools.core.terminal import TerminalOperations
import os

def test_calculator_add():
    calculator = Calculator()
    assert calculator.add(2, 3) == 5

def test_calculator_subtract():
    calculator = Calculator()
    assert calculator.subtract(5, 2) == 3

def test_calculator_multiply():
    calculator = Calculator()
    assert calculator.multiply(2, 4) == 8

def test_calculator_divide():
    calculator = Calculator()
    assert calculator.divide(10, 2) == 5

def test_calculator_divide_by_zero():
    calculator = Calculator()
    with pytest.raises(ValueError):
        calculator.divide(10, 0)

def test_calculator_square_root():
    calculator = Calculator()
    assert calculator.square_root(9) == 3

def test_calculator_square_root_negative():
    calculator = Calculator()
    with pytest.raises(ValueError):
        calculator.square_root(-9)

def test_calculator_power():
    calculator = Calculator()
    assert calculator.power(2, 3) == 8

def test_file_operations_list_directory():
    file_ops = TerminalOperations()
    # Create a dummy directory and file for testing
    os.makedirs("temp_test_dir", exist_ok=True)
    with open("temp_test_dir/test_file.txt", "w") as f:
        f.write("test content")
    contents = file_ops.list_directory("temp_test_dir")
    assert "test_file.txt" in contents
    os.remove("temp_test_dir/test_file.txt")
    os.rmdir("temp_test_dir")

def test_file_operations_read_file():
    file_ops = TerminalOperations()
    # Create a dummy file for testing
    with open("temp_test_file.txt", "w") as f:
        f.write("test content")
    content = file_ops.read_file("temp_test_file.txt")
    assert content == "test content"
    os.remove("temp_test_file.txt")

def test_file_operations_read_file_not_found():
    file_ops = TerminalOperations()
    with pytest.raises(ValueError) as excinfo:
        file_ops.read_file("non_existent_file.txt")
    assert "File not found" in str(excinfo.value)

def test_file_operations_write_file():
    file_ops = TerminalOperations()
    file_ops.write_file("temp_write_file.txt", "test content")
    with open("temp_write_file.txt", "r") as f:
        content = f.read()
    assert content == "test content"
    os.remove("temp_write_file.txt")

def test_file_operations_write_file_overwrite():
    file_ops = TerminalOperations()
    with open("temp_overwrite_file.txt", "w") as f:
        f.write("original content")
    file_ops.write_file("temp_overwrite_file.txt", "new content", overwrite=True)
    with open("temp_overwrite_file.txt", "r") as f:
        content = f.read()
    assert content == "new content"
    os.remove("temp_overwrite_file.txt")

def test_file_operations_write_file_exists():
    file_ops = TerminalOperations()
    with open("temp_exists_file.txt", "w") as f:
        f.write("original content")
    with pytest.raises(ValueError) as excinfo:
        file_ops.write_file("temp_exists_file.txt", "new content")
    assert "File already exists" in str(excinfo.value)
    os.remove("temp_exists_file.txt")

def test_file_operations_delete_file():
    file_ops = TerminalOperations()
    with open("temp_delete_file.txt", "w") as f:
        f.write("test content")
    file_ops.delete_file("temp_delete_file.txt")
    assert not os.path.exists("temp_delete_file.txt")

def test_file_operations_delete_file_not_found():
    file_ops = TerminalOperations()
    with pytest.raises(ValueError) as excinfo:
        file_ops.delete_file("non_existent_file.txt")
    assert "File not found" in str(excinfo.value)

def test_file_operations_create_directory():
    file_ops = TerminalOperations()
    file_ops.create_directory("temp_create_dir")
    assert os.path.exists("temp_create_dir")
    os.rmdir("temp_create_dir")

def test_file_operations_create_directory_exists():
    file_ops = TerminalOperations()
    os.makedirs("temp_exists_dir", exist_ok=True)
    with pytest.raises(ValueError) as excinfo:
        file_ops.create_directory("temp_exists_dir")
    assert "Directory already exists" in str(excinfo.value)
    os.rmdir("temp_exists_dir")
