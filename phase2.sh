rm -f indexes/*.idx

cat data/reviews.txt | perl break.pl | db_load -c duplicates=1 -T -t hash indexes/rw.idx
sort -u data/pterms.txt  | perl break.pl | db_load -c duplicates=1 -T -t btree indexes/pt.idx
sort -u data/rterms.txt  | perl break.pl | db_load -c duplicates=1 -T -t btree indexes/rt.idx
sort -u data/scores.txt  | perl break.pl | db_load -c duplicates=1 -T -t btree indexes/sc.idx