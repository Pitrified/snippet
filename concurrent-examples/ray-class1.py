import ray
import time
from timeit import default_timer as timer

class Class_1:
    def __init__(self, x):
        time.sleep(1)
        self.x = x

    def __repr__(self):
        return f'Class_1 x: {self.x}'

@ray.remote
def new_class_instance(x):
    return (x, Class_1(x))

def ray_class_dict(num):
    class_dict = {}

    results_ray = []
    for i in range(num):
        results_ray.append(new_class_instance.remote(i))

    results_ray_get = ray.get(results_ray)

    for which, instance in results_ray_get:
        class_dict[which] = instance

    return class_dict

def test_ray_class_dict():
    start = timer()
    result_class_dict = ray_class_dict(8)
    end = timer()
    print(f'Time ray_dict {end-start:.6f}')
    print(f'result_class_dict {result_class_dict}')


def main():
    # Start Ray.
    ray.init()

    test_ray_class_dict()

if __name__ == '__main__':
    main()
