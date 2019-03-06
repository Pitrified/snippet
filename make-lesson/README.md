# Basic Makefile

Basic makefile, made following [this guide](https://swcarpentry.github.io/make-novice/).

### Makefile recap
* Use `#` for comments in Makefiles
* Write rules as `target : dependencies`
* Specify update actions in a tab-indented block under the rule
* Use `.PHONY` to mark targets that *don’t* correspond to files
* `$@` means 'the target of the current rule'
* `$^` means 'all the dependencies of the current rule'
* `$<` means 'the first dependency of the current rule'
