import os
import music21 

basedir = 'C:\\jrp-scores'

for _,_, files in os.walk(basedir):
	for file in files:
		if not ("krn" in file):
			continue
		print os.path.join(subdir,file)
		try:
			s = music21.converter.parse(os.path.join(subdir,file))
			s.write('midi', os.path.join(basedir,file[:-4]) + ".mid")
		except:
			continue

