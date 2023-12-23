import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from get_name import get_job_info

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
json_file_name = 'gce-project-343715-1e2f693604ae.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

def save_job_info():
    gs = gc.open('crawling_data')
    job_information = gs.worksheet('job_information')
    
    job_info_df = get_job_info('데이터')
    set_with_dataframe(worksheet=job_information, dataframe=job_info_df, include_index=False, include_column_header=True, resize=True)

