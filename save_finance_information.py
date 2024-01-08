import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from get_information import *
from save_job_information import save_job_info

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
json_file_name = 'gce-project-343715-1e2f693604ae.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

save_job_info()

gs = gc.open('crawling_data')
job_information = gs.worksheet('job_information')
finance_information = gs.worksheet('finance_information2')
      
corporation_name = job_information.col_values(1)[1:]
exist_corporation_name = finance_information.col_values(1)

new_corporation_name = list(set(list(map(lambda x: x.split('(')[0], corporation_name))) - set(exist_corporation_name))

if len(new_corporation_name) > 0:

    finance_info_list = []
    not_found_corp_list = []

    for corp_name in new_corporation_name:
        corp_name = corp_name.split('(')[0]
        informations = scarp_info(corp_name)
        if informations is None:
            not_found_corp_list.append(corp_name)
            continue
        finance_info_list.append(get_info(informations[0].split(' '), informations[1], corp_name))

    if len(finance_info_list) > 0:
        corp_finance_df = pd.concat(finance_info_list, axis=0)
        result_df = corp_finance_df.pivot_table(index='name', columns='계정과목/연도', values=['2020', '2021', '2022'], aggfunc='max').stack(level=0)
        result_df['영업이익률'] = result_df.apply(lambda x: None if (isinstance(x['영업손익'], str)) & (isinstance(x['매출액'], str)) \
            else x['영업손익'] / x['매출액'] if x['매출액'] > 0 else None, axis=1)
        result_df = result_df.reset_index().rename(columns={'level_1': '연도'})
        result_df = pd.concat([result_df, pd.DataFrame({'name': not_found_corp_list})], axis=0).fillna('Unknown')
    else:
        result_df = pd.DataFrame({'name': not_found_corp_list})

    print(result_df)
    if len(set(corporation_name)) == len(new_corporation_name):
        set_with_dataframe(worksheet=finance_information, dataframe=result_df, include_index=False, include_column_header=True, resize=True)
    else:
        gs.values_append('finance_information2', {'valueInputOption': 'RAW'}, {'values': result_df.values.tolist()})