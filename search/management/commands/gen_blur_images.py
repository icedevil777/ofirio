import os

import cv2
import requests
from django.conf import settings
from ofirio_common.enums import EsIndex
from ofirio_common.helpers import get_elastic_search
from psycopg2.extensions import adapt, register_adapter, AsIs

from common.management import OfirioCommand


class Command(OfirioCommand):
    help = 'Generate Blur Images for Properies without images'

    def handle(self, *args, **options):
        self.log('Generate Blur Images for Propery without images')
        self.log('-' * 20)

        # Search query
        es = get_elastic_search()
        search_query_body = {
            "size": 500,
            "from": 0,
            "query" : {
                "bool": {
                    "must": [],
                    "filter": [],
                }
            },
        }
        res = es.search(index=EsIndex.SEARCH_INVEST, body=search_query_body)

        # GET PHOTOS FROM SEARCH
        photos = []
        for hit in res['hits']['hits']:
            source = hit['_source']
            prop_id = source['prop_id']
            photo1 = source['photo1']
            if photo1:
                photos.append(photo1)


        self.log(len(photos), 'images found from elastic')
        if len(photos)>=settings.BLUR_IMAGES_QTY:
            self.log('Crop images qty to 100')
            photos = photos[:settings.BLUR_IMAGES_QTY]

        if len(photos)<settings.BLUR_IMAGES_QTY:
            self.log('Less than', settings.BLUR_IMAGES_QTY, 'images found - exit')

        img_dir = str(settings.BASE_DIR) + '/media/blur_images'
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
            self.log('Create dir: ', img_dir)

        i = 0
        for photo in photos:
            self.log(i, photo)

            page = requests.get(photo)
            tmp_path = str(settings.BASE_DIR) + '/tmp/img.jpg'
            with open(tmp_path, 'wb') as f:
                f.write(page.content)

            cv2img = cv2.imread(tmp_path)
            blurimg = cv2.blur(cv2img, (25, 25))

            img_path = img_dir + '/' + str(i) + '.jpg'
            cv2.imwrite(img_path, blurimg)
            i+= 1


        self.log('Process images...')

        self.log('End of script')
        self.log('-' * 20)
