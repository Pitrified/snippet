from generator_class import a_generator
from generator_class import b_generator
from generator_class import c_generator


def main():
    print(f"Test a_generator\n")
    for a in a_generator(10):
        print(f"{a}")

    print(f"\nTest b_generator even\n")
    for b in b_generator(10):
        print(f"{b}")

    print(f"\nTest b_generator odd\n")
    for b in b_generator(9):
        print(f"{b}")

    print(f"\nTest c_generator\n")
    for c in c_generator(9):
        print(f"{c}")


if __name__ == "__main__":
    main()
