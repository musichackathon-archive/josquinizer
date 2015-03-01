# First download the http://josquin.stanford.edu/ corpus from https://github.com/josquin-research-project/jrp-scores
import os
import glob
from music21 import *
import pickle

# info of the corpus
corpusFolder = r'/Users/ugur/Documents/jrp-scores/'
composerFolders = glob.glob(corpusFolder+'/???')
composerNames = [folder[-3:] for folder in composerFolders]
for name, folder in zip(composerNames, composerFolders):
    krnFiles = glob.glob( folder+'/kern/*.krn' )
    print name, len(krnFiles)
    
# functions
def calculateNGrams(score, n=2):
    ngrams = dict()
    for ind, p in enumerate(score[:-n]):
        if not ngrams.has_key(p.beatStrength):
            ngrams[p.beatStrength] = []
        differences = tuple(score[ind+i+1].midi-score[ind+i].midi for i in range(n))
        ngrams[p.beatStrength].append( differences )
    return ngrams

def calculateHistogramsFromNGrams(ngrams):
    strengths = ngrams.keys()
    histograms = dict()

    for strength in strengths:
        keys = set(ngrams[strength])
        histogram = dict()
        for key in keys:
            histogram[key] = 0
        for g in ngrams[strength]:
            histogram[g] += 1

        histograms[strength] = histogram
    return histograms

def calculateHistogramsOfPartsFromAPiece(filePath):
    print "loading", filePath
    stream = converter.parse(filePath)
    print "num parts", len(stream.parts)
    histograms = dict()
    for part in stream.parts:
        print "part ID", part.id
        notes = part.flat.getElementsByClass(note.Note) 
        print "part length", len(notes)
        print "calculate ngrams of " + part.id
        ngrams = calculateNGrams(notes)
        print "calculate histograms of " + part.id
        histograms[part.id] = calculateHistogramsFromNGrams(ngrams)
    return histograms

def addHistograms(hist1, hist2):
    hist = dict(hist1)
    for k, v in hist2.items():
        if hist.has_key(k):
            hist[k] += v
        else:
            hist[k] = v
    return hist

# calculate histograms of each beatStrength of each part of each piece
hists = []
composerID = 'Tin' # a randomly chosen composer :-)
composerSongPaths = glob.glob( os.path.join(corpusFolder, composerID, 'kern', '*.krn') )
for filePath in composerSongPaths:
    hist = calculateHistogramsOfPartsFromAPiece(filePath)
    hists.append(hist)
    

# combine histograms of all pieces
partIDs = ['spine_0', 'spine_1', 'spine_2', 'spine_3'] # for some reason
strengths = [0.0625, 0.125, 0.25, 0.5, 1.0]
combined = dict()
for partID in partIDs:
    combined[partID] = dict()
    for strength in strengths:
        strengthHists = []
        for hist in hists:
            if hist[partID].has_key(strength):
                strengthHists.append(hist[partID][strength])
        combined[partID][strength] = reduce(addHistograms, strengthHists)
        
f = open('tinctoris_histograms.pkl','wb')
pickle.dump(hists, f)
f.close()