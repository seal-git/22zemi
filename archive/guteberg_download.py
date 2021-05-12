import os
import pandas as pd
import numpy as np
from tqdm import tqdm

os.system('apt install libdb5.3-dev')
os.system('pip install gutenberg')

from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers

df = pd.read_csv('gutenberg_metadata.csv')

data = {'Author': None, 'Title': None, 'Link': None, 'ID': None, 'Bookshelf': None, 'Text': None}

for key, row in tqdm(df.iterrows()):
    if data['Author'] == None:
        data['Author'] = [row['Author']]
    else:
        data['Author'].append(row['Author'])
    
    if data['Title'] == None:
        data['Title'] = [row['Title']]
    else:
        data['Title'].append(row['Title'])
    
    if data['Link'] == None:
        data['Link'] = [row['Link']]
    else:
        data['Link'].append(row['Link'])
    
    book_id = int(row['Link'].split('/')[-1])

    if data['ID'] == None:
        data['ID'] = [book_id]
    else:
        data['ID'].append(book_id)
    
    if data['Bookshelf'] == None:
        data['Bookshelf'] = [row['Bookshelf']]
    else:
        data['Bookshelf'].append(row['Bookshelf'])

    text = np.nan
    try:
        text = strip_headers(load_etext(etextno=book_id, 
                                        mirror='http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/')).strip()
        text = ' '.join(' '.join(' '.join(text.split('\n')).split('\t')).split('\r'))
    except:
        try: 
            page = requests.get(row['Link'])
            soup = BeautifulSoup(page.content, 'html.parser')
            text_link = 'http://www.gutenberg.org' + soup.find_all("a", string="Plain Text UTF-8")[0]['href']
            text = strip_headers(str(urlopen(text_link)))
            text = ' '.join(' '.join(' '.join(text.split('\n')).split('\t')).split('\r'))
        except:
            print("Couldn't acquire text for " + row['Title'] + ' with ID ' + str(book_id) + '. Link: ' + row['Link'])
    
    if data['Text'] == None:
        data['Text'] = [text]
    else:
        data['Text'].append(text)
    
df_data = pd.DataFrame(data, columns = ['Title', 'Author', 'Link', 'ID', 'Bookshelf', 'Text'])

df_data.to_csv('gutenberg_data.csv', index=False)