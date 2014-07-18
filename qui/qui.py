# Attempting to use Cosine Similiarty here due to the large number of text
# features. The code still needs significant debugging to check lookups.
# I also mistakenly started off using the metadata but have removed it below by
# slicing on the data when I call the TfidfVectorizer. Unfortunately, although
# it is returning some documents as matches, there is certainly a problem with
# those results.

from __future__ import division, print_function
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import cm

import glob as glob

import os


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def similarity(x_test, X_train, N=1):
    '''
    '''
    #N = min(N, X_train.shape[0])



    cos_sim = cosine_similarity(x_test, X_train)[0]

    idx = cos_sim.argsort()[-N:][::-1]
    scores = cos_sim[idx]

    return idx, scores


def main():
    '''
    '''
    
    metaname = 'poem-corpus/meta/metadata.csv'

    metadata = {}
    with open(metaname, "r") as fobj:
        for line in fobj:
            info = line.split(',')

            if 'file' in info[0]:
                fields = info
            else:
                file_index = info[0]
                #print(info)
                metadata[file_index] = info[1:]

    flist = glob.glob('poem-corpus/[0-99]*')
    #flist.sort()
    #print(flist)
    for fn in flist:
        with open(fn,"r") as fobj:
            title = fobj.readline()
            text = fobj.readlines()
            num_lines = len(text)
            filename = fn.split("/")[-1]
            text = "".join(text)
            if filename in metadata:
                metadata[filename].extend([title, text])
            else:
                #discard these ones without metadata
                pass
            #print(title, num_lines, text )
            #            metadata[filename].extend([title,num_lines,text])

    sorted_keys = sorted(metadata.keys())
    data = []
    for each in sorted_keys:
        data.append(" ".join(metadata[each]) )
        
    vectorizer = TfidfVectorizer()

    X = vectorizer.fit_transform(data[:-1][5:])
    x_test = vectorizer.transform(data[-1][5:])
    #print(vectorizer.get_feature_names())

    idxs, scores = similarity(x_test, X, N=10)
    best_matches = np.array(data)[idxs]
    print(scores)

    print("Target Document\n", data[-1].split()[:20])
    print()
    for each in best_matches:
        words = each.split()
        print(words[:20])




if __name__ == "__main__":

    main()
