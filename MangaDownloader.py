import json

from Downloader import Downloader

list_manga = json.load(open("list_manga.json", 'r'))

for index, manga in enumerate(list_manga):
    print("{}\t{}".format(index + 1, manga['name']))
try:
    manga_type_code = int(input("\033[1mChoose Manga Category : \033[0m"))
    manga_type_code = manga_type_code - 1
    manga_type = list_manga[manga_type_code]
    for index, manga in enumerate(manga_type['manga']):
        print("{}\t{}".format(index + 1, manga['name']))

    manga_code = int(input("\033[1mChoose Manga : \033[0m"))
    manga_code = manga_code - 1
    manga = manga_type['manga'][manga_code]

    downloader = Downloader(manga_type['main_dir'])
    downloader.set_manga_name(manga['name'])
    downloader.set_manga_page_link(manga['link'])

    print("Downloading... Download {} links".format(manga['name']))
    downloader.get_links_from_manga_page()
    print("Done")
    downloader.craw()
    downloader.create_sectioned_chapter()
    downloader.done()
except:
    exit()
