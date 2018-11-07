"""
===========================
Within Session P300
===========================

This Example shows how to perform a within session analysis on three different
P300 datasets.

We will compare two pipelines :

- Riemannian Geometry
- xDawn with Linear Discriminant Analysis

We will use the P300 paradigm, which uses the AUC as metric.

"""
# Authors: Pedro Rodrigues <pedro.rodrigues01@gmail.com>
#
# License: BSD (3-clause)

# getting rid of the warnings about the future (on s'en fout !)
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

import moabb

from moabb.paradigms import P300
from moabb.evaluations import WithinSessionEvaluation

from pyriemann.estimation import ERPCovariances, Xdawn
from pyriemann.tangentspace import TangentSpace

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

moabb.set_log_level('info')

# This is an auxiliary transformer that allows one to vectorize data structures in a pipeline
# For instance, in the case of a X with dimensions Nt x Nc x Ns, one might be interested in
# a new data structure with dimensions Nt x (Nc.Ns)


class Vectorizer(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y):
        """fit."""
        return self

    def transform(self, X):
        """transform. """
        return np.reshape(X, (len(X),-1))

##############################################################################
# Create pipelines
# ----------------
#
# Pipelines must be a dict of sklearn pipeline transformer.


pipelines = {}

# we have to do this because the classes are called 'Target' and 'NonTarget' but the
# evaluation function uses a LabelEncoder, transforming them to 0 and 1
labels_dict = {'Target': 1, 'NonTarget': 0}

pipelines['RG + LogReg'] = make_pipeline(ERPCovariances(estimator='lwf',
                                                                    classes=[labels_dict['Target']]),
                                         TangentSpace(),
                                         LogisticRegression())

pipelines['Xdw + LDA'] = make_pipeline(Xdawn(nfilter=4, estimator='lwf'), Vectorizer(), LDA(solver='lsqr',
                                                                                            shrinkage='auto'))

##############################################################################
# Evaluation
# ----------
#
# We define the paradigm (P300) and use all three datasets available for it.
# The evaluation will return a dataframe containing a single AUC score for
# each subject / session of the dataset, and for each pipeline.
#
# Results are saved into the database, so that if you add a new pipeline, it
# will not run again the evaluation unless a parameter has changed. Results can
# be overwritten if necessary.

paradigm = P300()
overwrite = False  # set to True if we want to overwrite cached results
evaluation = WithinSessionEvaluation(paradigm=paradigm, datasets=paradigm.datasets,
                                     suffix='examples', overwrite=overwrite)

results = evaluation.process(pipelines)

##############################################################################
# Plot Results
# ----------------
#
# Here we plot the results.

fig, ax = plt.subplots(facecolor='white', figsize=[8, 4])

sns.stripplot(data=results, y='score', x='pipeline', ax=ax, jitter=True,
              alpha=.5, zorder=1, palette="Set1")
sns.pointplot(data=results, y='score', x='pipeline', ax=ax,
              zorder=1, palette="Set1")

ax.set_ylabel('ROC AUC')
ax.set_ylim(0.5, 1)

fig.show()
