# USAGE: bash run_pipeline.sh
# to produce plots for isles and abyss
# and the summary table for the Zipf's law tests

python countwords.py books/isles.txt isles.dat
python countwords.py books/abyss.txt abyss.dat

python plotcounts.py isles.dat isles.png
python plotcounts.py abyss.dat abyss.png

# Generate summary table
python testzipf.py abyss.dat isles.dat > results.txt
