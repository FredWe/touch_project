kaldi_dir=/home/fredwei/Documents/kaldi
project_dir=$kaldi_dir/egs/touch-project
feats_dir=$project_dir/s5/feats
data_dir=$project_dir/s5/data
datatrain_dir=$data_dir/train_touch
datatest_dir=$data_dir/test_touch

for dir in $datatrain_dir $datatest_dir; do
    if ! [ -d $dir ]; then
        mkdir -p $dir
    fi
done
$kaldi_dir/src/featbin/copy-feats ark:$feats_dir/feats_train.ark ark,t,scp:$datatrain_dir/feats.ark,$datatrain_dir/feats.scp
$kaldi_dir/src/featbin/copy-feats ark:$feats_dir/feats_test.ark ark,t,scp:$datatest_dir/feats.ark,$datatest_dir/feats.scp
