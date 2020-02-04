def fib(n: int) -> int:
  if not isinstance(n, int):
    raise TypeError(f"n should be int, but is {type(n)}")
  f2 = 0
  f1 = 1
  f0 = -1
  if n < 0: raise ValueError("Sequence indices must be at least 0")
  elif n == 0: return 0
  elif n == 1: return 1
  for i in range(1, n):
    f0 = f1 + f2
    f2 = f1
    f1 = f0
  return f0
  
  
  def fib_test_not_int():
    try:
      fib(0.45)
    catch TypeError as e:
      assert True
      return
    assert False
  
  def fib_test_negative():
    try:
      fib(-1)
    catch ValueError as e:
      assert True
      return
    assert False
  
  def fib_test_0():
    assert fib(0) == 0
  
  def fib_test_1():
    assert fib(1) == 1
  
  def fib_test_general():
    assert [fib(x) for x in range(2, 15)] == [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
