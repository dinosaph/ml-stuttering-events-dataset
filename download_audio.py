#
# For licensing see accompanying LICENSE file.
# Copyright (C) 2021 Apple Inc. All Rights Reserved.
#

"""
For each podcast episode:
* Download the raw mp3/m4a file
* Convert it to a 16k mono wav file
# Remove the original file
"""

import os
import pathlib
import subprocess

import numpy as np

import argparse

parser = argparse.ArgumentParser(description='Download raw audio files for SEP-28k or FluencyBank and convert to 16k hz mono wavs.')
parser.add_argument('--episodes', type=str, required=True,
                   help='Path to the labels csv files (e.g., SEP-28k_episodes.csv)')
parser.add_argument('--wavs', type=str, default="wavs",
                   help='Path where audio files from download_audio.py are saved')


args = parser.parse_args()
episode_uri = args.episodes
wav_dir = args.wavs

# Load episode data
table = np.loadtxt(episode_uri, dtype=str, delimiter=",")
table = np.char.lstrip(table)
urls = table[:,2]
n_items = len(urls)

audio_types = [".mp3", ".m4a", ".mp4"]

def download_audio(url, out_path):
    try:
        subprocess.run(['wget', '-O', out_path, url], check=True)
        print("Download completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

for i in range(n_items):
	# Get show/episode IDs
	show_abrev = table[i,-2]
	ep_idx = table[i,-1]
	episode_url = table[i,2]

	# Check file extension
	ext = ''
	for ext in audio_types:
		if ext in episode_url:
			break

	# Ensure the base folder exists for this episode
	episode_dir = pathlib.Path(f"{wav_dir}/{show_abrev}/")
	os.makedirs(episode_dir, exist_ok=True)

	# Get file paths
	audio_path_orig = pathlib.Path(f"{episode_dir}/{ep_idx}{ext}")
	wav_path = pathlib.Path(f"{episode_dir}/{ep_idx}.wav")

	# Check if this file has already been downloaded
	if os.path.exists(wav_path):
		continue

	print("Processing", show_abrev, ep_idx)
	# Download raw audio file. This could be parallelized.
	if not os.path.exists(audio_path_orig):
		download_audio(url=episode_url, out_path=audio_path_orig)

	# Convert to 16khz mono wav file
	command = ['ffmpeg', '-i', audio_path_orig, '-ac', '1', '-ar', '16000', wav_path]
	process = subprocess.Popen(command,shell=True)
	process.wait()

	# Remove the original mp3/m4a file
	os.remove(audio_path_orig)
