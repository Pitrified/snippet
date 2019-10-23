Info on Pool:
* https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool
* https://sebastianraschka.com/Articles/2014_multiprocessing.html

Write your function
```python
def my_func(some_str, a, b):
    res = {"the_str" : some_str, "prod" : a * b}
    return res
```

Create the pool of workers:
```python
pool = mp.Pool(processes=cpu_count())
```
Prepare the data you need to pass to your function
```python
arguments = []
arguments.append(("data5", 1, 3))
arguments.append(("data3", 2, 5))
arguments.append(("data1", 3, 7))
```
Call the function
```python
results = [pool.apply_async(my_func, args=a) for a in arguments]
```
Get the results. Note that this is the line that actually executes the function.
```python
output = [p.get() for p in results]
```
Use the output as needed
```python
for o in output:
    print(o[prod])
```

