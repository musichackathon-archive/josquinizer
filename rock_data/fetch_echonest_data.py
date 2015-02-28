import os
import urllib
import json
import pandas as pd
import time

def getNamesFromFileName(names_df, filename):
  try:
    track_name = names_df[names_df.filename==filename].track_name.values[0]
    artist_name = names_df[names_df.filename==filename].artist_name.values[0]
  except IndexError:
    return None, None
  return artist_name, track_name

def getSongAndTrackIDs(names_df, filename):
  artist_name, song_name = getNamesFromFileName(names_df, filename)
  if artist_name is None or song_name is None:
    return None, None
  print "  %s - %s" % (artist_name, song_name)
  url = "http://developer.echonest.com/api/v4/song/search?api_key=K9SVE4GSTAS5SJLAX&format=json&sort=song_hotttnesss-desc&bucket=tracks&bucket=id:spotify&results=1&"
  if artist_name.lower().startswith('the '):
    artist_name = artist_name[4:]
  url += urllib.urlencode([
    ('artist', artist_name),
    ('title',song_name)
    ])
  # url = "http://developer.echonest.com/api/v4/song/search?api_key=K9SVE4GSTAS5SJLAX&format=json&sort=song_hotttnesss-desc&bucket=tracks&bucket=id:spotify&results=1&"
  # url += urllib.urlencode([
  #   ('combined', artist_name+" "+song_name)
  #   ])
  response = urllib.urlopen(url);
  data = json.loads(response.read())
  print "  "+str(data)
  if not data['response']['songs'] or not data['response']['songs'][0]['tracks']:
    return None, None
  songID = data['response']['songs'][0]['id']
  trackID = data['response']['songs'][0]['tracks'][0]['id']
  return songID, trackID

def getSongData(filename, songID):
  try:
    os.makedirs('echonest')
  except OSError:
    pass
  url = "http://developer.echonest.com/api/v4/track/profile?api_key=K9SVE4GSTAS5SJLAX&format=json&id=%s&bucket=audio_summary" % songID
  response = urllib.urlopen(url);
  data = json.loads(response.read())
  # be lazy, just request it again and put it in a file
  urllib.urlretrieve(url, 'echonest/%s.json'%filename)
  # now, download the full analysis too
  print "  "+str(data)
  audio_summary = data['response']['track']['audio_summary']
  if 'analysis_url' in audio_summary:
    analysis_url = audio_summary['analysis_url']
    urllib.urlretrieve(analysis_url, 'echonest/%s.full_analysis.json'%filename)


# first, load the names dataframe
names_df = pd.read_csv('rs200.txt', sep="\t", names=['filename', 'rs500_rank', 'track_name', 'artist_name', 'year', 'dunno'])

for dirname, dirnames, filenames in os.walk('rock_corpus_v2-1/timing_data'):
    for name in filenames:
      if name.startswith('.'):
        continue
      name = name[:-4]
      print name
      songID, trackID = getSongAndTrackIDs(names_df, name)
      if trackID is None:
        print "  Could not find song ID!  Skipping..."
        continue
      getSongData(name, trackID)
      # we have a limit of 120 calls per minute, so let's rate-limit ourselves
      # we make a max of 4 calls per loop, so we can do 30 loops per minute
      # since we don't want to deal with rate limiting code, let's just keep it simple here
      # ... and be patient :)
      time.sleep(2)
