from io import StringIO
from unittest.mock import patch, MagicMock

from django.core.management import call_command

from account.tests.factories import create_user
from api_property.enums import PropClass
from api_property.models import SimilarPropertyNotificationModel, PropCity, PropertyUpdateModel
from account.models.favorite_property import FavoriteProperty
from api_property.tests.base import PropertyBaseTest
from api_property.tests.constants import PROP_673, PROP_8BE


class CommandNotificationTest(PropertyBaseTest):

    def setUp(self):
        super().setUp()
        self.cmd_out = StringIO()


@patch('api_property.management.prop_notification.get_pg_connection')
@patch('api_property.management.prop_notification.get_similar')
@patch('common.klaviyo.util.track')
@patch('common.klaviyo.util.read_notification_props')
@patch('common.klaviyo.helpers.ask_socket_for_one_url')
class SimilarNotificationTest(CommandNotificationTest):

    def test_nothing_called_when_empty(self, socket_mock, read_mock, track_mock,
                                       get_similar_mock, _):
        call_command('similar_notification', stdout=self.cmd_out)

        self.assertFalse(socket_mock.called)
        self.assertFalse(read_mock.called)
        self.assertFalse(track_mock.called)
        self.assertFalse(get_similar_mock.called)

    def test_db_and_klaviyo_called(self, socket_mock, read_mock, track_mock, get_similar_mock, _):
        # buy main, buy related, rent main, rent related
        read_mock.side_effect = [[], [PROP_8BE], [], []]

        get_similar_mock.return_value = [{'prop_id': '456'}, {'prop_id': '567'},
                                         {'prop_id': '678'}, {'prop_id': '789'}]
        user = create_user()
        es = user.emailsettings_set.first()
        es.similars = True
        es.save()

        SimilarPropertyNotificationModel.objects.create(
            prop_id='123', prop_class=PropClass.BUY, user=user,
        )
        SimilarPropertyNotificationModel.objects.create(
            prop_id='234', prop_class=PropClass.RENT, user=user,
        )

        call_command('similar_notification', stdout=self.cmd_out)
        self.assertTrue(socket_mock.called)
        self.assertTrue(read_mock.called)
        self.assertTrue(track_mock.called)
        self.assertTrue(get_similar_mock.called)
        self.assertIn('Found 4 Buy Similar props', self.cmd_out.getvalue())

        # OT-2902: rent currently disabled
        self.assertNotIn('Found 4 Invest Similar props', self.cmd_out.getvalue())
        self.assertNotIn('Found 4 Rent Similar props', self.cmd_out.getvalue())

        # check klaviyo.track payload
        payload = track_mock.mock_calls[0][1][2]['props']
        self.assertNotIn('main', payload)
        self.assertEqual(len(payload['related'][0]), 1)
        self.assertEqual(payload['related'][0][0]['prop_id'], '8BE92C6B767350E9C428')


@patch('api_property.management.commands.prop_history_notification.Command.read_prop_cache')
@patch('common.klaviyo.util.track')
@patch('common.klaviyo.util.read_notification_props')
@patch('common.klaviyo.helpers.ask_socket_for_one_url')
class PropHistoryNotificationTest(CommandNotificationTest):

    def test_nothing_called_when_empty(self, socket_mock, read_mock, track_mock, read_pcache_mock):
        call_command('prop_history_notification', stdout=self.cmd_out)

        self.assertFalse(socket_mock.called)
        self.assertFalse(read_mock.called)
        self.assertFalse(track_mock.called)
        self.assertFalse(read_pcache_mock.called)

    def test_db_and_klaviyo_called(self, socket_mock, read_mock, track_mock, read_pcache_mock):
        read_mock.side_effect = [[PROP_8BE], []]
        read_pcache_mock.side_effect = [
            {'8BE92C6B767350E9C428': {'prop_id': '8BE92C6B767350E9C428', 'status': 'for_sale',
                                      'price': 897000}},
            {},
        ]
        user = create_user()
        es = user.emailsettings_set.first()
        es.prop_updates = True
        es.save()

        PropertyUpdateModel.objects.create(prop_id='8BE92C6B767350E9C428', user=user,
                                           prop_class=PropClass.BUY)

        call_command('prop_history_notification', stdout=self.cmd_out)
        self.assertTrue(socket_mock.called)
        self.assertTrue(read_mock.called)
        self.assertTrue(track_mock.called)
        self.assertTrue(read_pcache_mock.called)
        self.assertIn('Status for Buy prop 8BE92C6B767350E9C428 changed from "" to "for_sale"',
                      self.cmd_out.getvalue())

        # check klaviyo.track payload
        payload = track_mock.call_args[0][2]['props']
        self.assertNotIn('related', payload)
        self.assertEqual(len(payload['main'][0]), 1)
        self.assertEqual(payload['main'][0][0]['prop_id'], '8BE92C6B767350E9C428')


@patch('common.klaviyo.util.track_add_favorite')
@patch('api_property.management.prop_notification.get_pg_connection')
@patch('api_property.management.prop_notification.get_similar')
@patch('common.klaviyo.util.track')
@patch('common.klaviyo.util.read_notification_props')
@patch('common.klaviyo.helpers.ask_socket_for_one_url')
class FavoriteSimilarNotificationTest(CommandNotificationTest):

    def test_db_and_klaviyo_called(self, socket_mock, read_mock, track_mock, get_similar_mock,
                                   _, __):
        read_mock.side_effect = [[], [PROP_8BE]]
        get_similar_mock.return_value = [{'prop_id': '456'}, {'prop_id': '567'},
                                         {'prop_id': '678'}, {'prop_id': '789'},
                                         {'prop_id': '890'}, {'prop_id': '901'}]
        user = create_user()
        es = user.emailsettings_set.first()
        es.favorites_match_notification = True
        es.save()

        FavoriteProperty.objects.create(
            prop_id='8BE92C6B767350E9C428', prop_class=PropClass.BUY, user=user,
        )

        call_command('similar_fav_notification', stdout=self.cmd_out)
        self.assertTrue(socket_mock.called)
        self.assertTrue(read_mock.called)
        self.assertTrue(track_mock.called)
        self.assertTrue(get_similar_mock.called)
        self.assertIn('Found 6 Favorite Buy Similar props', self.cmd_out.getvalue())

        # OT-2902: rent currently disabled
        self.assertNotIn('Found 4 Favorite Invest Similar props', self.cmd_out.getvalue())
        self.assertNotIn('Found 4 Favorite Rent Similar props', self.cmd_out.getvalue())

        # check klaviyo.track payload
        payload = track_mock.call_args[0][2]['props']
        self.assertNotIn('main', payload)
        self.assertEqual(len(payload['related'][0]), 1)
        self.assertEqual(payload['related'][0][0]['prop_id'], '8BE92C6B767350E9C428')


@patch('common.klaviyo.util.track_add_favorite')
@patch('api_property.management.commands.prop_history_fav_notification.get_pg_connection')
@patch('api_property.management.commands.prop_history_fav_notification.get_similar')
@patch('api_property.management.commands.prop_history_fav_notification.Command.read_prop_cache')
@patch('common.klaviyo.util.track')
@patch('common.klaviyo.util.read_notification_props')
@patch('common.klaviyo.helpers.ask_socket_for_one_url')
class FavoritePropHistoryNotificationTest(CommandNotificationTest):

    def test_db_and_klaviyo_called(self, socket_mock, read_mock, track_mock, read_pcache_mock,
                                   get_similar_mock, _, __):
        # main, related
        read_mock.side_effect = [[PROP_8BE], [PROP_673]]

        read_pcache_mock.side_effect = [
            {'8BE92C6B767350E9C428': {'prop_id': '8BE92C6B767350E9C428',
                                      'status': 'for_sale', 'price': 897000}},
            {},
        ]
        get_similar_mock.return_value = [{'prop_id': '67350E9C4288BE92C6B7'}]
        user = create_user()
        es = user.emailsettings_set.first()
        es.favorites = True
        es.save()

        FavoriteProperty.objects.create(prop_id='8BE92C6B767350E9C428', user=user,
                                        prop_class=PropClass.BUY)

        call_command('prop_history_fav_notification', stdout=self.cmd_out)
        self.assertTrue(socket_mock.called)
        self.assertTrue(read_mock.called)
        self.assertTrue(track_mock.called)
        self.assertTrue(read_pcache_mock.called)

        exp_out = 'Status for Buy Favorite prop 8BE92C6B767350E9C428 changed from "" to "for_sale"'
        self.assertIn(exp_out, self.cmd_out.getvalue())

        # check klaviyo.track payload
        payload = track_mock.call_args[0][2]['props']

        self.assertEqual(len(payload['main'][0]), 1)
        self.assertEqual(payload['main'][0][0]['prop_id'], '8BE92C6B767350E9C428')

        self.assertEqual(len(payload['related'][0]), 1)
        self.assertEqual(payload['related'][0][0]['prop_id'], '67350E9C4288BE92C6B7')


@patch('api_property.management.commands.good_deal_notification.Command._query_for_props')
@patch('common.klaviyo.util.track')
@patch('common.klaviyo.util.read_notification_props')
@patch('common.klaviyo.helpers.ask_socket_for_one_url')
class GoodDealNotificationTest(CommandNotificationTest):

    def test_nothing_called_when_empty(self, socket_mock, read_mock, track_mock, query_mock):
        call_command('good_deal_notification', stdout=self.cmd_out)

        self.assertFalse(socket_mock.called)
        self.assertFalse(read_mock.called)
        self.assertFalse(track_mock.called)
        self.assertFalse(query_mock.called)

    def test_db_and_klaviyo_called(self, socket_mock, read_mock, track_mock, query_mock):
        # buy main, buy related, rent main, rent related
        read_mock.side_effect = [[], [PROP_8BE], [], []]

        query_mock.return_value = ['456', '567', '678', '789']
        user = create_user()
        es = user.emailsettings_set.first()
        es.good_deals = True
        es.save()

        city = PropCity.objects.create(city='Dallas', county='', state_id='TX', label='Dallas, TX')

        gds = user.gooddealsettings_set.first()
        gds.buy_enabled = True
        gds.cities.add(city)
        gds.save()

        call_command('good_deal_notification', stdout=self.cmd_out)
        self.assertTrue(socket_mock.called)
        self.assertTrue(read_mock.called)
        self.assertTrue(track_mock.called)
        self.assertTrue(query_mock.called)
        self.assertIn('Found 4 Buy Good_Deal props', self.cmd_out.getvalue())
        self.assertNotIn('Found 4 Rent Good_Deal props', self.cmd_out.getvalue())
        self.assertNotIn('Found 4 Invest Good_Deal props', self.cmd_out.getvalue())

        # check klaviyo.track payload
        payload = track_mock.mock_calls[0][1][2]['props']
        self.assertNotIn('main', payload)
        self.assertEqual(len(payload['related'][0]), 1)
        self.assertEqual(payload['related'][0][0]['prop_id'], '8BE92C6B767350E9C428')
