for i in ./*.pdf; do
    pdftk "$i" dump_data | grep NumberOfPages | awk '{print $2}'
done
