import kaldi_io
import numpy as np
import subprocess
import re

class RootHelper(object):
    __slots__ = ('kaldi_dir', 'mdl_path', 'aligz_path', 'phones_path', 'ark_path',) # 用tuple定义允许绑定的属性名称
    def __init__(self):
        self.kaldi_dir = None
        self.mdl_path = None
        self.aligz_path = None
        self.phones_path = None
        self.ark_path = None

root = RootHelper()

def basicConfig(**kwargs):
    root.kaldi_dir = kwargs.pop('kaldi_dir', None)
    root.mdl_path = kwargs.pop('mdl_path', None)
    root.aligz_path = kwargs.pop('aligz_path', None)
    root.phones_path = kwargs.pop('phones_path', None)
    root.ark_path = kwargs.pop('ark_path', None)    

cmd_gmm_info = lambda: '%s/src/gmmbin/gmm-info --print-args=false %s | grep pdfs' % (
    root.kaldi_dir, root.mdl_path)
cmd_ali_pdf = lambda: '%s/src/bin/ali-to-pdf --print-args=false %s "ark:gunzip -c %s|" ark,t:-' % (
    root.kaldi_dir, root.mdl_path, root.aligz_path)
show_alignments = lambda: '%s/src/bin/show-alignments --print-args=false %s %s "ark:gunzip -c %s|"' % (
    root.kaldi_dir, root.phones_path, root.mdl_path, root.aligz_path)
show_transitions = lambda: '%s/src/bin/show-transitions --print-args=false %s %s' % (
    root.kaldi_dir, root.phones_path, root.mdl_path)
copy_int_vector = lambda: '%s/src/bin/copy-int-vector --print-args=false "ark:gunzip -c %s|" ark,t:-' % (
    root.kaldi_dir, root.aligz_path)
alignment = lambda: {k: v for k, v in kaldi_io.read_vec_int_ark(
    root.aligz_path)}

def numpdfs():
    numpdfs = 0
    with subprocess.Popen(cmd_gmm_info(), stdout=subprocess.PIPE, shell=True) as proc:
        numpdfs = int(proc.stdout.readline().decode().strip().split(' ')[-1])
    return numpdfs

def transid2info():
    transid2info = {}
    with subprocess.Popen(show_transitions(), stdout=subprocess.PIPE, shell=True) as proc:
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
    feats = { k:m for k,m in kaldi_io.read_mat_ark(root.ark_path) }
    feats_by_pdfid = [np.zeros((0, 15)) for i in range(numpdfs())]
    with subprocess.Popen(cmd_ali_pdf(), stdout=subprocess.PIPE, shell=True) as proc:
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
