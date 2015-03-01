import os
from pyknon.genmidi import Midi
from pyknon.music import *
from music21 import *
import random
import numpy as np
import glob
import pickle

basedir = 'C:\\rock'

# get trigrams
histograms = pickle.load(open(os.path.join(basedir, "t.pkl"), "rb"))

strong_beats = []
weighted_strong_beats = []
strong_beat_counts = []
weak_beats   = []
weighted_weak_beats = []
weak_beat_counts = []

for p in histograms:
	for part in p:
		for s in p[part][1.0]:
			strong_beat_counts.append(p[part][1.0][s])
		for s in p[part][0.5]:
			weak_beat_counts.append(p[part][0.5][s])

		strong_beats.extend(p[part][1.0])
		weak_beats.extend(p[part][0.5])



for i, count in enumerate(strong_beat_counts):
	weighted_strong_beats.extend([strong_beats[i]] * count)

for i, count in enumerate(weak_beat_counts):
	weighted_weak_beats.extend([weak_beats[i]] * count)

song_count = 0

for (song_count,song) in enumerate(glob.glob(os.path.join(basedir,"*.mid"))):

	stream = converter.parse(song)
	
	part_notes = []
	part_durs   = []
	part_positions = []
	part_offsets = []
	part_midis = []


	# all the demo midis are 1 part so this is kind of useless
	for (i,part) in enumerate(stream):
		# midi numbers
		part_midis.append([n.pitch.midi for n in part.getElementsByClass(note.Note)])
		# pitch classes
		part_notes.append([n.pitch.pitchClass for n in part.getElementsByClass(note.Note)])
		# length in fractions of whole notes
		part_durs.append([n.duration.quarterLength / 4 for n in part.getElementsByClass(note.Note)])
		# position in the beat. 1 is downbeat, .5 is halfway through a measure
		# by only substituting on these positions, some of the
		# "this sounds like the beginning of a measure"-ness gets preserved
		part_positions.append([n.beatStrength for n in part.getElementsByClass(note.Note)])
		# how offset from the beginning of the piece a note is
		# for example if offsets % 8 == 0 and the song is in 4/4
		# that means we change a downbeat every OTHER measure
		part_offsets.append([int(n.offset) for n in part.getElementsByClass(note.Note)])


	notes = []
	ngram_length = 3

	start_note = part_midis[0][0]
	start_dur  = part_durs[0][0]

	# don't change the first note!
	notes.append(Note(value = start_note % 12, octave = start_note / 12, dur = start_dur))
	# iterates over the part_positions
	# using a raw iterator is a brutal hack to let me skip positions in the iterator

	beat_class_iter = iter(part_positions[0])

	# the lower these are, the more likely that type of beat will be modified
	strong_beat_threshold = .4
	weak_beat_threshold = .7

	# if a position is identified as good to change,
	# the first note is changed, and the two notes after
	# are changed to make the whole three-note unit
	# one of the trigrams starting at the original pitch

	loc = 0
	for note in beat_class_iter:
		loc += 1
		if (loc >= len(part_positions[0]) - 4):
			break
		# change this to % 8; %4 doesn't do anything but i'm too lazy to edit it
		if (part_positions[0][loc] == 1.0 and part_offsets[0][loc] % 4 == 0 and random.random() > strong_beat_threshold):
			
			beat_class_iter.next()
			beat_class_iter.next()
			loc += 2

			offset = [0]
			for el in random.choice(weighted_weak_beats):
				offset.append(el)

			for j in range(ngram_length):
				midi_number = part_midis[0][loc+j] + offset[j]
				dur         = part_durs[0][loc+j]
				notes.append(Note(midi_number % 12, midi_number / 12, dur = dur))

		elif (part_positions[0][loc] == .5 and part_offsets[0][loc] % 6 == 0 and random.random() > weak_beat_threshold):
			
			beat_class_iter.next()
			beat_class_iter.next()
			loc += 2

			offset = [0]
			for el in random.choice(weighted_weak_beats):
				offset.append(el)


			for j in range(ngram_length):
				midi_number = part_midis[0][loc+j] + offset[j]
				dur         = part_durs[0][loc+j]
				notes.append(Note(midi_number % 12, midi_number / 12, dur = dur))

					
		else:
			midi_number = part_midis[0][loc]
			dur   = part_durs[0][loc]
			notes.append(Note(midi_number % 12, midi_number / 12, dur = dur))



	# pyknon is a horrible horrible library but it gets the job done!
	midi = Midi(1, tempo = 120)
	midi.seq_notes(notes, track = 0)
	midi.write(os.path.join(basedir, str(song_count)+".mid"))