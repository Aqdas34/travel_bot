
import gspread
from google.oauth2.service_account import Credentials


# Define scopes first
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "astute-expanse-466322-s0",
    "private_key_id": "4255319386134fc98f2b6c42a4375fb47787c2a0",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDdrYkah8cY2LuF
sbPPnmAZXmG4RMf+1fYcM/qa7+1WVPveyMHyIZuDAI84xG3qSV9uDuDcGbbOf+rw
jsXZZsPFEJVa3ODi8tK9RRM0sgaj0iidNcs2v6e9NdoiP52NSKGG/S4KoLoqra25
YV0v8Av8SatUAS+/Mm4j8dlzoGOBKkJHn7DuuJabvZjmO2nfMt8CPlV0Y8htsesS
rKY00TRjXaIuJu84BKNyryK4eU+rx9Ah8680Rt3kwHasj8y8dRxIYL2bwZN5UopJ
csVPswT6QTjVBsnpF1J3iwQgsulmQicUtV0jcL7YBk0JXz1JESN5d8MAuCxSad+x
47Z3pg1HAgMBAAECggEAVXy6PkZ1U9IlAupkLuFjKvVYVwEDZXWqyvaKotx62Qu9
9AzUqmUmfS8mjFxIDQ1NpXpMYeTyuBDhj/JnPy8fuSvrhRZgDXVaKs5sGSq8X8nI
itP3cb4YWGHfpMyGnDkRvaZ+bm/MS3Ad6jsvfjCi1qCsVyF8Ac5XZjo6wxnrtZ/Y
FuR7iEDMmwcjoXhL5CgGRMDAipHMG294lX8bGtuICLxYO0//fVNjQUohZ32QdJLY
w+LWYaJHp2hiVlCV0F9Sy4XIrpaj9yHQIzdZgzTjXMcJSjiAuaz7QVj2Db3chnrB
pteZqEgNzbeFu129fV+XU/e8eTuQ/+fId5CYugER5QKBgQDzcE3h+WSxkSJZFmCc
9Bg5aPcugnDGj7ONUTaxkZWxr3g7H+66ebr8gwyFDgHyALnnPwE8LUKvNr6BGEmx
zBKEvN2ypLnEsTGw16dz2k0/hM5fWEtHCW6LDr0XhXx1iL9Caec+NtP6PK0kVY5d
xTJqGavbfiyMSyFORBFIvt5/4wKBgQDpHchTY9Vyy8xF3jqO4fVSUupTRbGlnP0g
DdkdQD+o2LY8gFFEhChU0SR4V/rEbrTmr6WSNyiiZhHdXQUZkSJI/qOxM48rKDx9
PPxfHLZjictMA+3HIeg6lxE371yd3hiPjkN82S1pc5fNsA7qdBfOG6lwvEQkHk8v
CR3xnOfyTQKBgC4D+HTSk3oNGRUF6dVBPqL7eF3OQksGNsZrp48BGe6wYGWsr4+I
GxRIIUG1WCDKillvy2f4ljZQfsogMS3uiUGWAcIW6RaI9/+ZhAmeJiPvkqLrKa+P
1NlsO8oKbXA6HQ0Mv60+5+rRNVk84uBOuizcFWQ0AW+zc+Q7cZjym1RJAoGAYQvQ
AL839eFXueJo+GCi81GnUWFbMjnnurdpIl9D4TPOseMtcdueuqiSiTL/J1V7I+oN
gJBL70eUulXmMJ2V61Nuq+9t86Z9gBmqaqIWX9vWcV/VVigMeI+5UFLqeKIkEWdF
Oy1iVVsU4EEiBIKuAlTLti36JBsmFcuy1onemaUCgYAmq08YOtGzMSK2O5lmVxTP
XvzzaF7Ktoy+UR+cgY6maxC0L3tySkbAippjCmAHpX30wUM8HyKJG0W266k48LeQ
w6Mipe7wqEzWTeLmMP4qIzYdfSdxcvwOMdoXxH1EWoNKachOPCVYoIW09HyBDIXu
NBA0oUdrdAOVV8SHo5rYfA==
-----END PRIVATE KEY-----""",
    "client_email": "chatbot@astute-expanse-466322-s0.iam.gserviceaccount.com",
    "client_id": "111423336873741087620",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/chatbot%40astute-expanse-466322-s0.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

def get_gsheet_client():
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc
def test_gsheet_connection():
    try:
        gc = get_gsheet_client()
        # Replace this with a real sheet URL you’ve shared with the service account
        sheet_url = 'https://docs.google.com/spreadsheets/d/1lWAk1cOb7fY5EJJXCm12XLc4ohNTQ25jwQvH5s4B2aU/edit?usp=sharing'
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)
        data = worksheet.get('A1')
        print("✅ Connection successful! A1 value:", data)
    except Exception as e:
        print("❌ Connection failed:", e)

# Run the test
test_gsheet_connection()