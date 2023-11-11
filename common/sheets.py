from datetime import datetime

import gspread
from celery import shared_task
from django.conf import settings
from gspread import WorksheetNotFound
from gspread.utils import ValueInputOption, ValueRenderOption
from ofirio_common.states_constants import states_from_short

from api_property.common.common import is_off_market_status
from api_property.common.rebates import get_full_rebate


list_ggl_cols = [
    'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1', 'M1',
    'N1', 'O1', 'P1', 'Q1', 'R1', 'S1', 'T1', 'U1', 'V1', 'W1', 'X1', 'Y1', 'Z1',
    'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM',
    'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ',  # LEN 52
]


def get_init_data():
    return {'Order Number': '',
            'Full Name': '',
            'Email': '',
            'Phone': '',
            'Message': '',
            'Move in Date': '',
            'Tour Type': '',
            'Schedule Tour Date': '',
            'Schedule Tour Time': '',
            'Time of Lead': '',
            'URL': '',
            'State': '',
            'County': '',
            'City': '',
            'Zip': '',
            'Address Line': '',
            'Prop Class': '',
            'Price': '',
            'Rebate': '',
            'Rebate Percent': '',
            'Best Time To Call': '',
            'Baths': '',
            'Beds': '',
            'Living Area': '',
            'Year Built': '',
            'Agent Commission': '',
            'Agent Percent': '',
            'Ofirio Profit': '',
            'Ofirio Percent': '',
            'Listing Agent Email': '',
            'Listing Agent Phone': '',
            'Listing(MLS) Id': '',
            'Status': '',
            'Assigned Agent': '',
            'Agent Email': '',
            'Email Sent': '',
            'Follow Up': '',
            # fields for agent:
            'Comment': '',
            'Do you know about Ofirio rebates?': '',
            'First time homebuyer?': '',
            'Own a home? Are you selling it?': '',
            'How far in Process?': '',
            'What kind of home are you looking for?': '',
            'Purpose of new home?': '',
            'Are you working with a lender?': '',
            'Are you currently working with an agent?': '',
            'Downpayment?': '',
            'Credit score?': '',
            'How many people will live with you?': '',
            'Pets?': '',
            }


num_cols = len(get_init_data())


def conn_to_sheets(path):
    try:
        conn = gspread.service_account(filename=path)
    except (FileNotFoundError, ValueError):
        return

    name_lids = f'{settings.PROJECT_DOMAIN.title()[:-4]} Leads'

    try:
        sheets = conn.open(name_lids)
    except (gspread.exceptions.SpreadsheetNotFound or AttributeError):
        formats_title = [{"range": f"A1:{list_ggl_cols[-1]}",
                          "format": {"textFormat": {"bold": True}}}]
        formats_usual = [{"range": f"A2:{list_ggl_cols[-1].replace('1', '2')}",
                          "format": {"textFormat": {"bold": False}}}]
        sheets = conn.create(name_lids)
        for user in settings.SHEETS_USER:
            sheets.share(user, perm_type='user', role='writer')

        sheet = sheets.add_worksheet(title='Leads', cols=num_cols, rows=4)
        frs_to_del = sheets.worksheet('Sheet1')
        sheets.del_worksheet(worksheet=frs_to_del)
        sheet.batch_format(formats_title, )
        sheet.batch_format(formats_usual)
        sheet.update(f"A1:{list_ggl_cols[-1]}", [list(get_init_data().keys())])

    return sheets


def get_or_create_worksheet(name, sheets):
    try:
        sheet = sheets.worksheet(name)
    except WorksheetNotFound:
        sheet = sheets.add_worksheet(title=name, cols=num_cols, rows=2)
    return sheet


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def add_to_google_sheets(req, prop):
    sheets = conn_to_sheets(settings.BASE_DIR / 'djangoproject/token_gspread.json')
    if not sheets:
        return

    data_to_send = get_init_data()
    sheet = get_or_create_worksheet('Leads', sheets)

    if prop:
        address = prop.get('address', {})
        data = prop.get('data', {})
        rebate_data = {}

        if req.get('prop_class') != 'rent':
            rebate_data = get_full_rebate(
                prop['address']['zip'],
                (req.get('price') or data.get('price')),
                (prop['status'])
            )

        data_to_send.update(
            {'State': states_from_short.get(address.get('state_code')),
             'County': address.get('county'),
             'City': address.get('city'),
             'Zip': address.get('zip'),
             'Address Line': address.get('line'),
             'Price': req.get('price') or data.get('price'),
             'Rebate': rebate_data.get('rebate'),
             'Rebate Percent': rebate_data.get('rebate_percent'),
             'Beds': data.get('beds'),
             'Baths': data.get('baths'),
             'Living Area': data.get('building_size'),
             'Year Built': data.get('year_built'),
             'Agent Commission': rebate_data.get('agent_commission'),
             'Agent Percent': rebate_data.get('agent_percent'),
             'Ofirio Profit': rebate_data.get('ofirio_commission'),
             'Ofirio Percent': rebate_data.get('ofirio_percent'),
             'Listing Agent Email': prop.get('features', {}).get('Listing', {}).get(
                 'Listing Information', {}).get('Listing Agent Email'),
             'Listing Agent Phone': prop.get('params', {}).get('agent_phone'),
             'Listing(MLS) Id': data.get('source_id'),
             })

    data_to_send.update({
        'Order Number': req['order_number'],
        'Full Name': req['full_name'],
        'Email': req['email'],
        'Phone': req['phone'].replace('-', '') if req['phone'] else '',
        'Message': req.get('request'),
        'Move in Date': str(req.get('move_in_date')),
        'Tour Type': req.get('tour_type'),
        'Schedule Tour Date': str(req.get('schedule_tour_date')),
        'Schedule Tour Time': str(req.get('schedule_tour_time')),
        'Time of Lead': datetime.now().isoformat(sep=' ', timespec='minutes'),
        'URL': req.get('url'),
        'Prop Class': req.get('prop_class'),
        'Best Time To Call': req.get('best_time_to_call'),
        'Status': get_render(sheet, 'Status'),
        'Assigned Agent': get_render(sheet, 'Assigned Agent'),
        'Agent Email': get_render(sheet, 'Agent Email'),
        'Email Sent': get_render(sheet, 'Email Sent'),
        'Follow Up': get_render(sheet, 'Follow Up'),
    })
    index = get_row_number(sheet) + 1
    sheet.insert_row(list(data_to_send.values()), index=index,
                     value_input_option=ValueInputOption.user_entered, )


def get_row_number(sheet):
    return len(sheet.col_values(1))


def get_render(sheet, col: str, row=2):
    val = sheet.cell(row, list(get_init_data().keys()).index(col) + 1,
                     value_render_option=ValueRenderOption.formula).value
    if val and str(val).startswith('='):
        return val
    return ''


class MigrateSheets:
    pass
