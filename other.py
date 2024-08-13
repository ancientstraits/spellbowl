import json
from pathlib import Path

with open('data/data.json', 'rb') as f:
    data = json.loads(f.read().decode('utf-8'))

for i in range(len(data)):
    mw_path = f'data/mw-pronunciations/{i+1}.mp3'
    if Path(mw_path).exists():
        data[i]['audio'] = mw_path
    else:
        data[i]['audio'] = f'data/pronunciations/{i+1}.mp3'

with open('data/data.json', 'wb') as f:
    f.write(json.dumps(data).encode('utf-8'))

