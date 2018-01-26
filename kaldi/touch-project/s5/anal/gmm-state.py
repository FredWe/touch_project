import common
import scipy.io as sio

if __name__ == '__main__':
	for ind, dat in enumerate(common.feats_by_pdfid()):
		print(ind, dat.shape)
	sio.savemat('ark.mat', {'data': common.feats_by_state()})