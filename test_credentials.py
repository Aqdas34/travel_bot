#!/usr/bin/env python3
"""
Test script to verify Google Sheets credentials
"""

import gspread
from google.oauth2.service_account import Credentials

def test_google_sheets():
    try:
        # Load credentials
        creds = Credentials.from_service_account_file(
            'service_account.json', 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Authorize
        gc = gspread.authorize(creds)
        
        # Open spreadsheet
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1lWAk1cOb7fY5EJJXCm12XLc4ohNTQ25jwQvH5s4B2aU/edit?usp=sharing')
        worksheet = sh.sheet1
        
        # Test write
        test_row = ['TEST', 'test@example.com', '123456789', 'Hotel', '2024-07-01', 'Test City', '']
        worksheet.append_row(test_row)
        
        print("✅ SUCCESS: Google Sheets credentials are working!")
        print("Test row added successfully.")
        
        # Clean up - remove test row
        all_values = worksheet.get_all_values()
        if all_values and all_values[-1] == test_row:
            worksheet.delete_rows(len(all_values))
            print("Test row cleaned up.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure service_account.json is in the project root")
        print("2. Verify the file contains valid JSON")
        print("3. Check that the service account has access to the spreadsheet")
        print("4. Ensure the spreadsheet URL is correct")

if __name__ == "__main__":
    test_google_sheets() 