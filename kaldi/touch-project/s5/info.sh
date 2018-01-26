~/Documents/kaldi/src/bin/show-alignments data/lang/phones.txt exp/mono0a/final.mdl "ark:gunzip -c exp/mono0a/decode_train_touch/ali_tmp.1.gz|" > ali-decode
~/Documents/kaldi/src/bin/show-alignments data/lang/phones.txt exp/mono0a/final.mdl "ark:gunzip -c exp/mono0a/ali.1.gz|" > ali-finalmdl
~/Documents/kaldi/src/bin/show-transitions exp/mono0a/phones.txt exp/mono0a/0.mdl > transition-0
~/Documents/kaldi/src/bin/show-transitions exp/mono0a/phones.txt exp/mono0a/final.mdl exp/mono0a/final.occs > transition-final
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=exp/mono0a/graph_tgpr/words.txt exp/mono0a/graph_tgpr/HCLG.fst | dot -Tpdf -oHCLG.pdf -v
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=exp/mono0a/graph_tgpr/words.txt exp/mono0a/graph_tgpr/HCLGa.fst | dot -Tpdf -oHCLGa.pdf -v
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=exp/mono0a/graph_tgpr/phones.txt exp/mono0a/graph_tgpr/Ha.fst | dot -Tpdf -oHa.pdf -v
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=data/lang_test_tg/words.txt -isymbols=data/lang_test_tg/phones.txt data/lang_test_tg/tmp/CLG_1_0.fst | dot -Tpdf -oCLG.pdf -v
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=data/lang_test_tg/words.txt -isymbols=data/lang_test_tg/phones.txt data/lang_test_tg/tmp/LG.fst | dot -Tpdf -oLG.pdf -v
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=data/lang_test_tg/words.txt -isymbols=data/lang_test_tg/phones.txt data/lang_test_tg/G.fst | dot -Tpdf -oG.pdf -v
~/Documents/kaldi/tools/openfst/bin/fstdraw -osymbols=data/lang_test_tg/words.txt -isymbols=data/lang_test_tg/phones.txt data/lang_test_tg/L.fst | dot -Tpdf -oL.pdf -v
~/Documents/kaldi/src/bin/draw-tree exp/mono0a/phones.txt exp/mono0a/tree | dot -Tpdf -otree.pdf
~/Documents/kaldi/src/bin/ali-to-phones --per-frame exp/mono0a/final.mdl "ark:gunzip -c exp/mono0a/ali.1.gz|" ark,t:- > ali-phones-final
~/Documents/kaldi/src/bin/ali-to-pdf --per-frame exp/mono0a/final.mdl "ark:gunzip -c exp/mono0a/ali.1.gz|" ark,t:- > ali-pdf-final
~/Documents/kaldi/src/bin/tree-info exp/mono0a/tree
~/Documents/kaldi/src/bin/hmm-info exp/mono0a/final.mdl
for i in {0..40}; do ~/Documents/kaldi/src/gmmbin/gmm-info exp/mono0a/$i.mdl; done
~/Documents/kaldi/src/featbin/add-deltas ark:/home/fredwei/Documents/kaldi/egs/touch-project/s5/feats/feats_train.ark ark,t:- > deltaddedfeats
~/Documents/kaldi/src/featbin/copy-feats ark:/home/fredwei/Documents/kaldi/egs/touch-project/s5/feats/feats_train.ark ark,t:- > nondeltafeats
for i in {0..40}; do grep 'GCONSTS.\+\[.\+\]' $i.mdl | awk '{SUM += NF - 3} END {print SUM}'; done
