from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import os

# Dependency imports
from absl import flags
import numpy as np
import scipy.sparse
from six.moves import cPickle as pickle
from six.moves import urllib
import tensorflow as tf
#import tensorflow_probability as tfp

def download(directory, filename):
  """Download a file."""
  filepath = os.path.join(directory, filename)
  if tf.io.gfile.exists(filepath):
    return filepath
  if not tf.io.gfile.exists(directory):
    tf.io.gfile.makedirs(directory)
  # url = os.path.join(ROOT_PATH, filename)
  # print("Downloading %s to %s" % (url, filepath))
  # urllib.request.urlretrieve(url, filepath)
  return filepath


def PubMed_dataset(directory, split_name, num_words):
  """Return tf.data.Dataset."""
  #data = np.load(download(directory, FILE_TEMPLATE.format(split=split_name)), allow_pickle=True, encoding="bytes")
  data = np.load("%s/%s.npy"%(directory, split_name), allow_pickle=True, encoding="latin1")
  # The last row is empty in both train and test.
  # data = data[:-1]

  # Each row is a list of word ids in the document. We first convert this to
  # sparse COO matrix (which automatically sums the repeating words). Then,
  # we convert this COO matrix to CSR format which allows for fast querying of
  # documents.
  #data = np.reshape(data, (3180,))
  num_documents = data.shape[0]
  #print(data)
  indices = np.array([(row_idx, column_idx)
                      for row_idx, row in enumerate(data)
                      for column_idx in row])
  #print(indices[:, 1])
  for i,x in enumerate(indices[:, 1]):
     if x < 0:
        print(i, x)
  sparse_matrix = scipy.sparse.coo_matrix(
      (np.ones(indices.shape[0]), (indices[:, 0], indices[:, 1])),
      shape=(num_documents, num_words),
      dtype=np.float32)
  sparse_matrix = sparse_matrix.tocsr()
  return sparse_matrix

directory = "./data"

with open(download(directory, "cold_dict.pkl"), "rb") as f:
    words_to_idx = pickle.load(f)
num_words = len(words_to_idx)

vocabulary = [None] * num_words
for word, idx in words_to_idx.items():
    #print(word, idx)
    vocabulary[idx] = word

sparse_matrix = PubMed_dataset(directory, 'cold_train', num_words)
sparse_matrix = PubMed_dataset(directory, 'cold_test', num_words)