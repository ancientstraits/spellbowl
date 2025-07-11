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
    play_inst = soup.find_all('a', class_='play-pron-v2')
    if len(play_inst) == 0:
        print('Could not find audio file for word')
        return
    href = play_inst[0]['href']
    params = parse_qs(urlparse(href).query)
    # sound_dir = params['dir'][0]
    # sound_file = params['file'][0]
    sound_url = f'https://media.merriam-webster.com/audio/prons/en/us/mp3/{params['dir'][0]}/{params['file'][0]}.mp3'
    urlretrieve(sound_url, save_path)

def get_definitions(word):
    word = word.replace(' ', '%20')

    dapi_resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

    if dapi_resp.status_code == 404 or dapi_resp.status_code == 429:
        print('word not found with dictionaryapi.dev, using Merriam-Webster')
        html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').text
        soup = BeautifulSoup(html, features='html.parser')
        return get_mw_definitions(soup)
    else:
        print(dapi_resp)
        dapi_json = json.loads(dapi_resp.text)
        defs = []
        for meaning in dapi_json[0]['meanings']:
            for definition in meaning['definitions']:
                defs.append(definition['definition'])
        return defs


def get_mw_definitions(soup):
    defs = []
    for dt_text in soup.find_all('span', class_='dtText'):
        # ':2' is because each span has a ': ' at the start
        defs.append(dt_text.text[2:])

    if len(defs) == 0:
        for un_text in soup.find_all('span', class_='unText'):
            defs.append(un_text.text[2:])    

    for i in range(len(defs)):
        defs[i] = re.sub(r'^\s*', '', defs[i])
        defs[i] = re.sub(r'\s*$', '', defs[i])
        defs[i] = defs[i].replace(' : ', '; ')

    return defs

words = get_word_list('spell.pdf')

# print(words[321])
# word = words[321].replace(' ', '%20')
# for i, word in enumerate(words):
#     print(i+1)
#     word = word.replace(' ', '%20')
#     print(word)
#     html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').text
#     soup = BeautifulSoup(html, features='html.parser')
#     save_word_from_mw(soup, f'data/mw-pronunciations/{i+1}.mp3')
# defs = []
# for i, word in enumerate(words):
#     print(i+1)
#     word = word.replace(' ', '%20')
#     print(word)
#     # html = requests.get(f'https://www.merriam-webster.com/dictionary/{word}').text
#     # soup = BeautifulSoup(html, features='html.parser')

#     # d = get_mw_definitions(soup)
#     d = get_definitions(word)
#     if len(d) == 0:
#         print('Could not get definition')
#         defs.append(None)
#     else:
#         defs.append(d)
#         # gTTS(d[0]).save(f'data/definitions/{i+1}.mp3')
#         print('\t' + d[0])
#     print('\n\n')

# print(get_definitions(soup))

# for w in get_word_list('spell.pdf'):
#     print(w)

for i, word in enumerate(words):
    gTTS(word, lang="en-us").save(f'data/pronunciations/{i+1}.mp3')
    print(i)

# with open('times', 'r') as f:
#     times = f.readlines()

# times = list(map(lambda x: float(x), times))

# data = []
# prev = 0
# for i, word in enumerate(words):
#     data.append({
#         'audio': f'data/pronunciations/{i+1}.mp3',
#         'defAudio': f'data/defintions/{i+1}.mp3',
#         'word': unidecode(word), # to remove accents from the word
#         # 'start': prev,
#         # 'end': times[i],
#         'definitions': defs[i]
#     })
#     # prev = times[i]

# with open('data/data.json', 'wb') as f:
#     f.write(json.dumps(data).encode('utf-8'))
