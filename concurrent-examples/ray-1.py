import ray
import time
from timeit import default_timer as timer

# Start Ray.
ray.init()

@ray.remote
def f(x):
    time.sleep(1)
    return x

def ray1(num):
    # Start 4 tasks in parallel.
    result_ids = []
    for i in range(num):
        result_ids.append(f.remote(i))
        
    # Wait for the tasks to complete and retrieve the results.
    # With at least 4 cores, this will take 1 second.
    results = ray.get(result_ids)  # [0, 1, 2, 3]

def test_ray1():
    start = timer()
    ray1(8)
    end = timer()
    print(f'Time ray1 {end-start:.6f}')

def main():
    test_ray1()

if __name__ == '__main__':
    main()
