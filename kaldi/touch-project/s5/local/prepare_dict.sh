#!/bin/bash

mkdir -p data/local/dict

cp input/lexicon_nosil.txt data/local/dict/lexicon_words.txt

cp input/lexicon.txt data/local/dict/lexicon.txt

cat input/phones.txt | grep -v SIL | grep -v P > data/local/dict/nonsilence_phones.txt

cp input/silence_phones.txt data/local/dict/silence_phones.txt

echo "SIL" > data/local/dict/optional_silence.txt

echo "Dictionary preparation succeeded"
