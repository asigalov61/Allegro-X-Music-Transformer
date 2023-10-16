# -*- coding: utf-8 -*-
"""Allegro_X_Music_Transformer_Training_Dataset_Maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/asigalov61/Allegro-X-Music-Transformer/blob/main/Training-Data/Allegro_X_Music_Transformer_Training_Dataset_Maker.ipynb

# Allegro X Music Transformer Training Dataset Maker (ver. 2.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

#### Project Los Angeles

#### Tegridy Code 2023

***

# (SETUP ENVIRONMENT)
"""

#@title Install all dependencies (run only once per session)

!git clone https://github.com/asigalov61/tegridy-tools
!pip install tqdm

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os

import math
import statistics
import random

from tqdm import tqdm

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

print('Loading TMIDIX module...')
os.chdir('/content/tegridy-tools/tegridy-tools')

import TMIDIX

print('Done!')

os.chdir('/content/')
print('Enjoy! :)')

"""# (DOWNLOAD SOURCE MIDI DATASET)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download original LAKH MIDI Dataset

# %cd /content/Dataset/

!wget 'http://hog.ee.columbia.edu/craffel/lmd/lmd_full.tar.gz'
!tar -xvf 'lmd_full.tar.gz'
!rm 'lmd_full.tar.gz'

# %cd /content/

#@title Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

"""# (FILE LIST)"""

#@title Save file list
###########

print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset"
# os.chdir(dataset_addr)
filez = list()
for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    filez += [os.path.join(dirpath, file) for file in filenames]
print('=' * 70)

if filez == []:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

print('Randomizing file list...')
random.shuffle(filez)

TMIDIX.Tegridy_Any_Pickle_File_Writer(filez, '/content/drive/MyDrive/filez')

#@title Load file list
filez = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/drive/MyDrive/filez')

"""# (PROCESS)"""

#@title Process MIDIs with TMIDIX MIDI processor

print('=' * 70)
print('TMIDIX MIDI Processor')
print('=' * 70)
print('Starting up...')
print('=' * 70)

###########

START_FILE_NUMBER = 0
LAST_SAVED_BATCH_COUNT = 0

input_files_count = START_FILE_NUMBER
files_count = LAST_SAVED_BATCH_COUNT

melody_chords_f = []

stats = [0] * 129

print('Processing MIDI files. Please wait...')
print('=' * 70)

for f in tqdm(filez[START_FILE_NUMBER:]):
    try:
        input_files_count += 1

        fn = os.path.basename(f)

        # Filtering out giant MIDIs
        file_size = os.path.getsize(f)

        if file_size <= 1000000:

          #=======================================================
          # START PROCESSING

          # Convering MIDI to ms score with MIDI.py module
          score = TMIDIX.midi2single_track_ms_score(open(f, 'rb').read(), recalculate_channels=False)

          # INSTRUMENTS CONVERSION CYCLE
          events_matrix = []
          itrack = 1
          patches = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

          while itrack < len(score):
              for event in score[itrack]:
                  if event[0] == 'note' or event[0] == 'patch_change':
                      events_matrix.append(event)
              itrack += 1

          events_matrix.sort(key=lambda x: x[1])

          events_matrix1 = []

          for event in events_matrix:
                  if event[0] == 'patch_change':
                        patches[event[2]] = event[3]

                  if event[0] == 'note':
                        event.extend([patches[event[3]]])

                        events_matrix1.append(event)

          if len(events_matrix1) > 0:
            if min([e[1] for e in events_matrix1]) >= 0 and min([e[2] for e in events_matrix1]) >= 0:

              #=======================================================
              # PRE-PROCESSING

              # checking number of instruments in a composition
              instruments_list_without_drums = list(set([y[3] for y in events_matrix1 if y[3] != 9]))
              instruments_list = list(set([y[3] for y in events_matrix1]))

              if len(events_matrix1) > 0 and len(instruments_list_without_drums) > 0:

                # recalculating timings
                for e in events_matrix1:
                    e[1] = int(e[1] / 8) # Max 2 seconds for start-times
                    e[2] = int(e[2] / 16) # Max 4 seconds for durations

                # Sorting by pitch, then by start-time
                events_matrix1.sort(key=lambda x: x[3])
                events_matrix1.sort(key=lambda x: x[4], reverse=True)
                events_matrix1.sort(key=lambda x: x[1])

                 #=======================================================
                # FINAL PRE-PROCESSING

                melody_chords = []

                pe = events_matrix1[0]

                for e in events_matrix1:

                    # Cliping all values...
                    time = max(0, min(255, e[1]-pe[1]))
                    dur = max(1, min(255, e[2]))
                    cha = max(0, min(15, e[3]))
                    ptc = max(1, min(127, e[4]))

                    # Calculating octo-velocity
                    vel = max(1, min(127, e[5]))

                    pat = max(0, min(127, e[6]))

                    # Writing final note
                    melody_chords.append([time, dur, cha, ptc, vel, pat])

                    pe = e

                #=======================================================
                # FINAL PROCESSING
                #=======================================================

                melody_chords2 = []

                # Break between compositions / Intro seq

                if 9 in instruments_list:
                  drums_present = 1666 # Yes
                else:
                  drums_present = 1665 # No

                if melody_chords[0][2] != 9:
                    pat = melody_chords[0][5]
                else:
                    pat = 128

                melody_chords2.extend([1795, drums_present, 1667+pat]) # Intro seq

                #=======================================================

                # TOTAL DICTIONARY SIZE 1795+1=1796

                #=======================================================
                # MAIN PROCESSING CYCLE
                #=======================================================

                chords_counter = 1

                comp_chords_len = len([y for y in melody_chords if y[0] != 0])

                if melody_chords[0][0] == 0: # Zero time token if start time is zero
                    melody_chords2.extend([0])

                pvs = [0] * 129 # Previous velocities by composition patches

                for m in melody_chords:

                    if (comp_chords_len - chords_counter) == 50:
                        melody_chords2.extend([1664]) # Outro token seq

                    if chords_counter % 50 == 0:
                        nct = 1152+min(511, ((chords_counter // 50)-1)) # chords counter token
                        melody_chords2.extend([nct])

                    if m[2] == 9: # Drums patch will be == 128
                        pat = 128
                    else:
                        pat = m[5]

                    # Pitches shifting
                    if pat < 8: # Piano pitches
                        ptc = m[3]

                    if 7 < pat < 128: # All other instruments pitches
                        ptc = m[3] + 128

                    if pat == 128: # Drums pitches
                        ptc = m[3] + 256

                    if m[0] != 0:
                        melody_chords2.extend([m[0]]) # Time tokens if time != 0
                        chords_counter += 1

                        if m[4] != pvs[pat]:
                            melody_chords2.extend([m[4]+1024]) # Velocity tokens

                        melody_chords2.extend([pat+256, m[1]+384, ptc+640]) # Main tokens triplet (Patch - Dur - Pitch)

                    else:

                        if m[4] != pvs[pat]:
                            melody_chords2.extend([m[4]+1024]) # Velocity tokens

                        melody_chords2.extend([pat+256, m[1]+384, ptc+640]) # Main tokens triplet (Patch - Dur - Pitch)

                    pvs[pat] = m[4] # Recording velocity of the current note by its patch

                    stats[pat] += 1 # Patches stats

                melody_chords2.extend([1795]) # EOS

                melody_chords_f.append(melody_chords2)

                #=======================================================

                # Processed files counter
                files_count += 1

                # Saving every 5000 processed files
                if files_count % 2500 == 0:
                  print('SAVING !!!')
                  print('=' * 70)
                  print('Saving processed files...')
                  print('=' * 70)
                  print('Data check:', min(melody_chords_f[0]), '===', max(melody_chords_f[0]), '===', len(list(set(melody_chords_f[0]))), '===', len(melody_chords_f[0]))
                  print('=' * 70)
                  print('Processed so far:', files_count, 'out of', input_files_count, '===', files_count / input_files_count, 'good files ratio')
                  print('=' * 70)
                  count = str(files_count)
                  TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/drive/MyDrive/LAKH_INTs_'+count)
                  melody_chords_f = []
                  print('=' * 70)

    except KeyboardInterrupt:
        print('Saving current progress and quitting...')
        break

    except Exception as ex:
        print('WARNING !!!')
        print('=' * 70)
        print('Bad MIDI:', f)
        print('Error detected:', ex)
        print('=' * 70)
        continue

# Saving last processed files...
print('=' * 70)
print('Saving processed files...')
print('=' * 70)
print('Data check:', min(melody_chords_f[0]), '===', max(melody_chords_f[0]), '===', len(list(set(melody_chords_f[0]))), '===', len(melody_chords_f[0]))
print('=' * 70)
print('Processed so far:', files_count, 'out of', input_files_count, '===', files_count / input_files_count, 'good files ratio')
print('=' * 70)
count = str(files_count)
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/drive/MyDrive/LAKH_INTs_'+count)

# Displaying resulting processing stats...
print('=' * 70)
print('Done!')
print('=' * 70)

print('Resulting Stats:')
print('=' * 70)
print('Total good processed MIDI files:', files_count)
print('=' * 70)

print('Instruments stats:')
print('=' * 70)
print('Piano:', stats[0])
print('Drums:', stats[128])
print('=' * 70)

"""# (TEST INTS)"""

#@title Test INTs

train_data1 = random.choice(melody_chords_f)

print('Sample INTs', train_data1[:15])

out = train_data1[:200000]

if len(out) != 0:

    song = out
    song_f = []

    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    patches = [0] * 16

    channels = [0] * 16
    channels[9] = 1

    velocities = [90] * 129

    for ss in song:

        if 0 <= ss < 256:

            time += (ss * 8)

        if 1024 <= ss < 1152:

            vel = (ss-1024)

        if 256 <= ss <= 384:
            patch = (ss-256)

            if patch < 128:

                if patch not in patches:
                  cha = channels.index(0)
                  channels[cha] = 1

                  patches[cha] = patch
                  channel = patches.index(patch)
                else:
                  channel = patches.index(patch)

            if patch == 128:
                channel = 9

        if 384 <= ss < 640:

            dur = ((ss-384) * 16)

        if 640 <= ss < 1024:

            pitch = (ss-640) % 128

            if vel != 0:
                velocities[patch] = vel
                vel = 0

            velocity = velocities[patch]

            song_f.append(['note', time, dur, channel, pitch, velocity ])

detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'Allegro X Music Transformer',
                                                        output_file_name = '/content/Allegro-X-Music-Composition',
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=patches
                                                        )

print('Done!')

"""# Congrats! You did it! :)"""