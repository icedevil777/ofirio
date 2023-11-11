import json
import httplib2

import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from common.emails import GoogleIndexEmail

User = get_user_model()

from common.management import OfirioCommand


class Command(OfirioCommand):

    def add_arguments(self, parser):
        parser.add_argument('--dry_run', '--dry_run', action='store_true')

    def send_to_google(self, idx, link):
        endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        body = {'url': link, 'type': "URL_UPDATED"}
        if self.dry_run:
            self.log(f'[{idx}] sent', body)
            return True

        response, content = self.http.request(endpoint, method="POST", body=json.dumps(body))
        self.log(f'[{idx}] sent', body)
        self.log(f'[{idx}] got', content)
        result = json.loads(content.decode())
        # For debug purpose only
        if "error" in result:
            self.log(
                "Error({} - {}): {}".format(
                    result["error"]["code"],
                    result["error"]["status"],
                    result["error"]["message"],
                )
            )
            return False

        self.log(
            "urlNotificationMetadata.url: {}".format(result["urlNotificationMetadata"]["url"])
        )
        self.log("urlNotificationMetadata.latestUpdate.url: {}".format(
            result["urlNotificationMetadata"]["latestUpdate"]["url"]))
        self.log("urlNotificationMetadata.latestUpdate.type: {}".format(
            result["urlNotificationMetadata"]["latestUpdate"]["type"]))
        self.log("urlNotificationMetadata.latestUpdate.notifyTime: {}".format(
            result["urlNotificationMetadata"]["latestUpdate"]["notifyTime"]))
        return True

    def handle(self, *args, **options):
        self.dry_run = options['dry_run'] or False
        scopes = ["https://www.googleapis.com/auth/indexing"]
        json_key = settings.BASE_DIR / 'data' / 'creds' / 'google_index_api_creds.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scopes=scopes)
        self.http = credentials.authorize(httplib2.Http())
        if self.dry_run:
            self.log('NOT really sending to google')
        self._handle(*args, **options)

    def _handle(self, *args, **options):
        df = pd.read_csv(settings.BASE_DIR / 'data/urls.csv')
        idx = 0
        for idx, link in df.itertuples():
            resp = self.send_to_google(idx, link)
            if not resp:
                # looks like we hit a limit
                break
        else:
            idx += 1
        df.iloc[:idx].to_csv('/tmp/urls.csv')
        user = User.objects.get(email='vlad.baloban@rigelstorm.com')
        GoogleIndexEmail.send(user, '/tmp/urls.csv')
        df = df.iloc[idx:]
        df.to_csv(settings.BASE_DIR / 'data/urls.csv', index=False)
