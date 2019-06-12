import json
import os

from Downloader import Downloader


def update_all_mangas():
    if not os.path.isfile('list_manga.json'):
        raise FileNotFoundError('list_manga.json is required')

    with open('list_manga.json', 'r') as f:
        manga_categories = json.load(f)
    for category in manga_categories:
        category_name = category['name']
        category_main_dir = category['main_dir']
        mangas = category['manga']

        if not os.path.exists(category_main_dir):
            print('Skip category : {}'.format(category_name))
            continue

        print("CHECK {}".format(category_name))

        dl = Downloader()
        dl.set_main_dir(category_main_dir)
        for manga in mangas:
            manga_name = manga['name']
            manga_link = manga['link']

            dl.set_manga_name(manga_name, False)
            dl.set_manga_page_link(manga_link)

            if not os.path.exists(dl.manga_dir) or len(os.listdir(dl.manga_dir)) == 0:
                print("\tSKIP {}, because not downloaded yet".format(manga_name))
                continue

            try:
                with open(dl.manga_dir + "chapters.json", 'r') as f:
                    chapter_before = json.load(f)

                dl.get_links_from_manga_page()

                with open(dl.manga_dir + "chapters.json", 'r') as f:
                    chapter_after = json.load(f)
            except Exception:
                continue

            if len(chapter_before) != len(chapter_after):
                print('\tUPDATE NEEDED!! {}'.format(manga_name))
                new_chapter = len(chapter_before) - len(chapter_after)
                if new_chapter == 1:
                    print('\tThere is NEW a chapter')
                else:
                    print('\tThere is NEW {} chapters'.format(new_chapter))

                dl.craw()
                dl.create_sectioned_chapter()
                dl.done()
            else:
                print('\tThere is NO update in {}'.format(manga_name))


update_all_mangas()
