import re
import json
import requests
import subprocess
from bs4 import BeautifulSoup
from pypdf import PdfReader
from gtts import gTTS
from urllib.parse import urlparse, parse_qs
from urllib.request import urlretrieve
from unidecode import unidecode

# '1. hello2. world' => True
# '3. hi' => False
def is_multiple_line(line):
    for word in line.split(' '):
        if word[0].isalpha() and word[-1] == '.':
            return True
    return False

# '1. hello2. world' => ['hello', 'world']
# '3. something4. else5. right' => ['something', 'else']
# '6. bruh' => ['bruh']
def remove_numbers_and_split(line):
    line = re.sub(r'\d+\. ', '\n', line)
    return line.split('\n')[1:]

def get_word_list(filename):
    reader = PdfReader(filename)
    words = []
    for i, page in enumerate(reader.pages):
        lines = page.extract_text(extraction_mode='plain').split('\n')
        if i == 0:
            # First page has 2 non-word lines at start
            # Other pages have 1 non-word line at start
            lines = lines[2:]
        else:
            lines = lines[1:]
        
        for line in lines:
            words += remove_numbers_and_split(line)

    # ' thing ' => 'thing'
    for i in range(len(words)):
        words[i] = re.sub(r'^\s*', '', words[i])
        words[i] = re.sub(r'\s*$', '', words[i])
        words[i] = words[i].replace('’', '\'')

    return words

def save_word_from_mw(soup, save_path):
    # word = word.replace(' ', '%20')
    # html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').text
    # soup = BeautifulSoup(html, features='lxml')
    href = soup.find_all('a', class_='play-pron-v2')[0]['href']
    params = parse_qs(urlparse(href).query)
    sound_url = f'https://media.merriam-webster.com/audio/prons/en/us/mp3/{params['dir'][0]}/{params['file'][0]}.mp3'
    urlretrieve(sound_url, save_path)

def get_definitions(soup):
    defs = []
    for dt_text in soup.find_all('span', class_='dtText'):
        defs += list(filter(lambda x: x.name is None, dt_text.children))
    for i in range(len(defs)):
        defs[i] = re.sub(r'^\s*', '', defs[i])
        defs[i] = re.sub(r'\s*$', '', defs[i])
    return defs

words = get_word_list('spell.pdf')

# print(words[321])
# word = words[321].replace(' ', '%20')
# html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').text
# soup = BeautifulSoup(html, features='lxml')
# print(get_definitions(soup))

# for w in get_word_list('spell.pdf'):
#     print(w)

# for i, word in enumerate(words):
#     gTTS(word).save(f'data/pronunciations/{i+1}.mp3')
#     print(i)

with open('times', 'r') as f:
    times = f.readlines()

times = list(map(lambda x: float(x), times))

data = []
prev = 0
for i, word in enumerate(words):
    data.append({
        'audio': f'data/pronunciations/{i+1}.mp3',
        'word': unidecode(word), # to remove accents from the word
        'start': prev,
        'end': times[i]
    })
    prev = times[i]

with open('data/data.json', 'wb') as f:
    f.write(json.dumps(data).encode('utf-8'))
