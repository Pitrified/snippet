# Info on structuring a project

Some good reads
* https://docs.python-guide.org/writing/structure/
* https://dev.to/codemouse92/dead-simple-python-project-structure-and-imports-38c6
* https://docs.python.org/3/tutorial/modules.html
* https://realpython.com/python-application-layouts/

### Folder structure

    .
    ├── .gitignore
    ├── README.md
    ├── setup.py
    ├── src
    │  └── sample
    │     ├── __init__.py
    │     ├── another_lib
    │     │  ├── __init__.py
    │     │  └── another_functions.py
    │     ├── main_sample.py
    │     └── some_lib
    │        ├── __init__.py
    │        ├── some_functions.py
    │        └── some_utils.py
    └── tests
       ├── another_lib
       │  └── test_another_functions.py
       └── some_lib
          ├── test_some_functions.py
          └── test_some_utils.py

### Imports between project files

* https://realpython.com/absolute-vs-relative-python-imports/ (uses a bit too much `__init__.py`, but is very clear)

<!-- Future me might laugh at my naïveté but at the moment I like the clarity of dealing in absolutes. -->

`sample` is the top level package. All imports start with that.

* Inside `some_utils.py` there are `slow_add` and `good_add`
* Inside `some_functions.py` there are `list_slow_add` and `list_good_add`
* Inside `another_functions.py` there is `ListTracker`


To import something in `some_functions.py` from `some_utils.py`, you can use relative imports, with one dot `.` as they are in the same folder:

    # in sample/some_lib/some_functions.py
    from .some_utils import slow_add

or absolute imports:

    # in sample/some_lib/some_functions.py
    from sample.some_lib.some_utils import good_add

To import something in `another_functions.py` from `some_utils.py`, you can use relative imports, with two dots `..` as they share a parent folder.

    # in sample/another_lib/another_functions.py
    from ..some_lib.some_functions import list_slow_add

That folder (`sample`) is marked as package, so the relative import works. If you try to go up too many folders (beyond the package) the following exception is thrown:

    ValueError: attempted relative import beyond top-level package

Absolute imports work as well

    # in sample/another_lib/another_functions.py
    from sample.some_lib.some_functions import list_good_add

And more context can be left in the namespace, loading all `some_utils` and then using `some_utils.good_add`

    # in sample/another_lib/another_functions.py
    from sample.some_lib import some_utils
    sum = some_utils.good_add(4, 5)


### Install the package locally

Create `setup.py` and set it up (https://packaging.python.org/guides/distributing-packages-using-setuptools/)

Install the package locally using

    pip install --editable .


You can check with `pip  list` that the installed package is from the development folder

    Package            Version   Location
    ------------------ --------- ----------------------------------
    sample             0.0.1     /home/Pietro/snippet/py-module/src

### Testing

Run all tests with

    py.test

All the examples you need http://doc.pytest.org/en/latest/example/index.html

To import from the tests, absolute imports are needed: the `tests` folder is outside the package, and cannot access it directly. The package is installed, and used as any package from `pypi`.
