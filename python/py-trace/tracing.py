from pathlib import Path
import trace


from submodule_a import misc_a  # type: ignore
from submodule_a.subsubmodule_a import specific_a  # type: ignore
from submodule_b import class_b  # type: ignore


def fnoreturn():
    pass


def fc(c):
    return c + 12


def fb(b):
    b = specific_a.subsub_a_spec_1(b, b)
    return fc(b) * 3


def fa(a, b):
    clb = class_b.Sub_b_class1(a, b)
    fnoreturn()
    temp = misc_a.sub_a_misc_1(clb.a, b)
    return fc(a) + fb(temp)


def tracecalls() -> None:
    r"""MAKEDOC: what is tracecalls doing?

    https://docs.python.org/3/library/trace.html
    """

    this_file_folder = Path(__file__).absolute().parent

    cover_folder = this_file_folder / "cover"

    tracer = trace.Trace(
        count=0,
        trace=1,
        countfuncs=0,
        countcallers=1,
        ignoremods=("pathlib"),
    )
    tracer.runfunc(fa, a=2, b=5)
    res = tracer.results()
    # res.write_results(summary=True)
    res.write_results(show_missing=True, coverdir=cover_folder)


def run_tracing() -> None:
    r"""MAKEDOC: What is tracing doing?"""
    # logg = logging.getLogger(f"c.{__name__}.run_tracing")
    # logg.setLevel("DEBUG")
    # logg.debug("Starting run_tracing")

    # tracecalls()
    fa(3, 4)


if __name__ == "__main__":
    # args = setup_env()
    run_tracing()
