#!/bin/bash

pip install https://github.com/VOICEVOX/voicevox_core/releases/download/0.16.0/voicevox_core-0.16.0-cp310-abi3-manylinux_2_34_x86_64.whl

binary=download-linux-x64
curl -sSfL https://github.com/VOICEVOX/voicevox_core/releases/latest/download/${binary} -o download
chmod +x download
./download -o ./src/voicevox/python --exclude c-api

pip install -r requirements.txt