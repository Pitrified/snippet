from mod.sub_mod_a.file_a import func_a


def func_b(a: int, b: int) -> int:
    func_a(a, b)
    # func_a("string")
    return 0
