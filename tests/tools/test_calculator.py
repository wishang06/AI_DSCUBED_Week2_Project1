import pytest
from src.tools.calculator import Calculator

def test_calculator_add():
    assert Calculator.add(1, 2) == 3

def test_calculator_subtract():
    assert Calculator.subtract(5, 3) == 2

def test_calculator_multiply():
    assert Calculator.multiply(2, 3) == 6

def test_calculator_divide():
    assert Calculator.divide(6, 2) == 3

def test_calculator_divide_by_zero():
    with pytest.raises(ValueError):
        Calculator.divide(5, 0)

def test_calculator_square_root():
    assert Calculator.square_root(9) == 3

def test_calculator_square_root_negative():
    with pytest.raises(ValueError):
        Calculator.square_root(-1)

def test_calculator_power():
    assert Calculator.power(2, 3) == 8
