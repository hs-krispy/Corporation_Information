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
finance_information = gs.worksheet('finance_information')

corporation_name = job_information.col_values(1)[1:]
exist_corporation_name = finance_information.col_values(1)

new_corporation_name = list(set(corporation_name) - set(exist_corporation_name)) 

finance_info_list = []

for corp_name in new_corporation_name:
    corp_name = corp_name.split('(')[0]
    informations = scarp_info(corp_name)
    if informations is None:
        finance_info_list.append(pd.DataFrame({i: [corp_name if i == 'name' else 'None'] for i in ['name', '계정과목/연도', '2020', '2021', '2022']}))
        continue
    finance_info_list.append(get_info(informations[0].split(' '), informations[1], corp_name))

corp_finance_df = pd.concat(finance_info_list, axis=0).fillna('Unknown')    
print(corp_finance_df)
if len(set(corporation_name)) == len(new_corporation_name):
    set_with_dataframe(worksheet=finance_information, dataframe=corp_finance_df, include_index=False, include_column_header=True, resize=True)
else:
    gs.values_append('finance_information', {'valueInputOption': 'RAW'}, {'values': corp_finance_df.values.tolist()})
