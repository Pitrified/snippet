import ray
import time
from timeit import default_timer as timer

@ray.remote
def f(x):
    time.sleep(1)
    return x

@ray.remote
def fid(x):
    time.sleep(1)
    return (x, x**2)

def ray1(num):
    # Start 4 tasks in parallel.
    print(f'Starting {num} tasks')
    result_ids = []
    for i in range(num):
        result_ids.append(f.remote(i))
        
    # Wait for the tasks to complete and retrieve the results.
    # With at least 4 cores, this will take 1 second.
    print(f'type(result_ids) {type(result_ids)}')
    results = ray.get(result_ids)  # [0, 1, 2, 3]
    print(f'type(results) {type(results)}')

    print(f'type(result_ids[0]) {type(result_ids[0])}')
    print(f'result_ids[0] {result_ids[0]}')

def test_ray1():
    start = timer()
    ray1(8)
    end = timer()
    print(f'Time ray1 {end-start:.6f}')

def ray_dict(num):
    result_ids = []
    for i in range(num):
        result_ids.append(fid.remote(i))

    results_id_pairs = ray.get(result_ids)

    result_ids_dict = {}
    for which, value in results_id_pairs:
        result_ids_dict[which] = value

    return result_ids_dict

def test_ray_dict():
    start = timer()
    result_ids_dict = ray_dict(8)
    end = timer()
    print(f'Time ray_dict {end-start:.6f}')
    print(f'result_ids_dict {result_ids_dict}')

def main():
    # Start Ray.
    ray.init()

    #  test_ray1()
    test_ray_dict()

if __name__ == '__main__':
    main()
