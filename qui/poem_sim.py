
'''
Python script to find similarities in poems. Uses a text vectorizer to build
a numerical representation and compare vocabularies via the cosine similarity.
The high dimensional vocabulary space makes cosine similarity a better choice
than Euclidean Distance.


Some interesting thigns to explore here would be the effect of
1) bigrams/trigrams to create better features, 
2) comparison on more than just cosine similarity
3) building in some more evaluation strategies for comparsion besides vocab
    i.e. Sentiments. Perhaps very different vocabulary poems could have similar
    emotional content/similarity.

'''

from __future__ import division, print_function
import numpy as np
import glob as glob
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def main():
    '''
    Requires a path to a target document as a command line argument. In addition
    you can specify the number of documents N to return as most similar to the
    target document.

    USAGE: $python poem_sim.py <target_poem> N
    '''
    print("USAGE: $python poem_sim.py <path_to_target_poem> N")
    # Check number of arguments
    assert( len(sys.argv) <= 3)

    # Set some fallback parameters
    target_document = 'poem-corpus/poem_document'
    N = 5

    # Try to add the user-specified parameters
    if len(sys.argv) > 1:
        target_document = sys.argv[1]
        if open(target_document,"r") is None:
            print("<path_to_target_opem> can't be opened.\n")
            print("USAGE: $python poem_sim.py <path_to_target_poem> N")
            exit(1)
    if len(sys.argv) > 2:
        N = int(sys.argv[2])

    # Log the current parameters to the console
    print("Target Document={0}, N={1}".format(target_document,N))

    flist = glob.glob('poem-corpus/[0-99]*')
    flist.extend([target_document])
    data = []
    for fn in flist:
        print(fn)
        with open(fn,"r") as fobj:
            text = fobj.readlines()
            data.append(" ".join(text))

    vectorizer = TfidfVectorizer(max_df=0.5)
    X = vectorizer.fit_transform(data[:-1])
    x_test = vectorizer.transform([data[-1]])

    cos_sim = cosine_similarity(x_test, X)[0]
    print("COSINE SIMILARITY for target_doc versus corpus")
    print(cos_sim)
    top_idxs = np.argsort(cos_sim)[-N:][::-1]
    top_scores = np.sort(cos_sim)[-N:][::-1]
    print("\tTARGET POEM TEXT")
    print(data[-1],"\n")

    print("\tTOP N SCORES and POEM TEXT")
    for scr,idx in zip(top_scores,top_idxs):
        print("SCORE={0}".format(scr))    
        print("POEM TEXT\n",np.array(data)[idx])

if __name__ == "__main__":

    main()
