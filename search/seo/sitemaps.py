import json
import socket
import xml.etree.cElementTree as ET
from datetime import datetime

from django.conf import settings

from common.utils import get_absolute_url


def gen_html_sitemaps(state_id, section, links):
    '''should create text file for each city with the list of indexed pages'''
    for city, links_ in links.items():
        filename = f'{section}-{city}.txt'
        sitemap_dir = settings.BASE_DIR / f'data/html-sitemap/{state_id}'.lower()
        sitemap_dir.mkdir(parents=True, exist_ok=True)
        with open(sitemap_dir / filename, 'w') as f:
            f.write('\n'.join(json.loads(x)[0] for x in links_))


def gen_html_sitemaps_buildings(state_id, section, links):
    '''writes json to the dir with other htmp sitemaps'''
    for city, links_ in links.items():
        filename = f'{section}-{city}.txt'
        sitemap_dir = settings.BASE_DIR / f'data/html-sitemap/{state_id}'.lower()
        sitemap_dir.mkdir(parents=True, exist_ok=True)
        with open(sitemap_dir / filename, 'w') as f:
            json.dump(links_, f)


def gen_srp_sitemap(url_list, file_name: str):
    root = ET.Element("urlset")
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    tree = ET.ElementTree(root)
    dt = datetime.now().strftime("%Y-%m-%d")
    if len(url_list) <= 30000:
        for _url in url_list:
            _url = json.loads(_url)[0]
            doc = ET.SubElement(root, "url")
            ET.SubElement(doc, "loc").text = _url
            ET.SubElement(doc, "lastmod").text = dt
        tree.write(settings.SITEMAPS_DIR_SRP / file_name,
                   encoding='utf-8', xml_declaration=False)
    else:
        start = 0
        end = 30000
        i = 1
        while start <= len(url_list):
            for _url in url_list[start:end]:
                _url = json.loads(_url)[0]
                doc = ET.SubElement(root, "url")
                ET.SubElement(doc, "loc").text = _url
                ET.SubElement(doc, "lastmod").text = dt
            count_file_name = file_name.replace('.xml', f'-{i}.xml')
            tree.write(settings.SITEMAPS_DIR_SRP / count_file_name,
                       encoding='utf-8', xml_declaration=False)
            start += 30000
            end += 30000
            i += 1


def gen_prop_sitemap(url_list, file_name: str, path='ads'):
    if not url_list:
        return
    root = ET.Element("urlset")
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    tree = ET.ElementTree(root)
    for lastmod, _url in url_list:
        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = _url
        ET.SubElement(doc, "lastmod").text = lastmod
    if path == 'ads':
        path = settings.BASE_DIR / 'static_django/sitemaps-ads' / file_name
    else:
        path = settings.BASE_DIR / 'static_django/sitemaps-srp' / file_name
    tree.write(path, encoding='utf-8', xml_declaration=False)
    print('Created sitemap', path)


def init_socket():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(settings.URLGEN_SOCKET_ADDRESS)
    return s


def gen_indexsitemap(sitemaps, filepath):
    root = ET.Element("sitemapindex")
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    tree = ET.ElementTree(root)
    for _url in sitemaps:
        doc = ET.SubElement(root, "sitemap")
        ET.SubElement(doc, "loc").text = get_absolute_url(f'/{_url}')
    tree.write(filepath, encoding='utf-8', xml_declaration=False)
    print('Created sitemap', filepath)


def ask_socket_for_one_url(prop_id, address):
    """
    Ask frontend socket for a URL of provided property and return the URL
    """
    socket = init_socket()
    socket.settimeout(5.0)
    sock_str = [{'generator': 'listing', 'id': prop_id, 'address': address}]
    socket.send(bytes(json.dumps(sock_str).encode('utf-8')) + b'end')
    url = socket.recv(1024).decode('utf-8')[2:-2]
    socket.close()
    return url
