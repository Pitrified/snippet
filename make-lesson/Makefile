# $@ means 'the target of the current rule' "results.txt"
# $^ means 'all the dependencies of the current rule'
# 	they need to be explicit (make looks for dats)
# $< means 'the first dependency of the current rule'
# % is a Make wildcard
# $* is a special variable which gets replaced by the stem with which the rule matched
# $(...) is a variable reference
# use include to load files

include config.mk

# create results file
results.txt : isles.dat abyss.dat last.dat
	$(ZIPF_EXE) $^ > $@

# create .dat files
.PHONY : dats
dats : isles.dat abyss.dat last.dat

%.dat : books/%.txt $(COUNT_SRC)
	$(COUNT_EXE) $< $*.dat

# clean up
.PHONY : clean
clean : 
	rm -f *.dat
	rm -f results.txt
