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
PNG_FILES=$(patsubst books/%.txt, %.png, $(BOOKS_TXT))

.PHONY : all
all : results.txt $(PNG_FILES)

## results.txt : generate Zipf summary table
results.txt : $(ZIPF_SRC) $(DAT_FILES)
	$(ZIPF_EXE) $(DAT_FILES) > $@

## dats : count words in text files
.PHONY : dats
dats : $(DAT_FILES)

%.dat : books/%.txt $(COUNT_SRC)
	$(COUNT_EXE) $< $@

## pngs : create pngs from dat
# python plotcounts.py isles.dat isles.png
.PHONY : pngs
pngs : $(PNG_FILES)

%.png : %.dat $(GEN_PNG_SRC)
	$(GEN_PNG_EXE) $< $@

## clean : remove auto-generated files
.PHONY : clean
clean : 
	rm -f $(DAT_FILES)
	rm -f $(PNG_FILES)
	rm -f results.txt

## variables : print variables used
.PHONY : variables
variables :
	@echo BOOKS: $(BOOKS_TXT)
	@echo DAT: $(DAT_FILES)
	@echo PNG: $(PNG_FILES)
	@echo LANGUAGE: $(LANGUAGE)
	@echo COUNT_SRC: $(COUNT_SRC)
	@echo ZIPF_SRC: $(ZIPF_SRC)

.PHONY : help
help : Makefile
	@sed -n 's/^##//p' $<
