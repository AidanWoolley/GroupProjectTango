def fib(n: int) -> int:
    """
    Calculate the nth fibonacci number in O(n), starting 0, 1, 1 (with 0 at index 0)

    Args:
        n: The index of the fibonacci number to calculate

    Returns:
        the `n`th fibonacci number

    Raises:
        TypeError: If `n` is not an int
        ValueError: If `n` is less than 0
    """
    if not isinstance(n, int):
        raise TypeError(f"n should be int, but is {type(n)}")
    f2 = 0
    f1 = 1
    f0 = 1
    if n < 0: raise ValueError("Sequence indices must be at least 0")
    elif n == 0: return 0
    # Start at 1 because we need to execute the loop once for n==2, etc
    for i in range(1, n):
        f0 = f1 + f2
        f2 = f1
        f1 = f0
    return f0
  
  
def test_fib_not_int():
    """Test that `fib` throws TypeError on non-int argument"""
    try:
      fib(0.45)
    except TypeError as e:
      assert True
      return
    assert False

def test_fib_negative():
    """Test that `fib` throws ValueError on negative argument"""
    try:
      fib(-1)
    except ValueError as e:
      assert True
      return
    assert False

def test_fib_0():
    """Test fib(0) == 0"""
    assert fib(0) == 0

def test_fib_1():
    """Test fib(1) == 1"""
    assert fib(1) == 1

def test_fib_general():
    """
    Test the first few values from `fib` are correct.
    As long as they are, all further values must also be correct due to Python's arbitrary-precision int arithmetic.
    """
    assert [fib(x) for x in range(2, 15)] == [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
