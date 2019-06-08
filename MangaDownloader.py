import json
import os
import re
import socket
from collections import OrderedDict
from functools import cmp_to_key

import PIL
import PyPDF2
import img2pdf
import requests
from PIL import Image
from bs4 import BeautifulSoup as BS
from tqdm import tqdm

regex_number = r"(\d+\.\d+)|(\d+)"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    # 'Accept-Encoding' : 'gzip, deflate, br'
}


def sort(x, y):
    x, y = str(x), str(y)
    x = re.sub(r'[^a-zA-Z0-9.,-_]', '', x)
    y = re.sub(r'[^a-zA-Z0-9.,]', '', y)
    try:
        x = float(re.search(regex_number, x).group())
        y = float(re.search(regex_number, y).group())
    except:
        return -1

    if x < y:
        return -1
    elif x > y:
        return 1
    else:
        return 0


def urlretrieve(url: str):
    try:
        url = url.strip()
        r = requests.get(url, headers=header, allow_redirects=True, timeout=20, )
        if 200 <= r.status_code < 400:
            return True, r.url, r.content
        else:
            print("\n" + url)
            print(r.status_code)
            return False, None, None
    except socket.timeout as e:
        print("Timeout download {}, Ulang lagi".format(url))
        return urlretrieve(url)
    except requests.exceptions.ReadTimeout:
        print("Timeout download {}, Ulang lagi".format(url))
        return urlretrieve(url)
    except Exception as s:
        print(s)
        print("Error download {}".format(url))
        return urlretrieve(url)


def is_image_good(file_path):
    try:
        img = Image.open(file_path, 'r')
        if img.mode == 'P' or img.mode == 'L':
            img = img.convert('RGBA')
        if img.mode == "RGBA":
            img = img.convert('RGB')
        if img.mode not in ['P', 'L', 'RGBA', 'RGB']:
            img = img.convert('RGB')
        img.save(file_path)
        return img.mode == 'RGB'
    except Exception as e:
        print(e)
        return False


def chunks(list, n):
    result = []
    for i in range(0, len(list), n):
        result.append(list[i:i + n])
    return result


class MangaDownloader:

    def __init__(self, main_dir=None, manga_name=None):
        if manga_name is not None:
            if type(manga_name) is not str:
                raise RuntimeError("manga_name harus string")

            self.__manga_name = manga_name
            self.__modul_name = manga_name.title()
            self.__modul_name = re.sub(r"\W+", '', self.__modul_name)

        self.__link = None
        self.__manga_page_link = None
        self.__main_dir = main_dir
        self.__manga_dir = None
        if main_dir is not None and not os.path.exists(main_dir):
            os.mkdir(self.__main_dir)

    def set_manga_name(self, manga_name):
        if type(manga_name) is not str:
            raise RuntimeError("manga_name harus string")
        self.__manga_name = manga_name
        self.__modul_name = manga_name.title()
        self.__modul_name = re.sub(r"\W+", '', self.__modul_name)
        self.__manga_dir = self.__main_dir + "/" + self.__manga_name + "/" if not self.__main_dir.endswith(
            '/') else self.__main_dir + self.__manga_name + "/"

    def set_manga_page_link(self, manga_page_link):
        self.__manga_page_link = manga_page_link

    def set_main_dir(self, main_dir):
        self.__main_dir = main_dir

    def get_links_from_manga_page(self):
        if not os.path.exists("Links"):
            os.mkdir("Links")

        if self.__manga_page_link is None:
            raise ValueError("panggil set_manga_page_link(manga_page_link) dulu")

        print("Downloading... Download links")
        r = requests.get(self.__manga_page_link, headers=header, timeout=10, stream=True)
        content = r.text
        print("Done")
        banner_link_image = ''
        links = {}
        if "komikcast" in self.__manga_page_link:
            span_elements = BS(content, 'html.parser').findAll('span', {'class': 'leftoff'})
            a_elements = BS(span_elements.__str__(), 'html.parser').find_all('a')
            for a in a_elements:
                links[a.text] = a.attrs['href']
            banner_link_image = BS(content, 'html.parser').find('img', {'class': 'attachment-post-thumbnail'}).attrs[
                'src']
        elif "komikgue" in self.__manga_page_link:
            a_elements = BS(content, 'html.parser').findAll('a', {'style': 'text-decoration:none;'})
            span_elements = BS(a_elements.__str__(), 'html.parser').find_all('span')
            for a, span in zip(a_elements, span_elements):
                links["Chapter {}".format(span.text)] = a.attrs['href']
            banner_link_image = \
                BS(content, 'html.parser').find('img', {'class': 'img-responsive', 'itemprop': 'image'}).attrs['src']
        elif "komikone" in self.__manga_page_link:
            span_elements = BS(content, 'html.parser').findAll('span', {'class': 'lchx'})
            a_elements = BS(span_elements.__str__(), 'html.parser').find_all('a')
            for a in a_elements:
                links[a.text] = a.attrs['href']
            banner_link_image = BS(content, 'html.parser').find('img', {'class': 'attachment-post-thumbnail'}).attrs[
                'src']
        elif "mangazuki" in self.__manga_page_link:
            li_elements = BS(content, 'html.parser').find_all('li', {'class': 'wp-manga-chapter'})
            a_elements = BS(li_elements.__str__(), 'html.parser').find_all('a')
            for a in a_elements:
                chapter_number = re.search(regex_number, a.text).group(0)
                lin = a.attrs['href']
                if "style=list" not in lin:
                    lin += "?style=list"
                links["Chapter {}".format(chapter_number)] = lin
            try:
                banner_link_image = BS(content, 'html.parser').find('div', {'class': 'summary_image'}).__str__()
                banner_link_image = BS(banner_link_image, 'html.parser').find('img')
                banner_link_image = banner_link_image.attrs['data-src']
            except:
                pass
        else:
            raise RuntimeError("Sumber manga tidak didukung")

        if banner_link_image:
            if not os.path.exists(self.__main_dir + self.__manga_name):
                os.mkdir(self.__main_dir + self.__manga_name)
            file_banner = self.__main_dir + self.__manga_name + "/1." + self.__manga_name + ".jpg"
            if not os.path.isfile(file_banner):
                result, url_image_banner, content = urlretrieve(banner_link_image)
                if result:
                    with open(file_banner, 'wb') as f:
                        f.write(content)
            # im = PIL.Image.open(file_banner+".jpg")
            # icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)]
            # im.save(file_banner+".ico", sizes=icon_sizes)

        links = sorted(links.items(), key=cmp_to_key(sort))
        self.__link = links
        with open(self.__manga_dir + "chapters.json", 'w') as f:
            json.dump(links, f, indent=4)

        # links = sorted(links.items(), key=cmp_to_key(sort))
        # self.__link = links
        # links = links.__str__()
        # links = "links = "+links
        #
        # modul_path = "Links/"+self.__modul_name+"Links.py"
        # with open(modul_path, 'w') as f:
        #     f.write(links)

    def craw(self):
        try:
            if self.__link is None:
                with open(self.__manga_dir + "chapters.json", "r") as f:
                    self.__link = json.load(f)
        except:
            raise ValueError("Tidak ada link, panggil get_links_from_manga_page() dulu")
        if self.__main_dir is None:
            raise RuntimeError("Set main_dir dulu")

        manga_folder_path = self.__main_dir + (
            "/" if not str(self.__main_dir).endswith("/") else "") + self.__manga_name + "/"
        if not os.path.exists(manga_folder_path):
            os.mkdir(manga_folder_path)
        if not os.path.exists(manga_folder_path + "Single Chapter Image/"):
            os.mkdir(manga_folder_path + "Single Chapter Image/")

        images_json = OrderedDict()
        if os.path.exists(manga_folder_path + "images.json"):
            with open(manga_folder_path + "images.json", 'r') as f:
                images_json = OrderedDict(json.load(f))

        # if len(self.__link) == len(images_json):
        #     print("Tidak ada chapter baru. Program berhenti")
        #     exit()

        print("Download %s" % self.__manga_name)
        for chapter_link in self.__link:
            chapter_name = chapter_link[0]
            link = chapter_link[1]
            chapter_folder_path = manga_folder_path + "Single Chapter Image/" + chapter_name + "/"
            if not os.path.exists(chapter_folder_path):
                os.mkdir(chapter_folder_path)

            if chapter_name not in images_json or not images_json[chapter_name]:
                r = requests.get(link, timeout=10, headers=header)
                content = r.text
                img_elements = []
                if "komikcast" in link:
                    img_elements = BS(content, 'html.parser').find_all('img', {'class': 'alignnone'})
                    if not img_elements:
                        img_elements = BS(content, 'html.parser').find_all('img')
                        img_elements = [img for img in img_elements if
                                        len(img.attrs['src']) > 10 and str(img.attrs['src']).startswith("https://")]
                elif "komikgue" in link:
                    img_elements = BS(content, 'html.parser').find_all('img', {'class': 'img-responsive'})
                elif "komikone" in link:
                    readerarea = BS(content, 'html.parser').find_all('div', {'id': 'readerarea'}).__str__()
                    # readerarea = BS(readerarea, 'html.parser').find('p').__str__()
                    img_elements = BS(readerarea, 'html.parser').find_all('img')
                    img_elements = [img_element for img_element in img_elements
                                    if (img_element.attrs['src'].strip().endswith('.jpg')
                                        or img_element.attrs['src'].strip().endswith('.png')) and
                                    len(img_element.attrs['src'].strip()) > 50]

                elif "mangazuki" in link:
                    img_elements = BS(content, 'html.parser').find_all('img', {'class': 'wp-manga-chapter-img'})
                img_elements = list(map(lambda x: x.attrs['src'], img_elements))
                images_json[chapter_name] = img_elements
            else:
                img_elements = images_json[chapter_name]

            if not img_elements:
                continue

            with open(manga_folder_path + "images.json", 'w+') as f:
                json.dump(images_json, f, indent=4, sort_keys=True)

            downloaded_images = set()
            if os.path.isfile(chapter_folder_path + "images.json"):
                with open(chapter_folder_path + "images.json", 'r') as f:
                    downloaded_images = set(json.load(f))

            for idx, img_link in tqdm(zip(range(len(img_elements)), img_elements), desc=chapter_name,
                                      total=len(img_elements)):
                file_name = str(img_link.split('/')[-1]).strip()
                file_name = re.sub(r'[^a-zA-Z0-9\\.-_]+', '', file_name)
                extension = file_name.split('.')[-1]
                if extension not in ['jpg', 'jpeg', 'png']:
                    extension = 'jpg'
                if not bool(re.search(r'\d', file_name)):
                    continue
                file_name = "{}.{}".format(idx, extension)
                if file_name not in downloaded_images:
                    result, url_result, content = urlretrieve(img_link)
                    file_name = "{}.{}".format(idx, extension)
                    full_file_path = chapter_folder_path + file_name
                    if result:
                        try:
                            if content is not None:
                                with open(full_file_path, 'wb') as f:
                                    f.write(content)
                            im = PIL.Image.open(full_file_path)
                            with open(chapter_folder_path + "images.json", "w+") as f:
                                downloaded_images.add(file_name)
                                json.dump(list(downloaded_images), f, indent=4, sort_keys=True)
                        except:
                            print("\nBermasalah : " + full_file_path)
                            os.remove(full_file_path)
                            print(full_file_path + " Deleted")
                    else:
                        print("Error ketika download gambar")

    def create_sectioned_chapter(self, chapter_per_section=50):
        print("Create sectioned chapter")
        manga_folder_path = self.__main_dir + (
            "/" if not str(self.__main_dir).endswith("/") else "") + self.__manga_name + "/"
        source_folder = manga_folder_path + "Single Chapter Image/"
        with open(manga_folder_path + "chapters.json") as f:
            json_chapter_links = json.load(f)

        available_chapter = [chapter_pair[0] for chapter_pair in json_chapter_links
                             if os.path.exists(source_folder + chapter_pair[0])]

        chapter_in_json = OrderedDict()
        if os.path.exists(manga_folder_path + "images.json"):
            with open(manga_folder_path + "images.json", 'r') as f:
                chapter_in_json = OrderedDict(json.load(f)).keys()
        chapter_in_json = sorted(chapter_in_json, key=cmp_to_key(sort))
        available_chapter_with_paths = [chapter for chapter in chapter_in_json if chapter in available_chapter]
        available_chapter_with_paths = list(map(lambda x: source_folder + x + "/", available_chapter_with_paths))
        available_chapter_with_paths = [(available_chapter[i], path) for i, path in
                                        enumerate(available_chapter_with_paths)]
        available_chapter_with_paths_sectioned = chunks(available_chapter_with_paths, chapter_per_section)
        section_count = len(list(available_chapter_with_paths_sectioned))
        json_section = {'latest_section_file': None}

        if os.path.isfile(manga_folder_path + "sectioned.json"):
            last_file_section_name = ''
            with open(manga_folder_path + "sectioned.json", 'r') as f:
                last_file_section_name = json.load(f)['latest_section_file']
            last_file_section_name = manga_folder_path + last_file_section_name
            if os.path.isfile(last_file_section_name):
                os.remove(last_file_section_name)

        for index, section_available_chapter_with_paths in enumerate(available_chapter_with_paths_sectioned):
            try:
                awal = re.search(r"(\d+\.\d+)|(\d+)", section_available_chapter_with_paths[0][0]).group()
                akhir = re.search(r"(\d+\.\d+)|(\d+)", section_available_chapter_with_paths[-1][0]).group()
            except:
                awal = section_available_chapter_with_paths[0][0].replace("Chapter", "").strip()
                akhir = section_available_chapter_with_paths[-1][0].replace("Chapter", "").strip()

            file_name = "{} Chapter {} - {}.pdf".format(self.__manga_name, awal, akhir)
            print("Creating {}".format(file_name))
            if os.path.isfile(self.__manga_dir + file_name):
                continue
            images_list = []
            bookmarked_page = []
            last_page = 0
            for (cahpter_name, available_chapter_with_path) in tqdm(section_available_chapter_with_paths):
                images_in_chapter_folder = sorted(os.listdir(available_chapter_with_path), key=cmp_to_key(sort))
                images_in_chapter_folder = list(filter(lambda x:
                                                       str(x).endswith(".jpg") or
                                                       str(x).endswith(".jpeg") or
                                                       str(x).endswith(".png"),
                                                       images_in_chapter_folder))
                images_in_chapter_folder = list(
                    map(lambda x: available_chapter_with_path + x, images_in_chapter_folder))
                images_in_chapter_folder = list(filter(is_image_good, images_in_chapter_folder))
                if images_in_chapter_folder:
                    bookmarked_page.append((last_page, cahpter_name))
                    images_list.extend(images_in_chapter_folder)
                    last_page += len(images_in_chapter_folder)

            with open(manga_folder_path + file_name, 'wb') as f:
                f.write(img2pdf.convert(images_list))

            reader = PyPDF2.PdfFileReader(manga_folder_path + file_name)
            writer = PyPDF2.PdfFileWriter()
            writer.appendPagesFromReader(reader)
            for bookmark in bookmarked_page:
                page = bookmark[0]
                title = bookmark[1]
                writer.addBookmark(title=title, pagenum=page)
            with open(manga_folder_path + file_name, 'wb') as f1:
                writer.write(f1)
                print(file_name + " Created")

            if index == section_count - 1:
                json_section['latest_section_file'] = file_name
        with open(manga_folder_path + "sectioned.json", 'w+') as f:
            json.dump(json_section, f)

    def done(self):
        import time
        from datetime import datetime
        file_banner = self.__main_dir + self.__manga_name + "/1." + self.__manga_name + ".jpg"
        if os.path.isfile(file_banner):
            now = datetime.now()
            second = now.second
            now = now.replace(second=second + 1)
            now = time.mktime(now.timetuple())
            os.utime(file_banner, (now, now))


list_manga = json.load(open("list_manga.json", 'r'))

for index, manga in enumerate(list_manga):
    print("{}\t{}".format(index + 1, manga['name']))
try:
    manga_type_code = int(input("\033[1mJenis Manga : \033[0m"))
    manga_type_code = manga_type_code - 1
    manga_type = list_manga[manga_type_code]
    for index, manga in enumerate(manga_type['manga']):
        print("{}\t{}".format(index + 1, manga['name']))

    manga_code = int(input("\033[1mPilih Manga : \033[0m"))
    manga_code = manga_code - 1
    manga = manga_type['manga'][manga_code]

    downloader = MangaDownloader(manga_type['main_dir'])
    downloader.set_manga_name(manga['name'])
    downloader.set_manga_page_link(manga['link'])
except:
    exit()

downloader.get_links_from_manga_page()
downloader.craw()
downloader.create_sectioned_chapter()
downloader.done()
