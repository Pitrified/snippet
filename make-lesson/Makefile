# $@ means 'the target of the current rule' "results.txt"
# $^ means 'all the dependencies of the current rule'
# 	they need to be explicit (make looks for dats)
# $< means 'the first dependency of the current rule'
# % is a Make wildcard
# $* is a special variable which gets replaced by the stem with which the rule matched
# $(...) is a variable reference
# use include to load files

include config.mk

BOOKS_TXT=$(wildcard books/*.txt)
DAT_FILES=$(patsubst books/%.txt, %.dat, $(BOOKS_TXT))

# create results file
results.txt : $(DAT_FILES)
	$(ZIPF_EXE) $^ > $@

# create .dat files
.PHONY : dats
dats : $(DAT_FILES)

%.dat : $(BOOKS_TXT) $(COUNT_SRC)
	$(COUNT_EXE) $< $@

# clean up
.PHONY : clean
clean : 
	rm -f $(DAT_FILES)
	rm -f results.txt

# show variables used
.PHONY : variables
variables :
	@echo BOOKS: $(BOOKS_TXT)
	@echo DAT: $(DAT_FILES)
	@echo LANGUAGE: $(LANGUAGE)
	@echo COUNT_SRC: $(COUNT_SRC)
	@echo ZIPF_SRC: $(ZIPF_SRC)
