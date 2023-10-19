# -*- coding: utf-8 -*-
"""Allegro_X_Music_Transformer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1brBESJGILa706SlNyJy3RjB3rvb25bdt

# Allegro X Music Transformer (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2023

***

# (GPU CHECK)
"""

#@title NVIDIA GPU check
!nvidia-smi

"""# (SETUP ENVIRONMENT)"""

#@title Install dependencies
!git clone --depth 1 https://github.com/asigalov61/Allegro-X-Music-Transformer
!pip install huggingface_hub
!pip install torch
!pip install einops
!pip install torch-summary
!pip install tqdm
!pip install matplotlib
!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio

# Commented out IPython magic to ensure Python compatibility.
#@title Import modules

print('=' * 70)
print('Loading core Allegro X Music Transformer modules...')

import os
import pickle
import random
import secrets
import statistics
from time import time
import tqdm

print('=' * 70)
print('Loading main Allegro X Music Transformer modules...')
import torch

# %cd /content/Allegro-X-Music-Transformer

import TMIDIX
from x_transformer_1_23_2 import *

# %cd /content/
print('=' * 70)
print('Loading aux Allegro X Music Transformer modules...')

import matplotlib.pyplot as plt

from torchsummary import summary
from sklearn import metrics

from midi2audio import FluidSynth
from IPython.display import Audio, display

from huggingface_hub import hf_hub_download

from google.colab import files

print('=' * 70)
print('Done!')
print('Enjoy! :)')
print('=' * 70)

"""# (LOAD MODEL)

# Choose one and do not forget to restart colab runtime if switching between models
"""

#@title Load Allegro X Music Transformer Small Model (BEST)

#@markdown Very fast model, 32 layers, 245k MIDIs training corpus

full_path_to_model_checkpoint = "/content/Allegro-X-Music-Transformer/Models/Large/Allegro_X_Music_Transformer_Large_Trained_Model_35308_steps_0.5872_loss_0.8248_acc.pth" #@param {type:"string"}

#@markdown Model precision option

model_precision = "bfloat16" # @param ["bfloat16", "float16", "float32"]

#@markdown bfloat16 == Third precision/triple speed (if supported, otherwise the model will default to float16)

#@markdown float16 == Half precision/double speed

#@markdown float32 == Full precision/normal speed

plot_tokens_embeddings = True # @param {type:"boolean"}

print('=' * 70)
print('Loading Allegro X Music Transformer Small Pre-Trained Model...')
print('Please wait...')
print('=' * 70)

if os.path.isfile(full_path_to_model_checkpoint):
  print('Model already exists...')

else:
  hf_hub_download(repo_id='asigalov61/Allegro-X-Music-Transformer',
                  filename='Allegro_X_Music_Transformer_Large_Trained_Model_35308_steps_0.5872_loss_0.8248_acc.pth',
                  local_dir='/content/Allegro-X-Music-Transformer/Models/Large/',
                  local_dir_use_symlinks=False)
print('=' * 70)
print('Instantiating model...')

torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda'

if model_precision == 'bfloat16' and torch.cuda.is_bf16_supported():
  dtype = 'bfloat16'
else:
  dtype = 'float16'

if model_precision == 'float16':
  dtype = 'float16'

if model_precision == 'float32':
  dtype = 'float32'

ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = torch.amp.autocast(device_type=device_type, dtype=ptdtype)

SEQ_LEN = 8192

# instantiate the model

model = TransformerWrapper(
    num_tokens = 1093,
    max_seq_len = SEQ_LEN,
    attn_layers = Decoder(dim = 1024, depth = 32, heads = 32, attn_flash=True)
)
model = AutoregressiveWrapper(model, ignore_index=1092)

model.cuda()
print('=' * 70)

print('Loading model checkpoint...')

model.load_state_dict(torch.load(full_path_to_model_checkpoint))
print('=' * 70)

model.eval()

print('Done!')
print('=' * 70)

print('Model will use', dtype, 'precision...')
print('=' * 70)

# Model stats
print('Model summary...')
summary(model)

# Plot Token Embeddings

if plot_tokens_embeddings:

  tok_emb = model.net.token_emb.emb.weight.detach().cpu().tolist()

  cos_sim = metrics.pairwise_distances(
    tok_emb, metric='cosine'
  )
  plt.figure(figsize=(7, 7))
  plt.imshow(cos_sim, cmap="inferno", interpolation="nearest")
  im_ratio = cos_sim.shape[0] / cos_sim.shape[1]
  plt.colorbar(fraction=0.046 * im_ratio, pad=0.04)
  plt.xlabel("Position")
  plt.ylabel("Position")
  plt.tight_layout()
  plt.plot()
  plt.savefig("/content/Allegro-X-Music-Transformer-Small-Tokens-Embeddings-Plot.png", bbox_inches="tight")

"""# (GENERATE)

# (IMPROV)
"""

#@title Standard Improv Generator

#@markdown Improv settings
improv_type = "Freestyle" # @param ["Freestyle", "Custom"]

#@markdown Custom Improv Settings

first_note_MIDI_patch_number = 0 # @param {type:"slider", min:0, max:128, step:1}
add_drums = False #@param {type:"boolean"}

#@markdown Generation settings

number_of_tokens_tp_generate = 510 # @param {type:"slider", min:30, max:2048, step:3}
number_of_batches_to_generate = 4 #@param {type:"slider", min:1, max:16, step:1}
temperature = 0.9 #@param {type:"slider", min:0.1, max:1, step:0.1}

#@markdown Other settings

render_MIDI_to_audio = True # @param {type:"boolean"}

print('=' * 70)
print('Allegro X Music Transformer Standard Improv Model Generator')
print('=' * 70)

if add_drums:
  drumsp = 961 # Yes
else:
  drumsp = 960 # No

if improv_type == 'Freestyle':
  outy = [1091]

else:
  outy = [1091, drumsp, 962+first_note_MIDI_patch_number]

print('Selected Improv sequence:')
print(outy)
print('=' * 70)

inp = [outy] * number_of_batches_to_generate

inp = torch.LongTensor(inp).cuda()

with ctx:
  out = model.generate(inp,
                      number_of_tokens_tp_generate,
                      temperature=temperature,
                      return_prime=True,
                      verbose=True)

out0 = out.tolist()

print('=' * 70)
print('Done!')
print('=' * 70)

#======================================================================

print('Rendering results...')

for i in range(number_of_batches_to_generate):

  print('=' * 70)
  print('Batch #', i)
  print('=' * 70)

  out1 = out0[i]

  print('Sample INTs', out1[:12])
  print('=' * 70)

  if len(out1) != 0:

      song = out1
      song_f = []

      time = 0
      dur = 0
      vel = 90
      pitch = 0
      channel = 0

      patches = [-1] * 16

      channels = [0] * 16
      channels[9] = 1

      velocities = [90] * 129

      for ss in song:

          if 0 <= ss < 64:

              time += (ss * 32)

          if 64 <= ss <= 192:
              patch = (ss-64)

              if patch < 128:

                  if patch not in patches:
                    if 0 in channels:
                      cha = channels.index(0)
                      channels[cha] = 1
                    else:
                      cha = 15

                    patches[cha] = patch
                    channel = patches.index(patch)
                  else:
                    channel = patches.index(patch)

              if patch == 128:
                  channel = 9

          if 640 <= ss < 704:

              vel = ((ss-640) * 2)

          if 192 <= ss < 256:

              dur = ((ss-192) * 64)

          if 256 <= ss < 640:

              pitch = (ss-256) % 128

              if vel != 0:
                  velocities[patch] = vel
                  vel = 0

              velocity = velocities[patch]

              song_f.append(['note', time, dur, channel, pitch, velocity ])

      patches = [0 if x==-1 else x for x in patches]

      detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                                output_signature = 'Allegro X Music Transformer',
                                                                output_file_name = '/content/Allegro-X-Music-Transformer-Composition_'+str(i),
                                                                track_name='Project Los Angeles',
                                                                list_of_MIDI_patches=patches
                                                                )


      print('=' * 70)
      print('Displaying resulting composition...')
      print('=' * 70)

      fname = '/content/Allegro-X-Music-Transformer-Composition_'+str(i)

      x = []
      y =[]
      c = []

      colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver', 'lightgreen', 'indigo', 'maroon', 'turquoise']

      for s in song_f:
        x.append(s[1] / 1000)
        y.append(s[4])
        c.append(colors[s[3]])

      if render_MIDI_to_audio:
        FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
        display(Audio(str(fname + '.wav'), rate=16000))

      plt.figure(figsize=(14,5))
      ax=plt.axes(title=fname)
      ax.set_facecolor('black')

      plt.scatter(x,y, c=c)
      plt.xlabel("Time")
      plt.ylabel("Pitch")
      plt.show()

"""# (CUSTOM MIDI)"""

#@title Load Seed MIDI

#@markdown Press play button to to upload your own seed MIDI or to load one of the provided sample seed MIDIs from the dropdown list below

select_seed_MIDI = "Upload your own custom MIDI" #@param ["Upload your own custom MIDI", "Allegro-X-Music-Transformer-Piano-Seed-1", "Allegro-X-Music-Transformer-Piano-Seed-2", "Allegro-X-Music-Transformer-Piano-Seed-3", "Allegro-X-Music-Transformer-Piano-Seed-4", "Allegro-X-Music-Transformer-Piano-Seed-5", "Allegro-X-Music-Transformer-MI-Seed-1", "Allegro-X-Music-Transformer-MI-Seed-2", "Allegro-X-Music-Transformer-MI-Seed-3", "Allegro-X-Music-Transformer-MI-Seed-4", "Allegro-X-Music-Transformer-MI-Seed-5"]
render_MIDI_to_audio = False # @param {type:"boolean"}

print('=' * 70)
print('Allegro X Music Transformer Seed MIDI Loader')
print('=' * 70)

f = ''

if select_seed_MIDI != "Upload your own custom MIDI":
  print('Loading seed MIDI...')
  f = '/content/Allegro-X-Music-Transformer/Seeds/'+select_seed_MIDI+'.mid'
  score = TMIDIX.midi2single_track_ms_score(open(f, 'rb').read(), recalculate_channels=False)

else:
  print('Upload your own custom MIDI...')
  print('=' * 70)
  uploaded_MIDI = files.upload()
  if list(uploaded_MIDI.keys()):
    score = TMIDIX.midi2single_track_ms_score(list(uploaded_MIDI.values())[0], recalculate_channels=False)
    f = list(uploaded_MIDI.keys())[0]

if f != '':

  print('=' * 70)
  print('File:', f)
  print('=' * 70)

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
            e[1] = int(e[1] / 32) # Max 2 seconds for start-times
            e[2] = int(e[2] / 64) # Max 4 seconds for durations

        # Sorting by patch, pitch, and by start-time
        events_matrix1.sort(key=lambda x: x[6])
        events_matrix1.sort(key=lambda x: x[4])
        events_matrix1.sort(key=lambda x: x[1])

        #=======================================================
        # FINAL PRE-PROCESSING

        melody_chords = []

        pe = events_matrix1[0]

        for e in events_matrix1:

            # Cliping all values...
            time = max(0, min(63, e[1]-pe[1]))
            dur = max(1, min(63, e[2]))
            cha = max(0, min(15, e[3]))
            ptc = max(1, min(127, e[4]))

            # Calculating octo-velocity
            vel = max(1, min(63, int(e[5] / 2)))

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
          drums_present = 961 # Yes
        else:
          drums_present = 960 # No

        if melody_chords[0][2] != 9:
            pat = melody_chords[0][5]
        else:
            pat = 128

        melody_chords2.extend([1091, drums_present, 962+pat]) # Intro seq

        #=======================================================

        # TOTAL DICTIONARY SIZE 1091+1=1092

        #=======================================================
        # MAIN PROCESSING CYCLE
        #=======================================================

        chords_counter = 1

        comp_chords_len = len([y for y in melody_chords if y[0] != 0])

        if melody_chords[0][0] == 0: # Zero time token if start time is zero
            melody_chords2.extend([0])

        pvs = [0] * 129 # Previous velocities by composition patches

        ppat = -1 # Previous note patch

        for m in melody_chords:

            # if ((comp_chords_len - chords_counter) == 50) and (m[0] != 0):
            #    melody_chords2.extend([959]) # Outro token

            if chords_counter % 50 == 0 and m[0] != 0:
                nct = 704+min(255, ((chords_counter // 50)-1)) # Chords counter token
                melody_chords2.extend([nct])
                chords_counter += 1
            else:
                if m[0] != 0:
                    chords_counter += 1

            # Drums patch
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

                if pat != ppat: # Patch tokens
                    melody_chords2.extend([pat+64])

                if m[4] != pvs[pat]:
                    melody_chords2.extend([m[4]+640]) # Velocity tokens

                melody_chords2.extend([m[1]+192, ptc+256]) # Main tokens tuplets (Dur - Pitch)

            else:

                if pat != ppat: # Patch tokens
                    melody_chords2.extend([pat+64])

                if m[4] != pvs[pat]:
                    melody_chords2.extend([m[4]+640]) # Velocity tokens

                melody_chords2.extend([m[1]+192, ptc+256]) # Main tokens tuplets (Dur - Pitch)

            pvs[pat] = m[4] # Recording velocity of the current note by its patch

            ppat = pat # Previous note patch

        melody_chords2.extend([1091]) # EOS

  #=======================================================

  song = melody_chords2

  song_f = []

  time = 0
  dur = 0
  vel = 90
  pitch = 0
  channel = 0

  patches = [-1] * 16

  channels = [0] * 16
  channels[9] = 1

  velocities = [90] * 129

  for ss in song:

      if 0 <= ss < 64:

          time += (ss * 32)

      if 64 <= ss <= 192:
          patch = (ss-64)

          if patch < 128:

              if patch not in patches:
                if 0 in channels:
                  cha = channels.index(0)
                  channels[cha] = 1
                else:
                  cha = 15

                patches[cha] = patch
                channel = patches.index(patch)
              else:
                channel = patches.index(patch)

          if patch == 128:
              channel = 9

      if 640 <= ss < 704:

          vel = ((ss-640) * 2)

      if 192 <= ss < 256:

          dur = ((ss-192) * 64)

      if 256 <= ss < 640:

          pitch = (ss-256) % 128

          if vel != 0:
              velocities[patch] = vel
              vel = 0

          velocity = velocities[patch]

          song_f.append(['note', time, dur, channel, pitch, velocity ])

  patches = [0 if x==-1 else x for x in patches]

  detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                            output_signature = 'Allegro X Music Transformer',
                                                            output_file_name = '/content/Allegro-X-Music-Transformer-Seed-Composition',
                                                            track_name='Project Los Angeles',
                                                            list_of_MIDI_patches=patches
                                                            )

  #=======================================================

  print('=' * 70)
  print('Composition stats:')
  print('Composition has', chords_counter, 'chords')
  print('Composition has', len(melody_chords2), 'tokens')
  print('=' * 70)

  fname = '/content/Allegro-X-Music-Transformer-Seed-Composition'

  x = []
  y =[]
  c = []

  colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver', 'red', 'yellow', 'green', 'cyan']

  for s in song_f:
    x.append(s[1] / 1000)
    y.append(s[4])
    c.append(colors[s[3]])

  if render_MIDI_to_audio:
    FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
    display(Audio(str(fname + '.wav'), rate=16000))

  plt.figure(figsize=(14,5))
  ax=plt.axes(title=fname)
  ax.set_facecolor('black')

  plt.scatter(x,y, c=c)
  plt.xlabel("Time")
  plt.ylabel("Pitch")
  plt.show()

else:
  print('=' * 70)

"""# (CONTINUATION)"""

#@title Standard Continuation Generator

#@markdown Generation settings

try_to_generate_outro = False #@param {type:"boolean"}
number_of_prime_tokens = 8190 # @param {type:"slider", min:4, max:8192, step:4}
number_of_tokens_to_generate = 510 #@param {type:"slider", min:30, max:2046, step:30}
number_of_batches_to_generate = 4 #@param {type:"slider", min:1, max:16, step:1}
temperature = 0.9 #@param {type:"slider", min:0.1, max:1, step:0.1}

#@markdown Other settings

include_prime_tokens_in_generated_output = True #@param {type:"boolean"}
allow_model_to_stop_generation_if_needed = False #@param {type:"boolean"}
render_MIDI_to_audio = True # @param {type:"boolean"}

print('=' * 70)
print('Allegro X Music Transformer Standard Continuation Model Generator')
print('=' * 70)

if allow_model_to_stop_generation_if_needed:
  min_stop_token = 1091
else:
  min_stop_token = None

outy = melody_chords2[:number_of_prime_tokens]

if try_to_generate_outro:
  outy.extend([959])

inp = [outy] * number_of_batches_to_generate

inp = torch.LongTensor(inp).cuda()

with ctx:
  out = model.generate(inp,
                      number_of_tokens_to_generate,
                      temperature=temperature,
                      return_prime=include_prime_tokens_in_generated_output,
                      eos_token=min_stop_token,
                      verbose=True,
                      )

out0 = out.tolist()

print('=' * 70)
print('Done!')
print('=' * 70)

#======================================================================
print('Rendering results...')

for i in range(number_of_batches_to_generate):

  print('=' * 70)
  print('Batch #', i)
  print('=' * 70)

  out1 = out0[i]

  print('Sample INTs', out1[:12])
  print('=' * 70)

  if len(out) != 0:

      song = out1
      song_f = []

      time = 0
      dur = 0
      vel = 90
      pitch = 0
      channel = 0

      patches = [-1] * 16

      channels = [0] * 16
      channels[9] = 1

      velocities = [90] * 129

      for ss in song:

          if 0 <= ss < 64:

              time += (ss * 32)

          if 64 <= ss <= 192:
              patch = (ss-64)

              if patch < 128:

                  if patch not in patches:
                    if 0 in channels:
                      cha = channels.index(0)
                      channels[cha] = 1
                    else:
                      cha = 15

                    patches[cha] = patch
                    channel = patches.index(patch)
                  else:
                    channel = patches.index(patch)

              if patch == 128:
                  channel = 9

          if 640 <= ss < 704:

              vel = ((ss-640) * 2)

          if 192 <= ss < 256:

              dur = ((ss-192) * 64)

          if 256 <= ss < 640:

              pitch = (ss-256) % 128

              if vel != 0:
                  velocities[patch] = vel
                  vel = 0

              velocity = velocities[patch]

              song_f.append(['note', time, dur, channel, pitch, velocity ])

      patches = [0 if x==-1 else x for x in patches]

      detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                                output_signature = 'Allegro X Music Transformer',
                                                                output_file_name = '/content/Allegro-X-Music-Transformer-Composition_'+str(i),
                                                                track_name='Project Los Angeles',
                                                                list_of_MIDI_patches=patches
                                                                )
      print('=' * 70)
      print('Displaying resulting composition...')
      print('=' * 70)

      fname = '/content/Allegro-X-Music-Transformer-Composition_'+str(i)

      x = []
      y =[]
      c = []

      colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver', 'lightgreen', 'indigo', 'maroon', 'turquoise']

      for s in song_f:
        x.append(s[1] / 1000)
        y.append(s[4])
        c.append(colors[s[3]])

      if render_MIDI_to_audio:
        FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
        display(Audio(str(fname + '.wav'), rate=16000))

      plt.figure(figsize=(14,5))
      ax=plt.axes(title=fname)
      ax.set_facecolor('black')

      plt.scatter(x,y, c=c)
      plt.xlabel("Time")
      plt.ylabel("Pitch")
      plt.show()

"""# Congrats! You did it! :)"""