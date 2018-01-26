import kaldi_io
import numpy as np
import subprocess
import re

cmd_gmm_info = '~/Documents/kaldi/src/gmmbin/gmm-info --print-args=false ../exp/mono0a/final.mdl | grep pdfs'
cmd_ali_pdf = '~/Documents/kaldi/src/bin/ali-to-pdf --print-args=false ../exp/mono0a/final.mdl "ark:gunzip -c ../exp/mono0a/ali.1.gz|" ark,t:-'
show_alignments = '~/Documents/kaldi/src/bin/show-alignments --print-args=false ../data/lang/phones.txt ../exp/mono0a/final.mdl "ark:gunzip -c ../exp/mono0a/ali.1.gz|"'
show_decode_alignments = '~/Documents/kaldi/src/bin/show-alignments --print-args=false ../data/lang/phones.txt ../exp/mono0a/final.mdl "ark:gunzip -c ../exp/mono0a/decode_train_touch/ali_tmp.1.gz|"'
show_transitions = '~/Documents/kaldi/src/bin/show-transitions --print-args=false ../exp/mono0a/phones.txt ../exp/mono0a/final.mdl'
copy_int_vector = '~/Documents/kaldi/src/bin/copy-int-vector --print-args=false "ark:gunzip -c ../exp/mono0a/ali.1.gz|" ark,t:-'

decode_alignment = {k: v for k, v in kaldi_io.read_vec_int_ark('../exp/mono0a/decode_train_touch/ali_tmp.1.gz')}
alignment = {k: v for k, v in kaldi_io.read_vec_int_ark('../exp/mono0a/ali.1.gz')}
feats = { k:m for k,m in kaldi_io.read_mat_ark('../feats/feats_train.ark') }

def numpdfs():
    numpdfs = 0
    with subprocess.Popen(cmd_gmm_info, stdout=subprocess.PIPE, shell=True) as proc:
	    numpdfs = int(proc.stdout.readline().decode().strip().split(' ')[-1])
    return numpdfs

def transid2info():
    transid2info = {}
    with subprocess.Popen(show_transitions, stdout=subprocess.PIPE, shell=True) as proc:
        phone = ''
        hmmstate = -1
        pdfid = -1
        transid = -1
        transtext = ''
        for line in proc.stdout:
            line = line.decode().strip()
            m_transtate = re.match(
                r'Transition-state.+phone = (\w+) hmm-state = (\d+) pdf = (\d+)', line)
            m_transid = re.match(
                r'Transition-id = (\d+).+(\[.+\])', line)
            if m_transtate:
                phone, hmmstate, pdfid = m_transtate.group(1), m_transtate.group(2), m_transtate.group(3)
            if m_transid:
                transid, transtext = m_transid.group(1), m_transid.group(2)
                transid2info[int(transid)] = {
                    'phone': phone,
                    'hmmstate': hmmstate,
                    'pdfid': pdfid,
                    'transtext': transtext}
    return transid2info

def pdfid2info():
    pdfid2info = {
        int(it['pdfid']): {
            'phone': it['phone'],
            'hmmstate': it['hmmstate']}
        for it in transid2info().values()}
    return pdfid2info

def feats_by_pdfid():
	feats_by_pdfid = [np.zeros((0, 15)) for i in range(numpdfs())]
	with subprocess.Popen(cmd_ali_pdf, stdout=subprocess.PIPE, shell=True) as proc:
		for line in proc.stdout:
			if not line.decode().endswith('pdf sequences.'):
				outarr = line.decode().strip().split(' ')
				for framei, pdfi in enumerate(outarr[1:]):
					feats_by_pdfid[int(pdfi)] = np.vstack([
						feats_by_pdfid[int(pdfi)],
						feats[outarr[0]][framei]])
	return feats_by_pdfid

def feats_by_state():
	info = pdfid2info()
	return {
		(info[ind]['phone'] + info[ind]['hmmstate']): dat 
		for ind, dat in enumerate(feats_by_pdfid())}
