:<<COMMENT
for ss in {3..10}; do
for nss in {3..10}; do
for totg in 2000 4000 6000 8000 10000; do
	bash run.sh \
	--num-sil-states $ss --num-nonsil-states $nss \
	--totgauss $totg
done
done
done
COMMENT

for sil_prob_10 in {0..10} ; do
    sil_prob=$(bc<<<"$sil_prob_10 * 0.1")
	./run.sh --sil_prob $sil_prob
done
