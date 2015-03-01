import music21
import numpy as np
from pyknon.genmidi import Midi
from pyknon.music import *
import os


#codecs.open("new.txt", encoding="utf-8").read()
basedir = "C:\\Users\\Dakota\\rock\\rock_corpus_v2-1"
with open(os.path.join(basedir,"a.txt")) as f:
	s = np.loadtxt(f)
	notes = []
	for note in s:
		dur = note[0]
		pc = int(note[1]) % 12
		octave = int(note[1]) / 12
		print note
		
		notes.append(Note(value = pc, octave = octave, dur = dur))

midi = Midi(1, tempo = 90)
midi.seq_notes(notes, track = 0)
midi.write("hi.mid")


