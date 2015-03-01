import pickle;

f = open('tinctoris_histograms.pkl', 'rb')

histograms = pickle.load(f)

print histograms[0]['spine_0'][1.0]

