import kaldi_io
import numpy as np
import matplotlib.pyplot as plt
from sklearn import mixture
import common

feats_merged = np.vstack(m for k,m in common.feats.items())

# fit a Gaussian Mixture Model with two components
clf = mixture.GaussianMixture(n_components=400, covariance_type='full')
clf.fit(feats_merged)

pred = clf.predict(feats_merged)
pred_proba = clf.predict_proba(feats_merged)
logprob = clf.score_samples(feats_merged)
print('---logprob.shape---')
print(logprob.shape)
print('---logprob---')
print(logprob)
print('---pred.shape---')
print(pred.shape)
print('---pred---')
print(pred)
print('---pred_proba---')
print(pred_proba)
print('---clf---')
print(clf)
print('---clf.weights_---')
print(clf.weights_)
print('---clf.means_---')
print(clf.means_)
print('---covariances_---')
print(clf.covariances_)
print('---precisions_---')
print(clf.precisions_)
print('---lower_bound_---')
print(clf.lower_bound_)
