# Manga Downloader V2
- Written with Python programming language
- Reliable
- Support multi manga provider
# Required & libraries
- Python 3.x
- request - ```pip install requests```
- bs4 - ```pip install bs4```
- img2pdf - ```pip install img2pdf```
- PyPDF2 - ```pip install PyPDF2```
- PIL - ```pip install pillow```
- tqdm - ```pip install tqdm```
# How to use
- Define list of manga in ```list_manga.json``` within format as bellow
```json
[
  {
    "name" : "Category of manga 1",
    "main_dir": "D:/Manga/Category of manga 1/",
    "manga": [
      {
        "name": "Manga 1",
        "link": "https://komikcast.com/komik/manga-1/"
      },
      {
        "name": "Manga 2",
        "link": "https://komikcast.com/komik/manga-2/"
      }
    ]
  },
  {
    "name" : "Category of manga 2",
    "main_dir": "D:/Manga/Category of manga 2/",
    "manga": [
      {
        "name": "Manga 3",
        "link": "https://komikcast.com/komik/manga-3/"
      },
      {
        "name": "Manga 4",
        "link": "https://www.komikone.com/manga/manga-4/"
      }
    ]
  }
]
```
Note : always end directory with slash (/) in json file
 - Run ```MangaDownloader.py``` file
 # Supported website
- https://www.komikcast.com/
- https://www.komikgue.com/
- https://www.komikone.com/
- https://www.mangazuki.com/

```
                                Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```