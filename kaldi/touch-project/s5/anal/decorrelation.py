import kaldi_io
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

NPAD = 15
def plot_values(data, title):
    fig = plt.figure()
    axes = fig.subplots(NPAD, sharey=True)
    for i in range(NPAD):
        axes[i].plot(data[:, i], '-+')
        axes[i].set_ylabel(i)
    axes[0].set_title(title)

def KLT(a):
    """
    Returns Karhunen Loeve Transform of the input and 
    the transformation matrix and eigenval
     
    Ex:
    import numpy as np
    a  = np.array([[1,2,4],[2,3,10]])
     
    kk,m = KLT(a)
    print kk
    print m
     
    # to check, the following should return the original a
    print np.dot(kk.T,m).T
         
    """
    val,vec = np.linalg.eig(np.cov(a))
    klt = np.dot(vec,a)
    return klt,vec,val

feats = {k: m for k, m in kaldi_io.read_mat_ark('../feats/feats_train.ark')}
feats_merged = np.vstack(m for k, m in feats.items())
cov = np.cov(feats_merged, rowvar=False)

# plt.imshow(np.corrcoef(feats_merged, rowvar=False))
# plt.colorbar()
# plt.show()

val, vec = np.linalg.eig(cov)
mean = np.mean(feats_merged, axis=0)
sigma = np.diag(np.std(feats_merged, axis=0))

stretch_factor = np.diag(1 / np.sqrt(val))
t = np.linalg.multi_dot([sigma, vec, stretch_factor, vec.T])

feats_decorr = {}
for k, mat in feats.items():
    dy = np.dot(mat - mean, t)
    feats_decorr[k] = dy + mean

# plt.imshow(np.corrcoef(np.vstack(m for k, m in feats_decorr.items()), rowvar=False))
# plt.colorbar()
# plt.show()

# KL transform / PCA
# feats_decorr = {}
# for k, m in feats.items():
#     d = m - mean
#     dy = np.dot(d, vec)
#     feats_decorr[k] = dy + mean

"""
#inv cov transform
decorr = np.linalg.inv(cov)
feats_decorr = {k: np.dot(vec, m.T).T for k, m in feats.items()}
"""
#sio.savemat('decorr_merged.mat', {'totdata_decorr': np.vstack(m for k, m in feats_decorr.items())})

keey = list(feats.keys())[0]
plot_values(feats[keey], keey)
plot_values(feats_decorr[keey], keey)
plt.show()

with kaldi_io.open_or_fd('../feats/feats_train_decorr.ark', 'wb') as f:
    for k,m in feats_decorr.items():
        kaldi_io.write_mat(f, m, k)
