from __future__ import division
import nltk
import nltk.classify.svm
import svmlight
import math
from nlp_common import *
posTagHash = {}

def getNGrams(line, n):
    words = nltk.wordpunct_tokenize(line.strip().lower())
    if n == 0:
        tagged_words = nltk.wordpunct_tokenize(line.strip().lower())
	for word in words:
	    if word not in posTagHash:
		posTagHash[word] = nltk.pos_tag([word])[0][1]

        return [posTagHash[word] for word in words]

    if n <= 0:
	return []
    ngrams = nltk.ngrams(words, n)
    ngramArr = []
    for ngram in ngrams:
        ngramStr =  ngram[0]
        for i in range(n-1):
            ngramStr = ngramStr + "##" + ngram[i + 1]
        ngramArr.append(ngramStr)
    
    return ngramArr + getNGrams(line, n - 1) 

  
def getFeatureVectors(filename, ngramHash):
  allFeatures = []
  for line in open(filename):
       ngrams = getNGrams(line, N_IN_NGRAM)
       ufd = nltk.FreqDist(ngrams);
       subHash = {} 
       maxFd = max(ufd.values());
       for ngram in ufd.keys():
           subHash[ngram] = ngramHash[ngram]
       sortedKeys = sorted(subHash, key=lambda key: subHash[key])
       features = []
       for ngramtype in sortedKeys:
           features.append((str(ngramHash[ngramtype]), str((float(ufd[ngramtype])/maxFd) * math.log(TOT_NUM_DOCS/df[ngramtype]))))
       allFeatures.append(features)
  return allFeatures

textDir = "hotel-reviews"
truthfulRevFile = textDir + "/hotel_truthful"
deceptiveRevFile = textDir + "/hotel_deceptive"


ngramHash = {}
df = {}
idx = 0;
truthfulRevs = []
for line in open(truthfulRevFile):
    truthfulRevs.append(line)
    wt = {}
    for ngram in getNGrams(line, N_IN_NGRAM):
      if ngram not in ngramHash:
          idx = idx + 1
          ngramHash[ngram] = idx
      if ngram not in wt:
          if ngram not in df:
              df[ngram] = 1
          else:
              df[ngram] = df[ngram] + 1
          wt[ngram] = True

deceptiveRevs = []
for line in open(deceptiveRevFile):
    deceptiveRevs.append(line)
    wt = {}
    for ngram in getNGrams(line, N_IN_NGRAM):
      if ngram not in ngramHash:
          idx = idx + 1
          ngramHash[ngram] = idx
      if ngram not in wt:
          if ngram not in df:
              df[ngram] = 1
          else:
              df[ngram] = df[ngram] + 1
          wt[ngram] = True


trueFeatures = getFeatureVectors(truthfulRevFile, ngramHash)
deceptiveFeatures = getFeatureVectors(deceptiveRevFile, ngramHash)

for i in range(int(NUM_DOC_PER_LABEL)):
    trueRev = trueFeatures[i]
    print "-1",
    for (feat, val) in trueRev:
        print " " + feat + ":" + val,
    deceptiveRev = deceptiveFeatures[i]
    print ""
    print "+1",
    for (feat, val) in deceptiveRev:
        print " " + feat + ":" + val,
    print ""
    

whfile = open("info/Hash_" + str(N_IN_NGRAM) + "_Grams.txt", "w");
srtd = sorted(ngramHash, key=lambda key:  ngramHash[key])
totdf = 0
for key in srtd:
    whfile.write(str(ngramHash[key]) + " : " + key + " : " + str(df[key]) + "\n");
    totdf = totdf + df[key]
whfile.write("Average DF: " + str(totdf/len(df.keys())))

if N_IN_NGRAM == 0:
    whfile = open("info/Hash_" + str(N_IN_NGRAM) + "_POS.txt", "w");
    #srtd = sorted(posTagHash, key=lambda key:  posTagHash[key])
    for key in posTagHash:
        whfile.write(key + " : " + str(posTagHash[key]) +  "\n");

#avg_df =  reduce(lambda x, y: x + y, df.values()) / len(df.values())
#print "Average DF: " + str(avg_df)

