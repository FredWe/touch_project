#!/bin/bash
set -e

run_cmd="utils/run.pl"

train_basename=train_touch
test_basename=test_touch

nj=1

rm -rf data exp cmvn

num_sil_states=3
num_nonsil_states=3
totgauss=400
realign_iters="1 2 3 4 5 6 7 8 9 10 12 14 16 18 20 23 26 29 32 35 38";
#realign_iters=$(echo {1..40});
sil_prob=0.9

echo "$0 $@"  # Print the command line for logging
. utils/parse_options.sh

# Data preparation
bash local/create_touch_test_train.sh
local/prepare_dict.sh
utils/prepare_lang.sh \
	--num-sil-states $num_sil_states --num-nonsil-states $num_nonsil_states \
	--position-dependent-phones false --sil-prob $sil_prob\
	data/local/dict "<SIL>" data/local/lang data/lang
local/prepare_lm.sh
python3 local/prepare_data.py

# Feature extraction
for x in $train_basename $test_basename; do 
 steps/compute_cmvn_stats.sh data/$x exp/make_cmvn/$x cmvn
 utils/fix_data_dir.sh data/$x
done

# Mono training
steps/train_mono.sh \
    --nj $nj --cmd "$run_cmd" \
    --totgauss $totgauss --realign-iters "$realign_iters" \
    data/$train_basename data/lang exp/mono0a 
  
# Graph compilation  
utils/mkgraph.sh data/lang_test_tg exp/mono0a exp/mono0a/graph_tgpr

# Decoding
steps/decode.sh --nj $nj --cmd "$run_cmd" \
    --scoring-opts "--word-ins-penalty 0,1,10" \
    exp/mono0a/graph_tgpr data/$train_basename exp/mono0a/decode_$train_basename

for x in exp/*/decode*; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done

#gridsearch
bestwer=$(cat exp/mono0a/decode_train_touch/scoring_kaldi/best_wer | cut -d' ' -f 2)
touch "sil_prob$sil_prob->WER$bestwer"

:<<EOF
#gridsearch
bestwer=$(for x in exp/*/decode*; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; done | cut -d' ' -f 2)
mkdir -p output/ss${num_sil_states}nss${num_nonsil_states}totg${totgauss}wer${bestwer}
mv data exp cmvn output/ss${num_sil_states}nss${num_nonsil_states}totg${totgauss}wer${bestwer}
EOF

#steps/score_kaldi.sh --cmd "$run_cmd" \
#	data/$train_basename exp/mono0a/graph_tgpr exp/mono0a/decode_$train_basename
	
