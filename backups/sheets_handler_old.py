"""
Google Sheets Handler
Manages reading from and writing to Google Sheets
"""

import os
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import List, Dict


class SheetsHandler:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        """
        SheetsHandler supports both Service Account and OAuth user credentials.
        If credentials.json is a service account key, uses ServiceAccountCredentials.
        If credentials.json is an OAuth client secret, uses gspread.oauth and stores token in token.json.
        Always resolves credentials_path to absolute path from project root.
        """
        # Resolve to absolute path relative to this file's directory
        if not os.path.isabs(credentials_path):
            self.credentials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), credentials_path))
        else:
            self.credentials_path = credentials_path
        
        if not os.path.isabs(token_path):
            self.token_path = os.path.abspath(os.path.join(os.path.dirname(__file__), token_path))
        else:
            self.token_path = token_path
            
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with Google Sheets API using either Service Account or OAuth user credentials.
        Auto-detects credentials.json type.
        """
        try:
            print(f"Authenticating with Google Sheets API using credentials from {self.credentials_path} ...")
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")

            # Detect credentials type
            with open(self.credentials_path, "r", encoding="utf-8") as f:
                cred_data = json.load(f)

            if "type" in cred_data and cred_data["type"] == "service_account":
                # Service Account credentials
                print("Detected Service Account credentials.")
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_path, scope
                )
                self.client = gspread.authorize(creds)
                print("Authentication successful (Service Account)!")
            elif "installed" in cred_data and "client_id" in cred_data["installed"]:
                # OAuth user credentials
                print("Detected OAuth user credentials.")
                import gspread.auth
                self.client = gspread.oauth(
                    credentials_filename=self.credentials_path,
                    authorized_user_filename=self.token_path
                )
                print("Authentication successful (OAuth user)!")
            else:
                raise ValueError("Unrecognized credentials.json format. Must be a service account key or OAuth client secret.")
        except Exception as e:
            print(f"ERROR: Authentication failed: {str(e)}")
            raise
    
    def load_word_list(self, sheet_url: str) -> List[Dict]:
        """Load word list from Google Sheets"""
        try:
            print(f"Loading word list from Google Sheets...")
            
            # Open the spreadsheet
            sheet = self.client.open_by_url(sheet_url)
            worksheet = sheet.get_worksheet(0)  # First sheet
            
            # Get all values
            data = worksheet.get_all_values()
            
            if not data:
                raise ValueError("Sheet is empty")
            
            # Assume first row is header
            headers = data[0]
            word_list = []
            
            for row in data[1:]:
                if len(row) >= 2:  # At least French and English columns
                    word_data = {
                        'french': row[0].strip(),
                        'english': row[1].strip() if len(row) > 1 else '',
                        'pos': row[2].strip() if len(row) > 2 else ''
                    }
                    if word_data['french']:  # Skip empty rows
                        word_list.append(word_data)
            
            print(f"Loaded {len(word_list)} words from Google Sheets")
            return word_list
            
        except Exception as e:
            print(f"ERROR: Failed to load word list: {str(e)}")
            raise
    
    def create_output_sheet(self, results: Dict, word_list: List[Dict]) -> str:
        """
        Create new Google Sheet with optimization results
        Returns URL of created sheet
        """
        try:
            print("Creating output Google Sheet...")
            
            # Create new spreadsheet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sheet_name = f"French_Vocab_Optimization_{timestamp}"
            spreadsheet = self.client.create(sheet_name)
            
            # Share with owner (make it accessible)
            # spreadsheet.share('', perm_type='anyone', role='reader')
            
            print(f"Created spreadsheet: {sheet_name}")
            
            # Tab 1: Optimized Sentences
            self._create_sentences_tab(spreadsheet, results)
            
            # Tab 2: Coverage Summary
            self._create_summary_tab(spreadsheet, results)
            
            # Tab 3: Missing Words
            self._create_missing_words_tab(spreadsheet, results)
            
            # Tab 4: Full Coverage Map
            self._create_coverage_map_tab(spreadsheet, results)
            
            sheet_url = spreadsheet.url
            print(f"Output sheet created: {sheet_url}")
            return sheet_url
            
        except Exception as e:
            print(f"ERROR: Failed to create output sheet: {str(e)}")
            raise
    
    def _create_sentences_tab(self, spreadsheet, results: Dict):
        """Create Optimized Sentences tab"""
        try:
            worksheet = spreadsheet.get_worksheet(0)
            worksheet.update_title("Optimized Sentences")
            
            # Headers
            headers = ["Row", "Sentence", "Words Covered", "New Words Count"]
            
            # Data rows
            rows = [headers]
            for idx, sent_data in enumerate(results['selected_sentences'], 1):
                rows.append([
                    idx,
                    sent_data['sentence'],
                    ', '.join(sent_data['words_covered']),
                    sent_data['new_words_count']
                ])
            
            # Update sheet
            worksheet.update('A1', rows)
            
            # Format headers
            worksheet.format('A1:D1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8}
            })
            
            print("  ✓ Created 'Optimized Sentences' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Sentences tab: {str(e)}")
    
    def _create_summary_tab(self, spreadsheet, results: Dict):
        """Create Coverage Summary tab"""
        try:
            worksheet = spreadsheet.add_worksheet("Coverage Summary", 20, 2)
            
            summary_data = [
                ["Metric", "Value"],
                ["Total Sentences Selected", results['total_sentences']],
                ["Total Words Covered", f"{results['words_covered']}/{results['total_words']}"],
                ["Coverage Percentage", f"{results['coverage_percent']}%"],
                ["Efficiency Score", f"{results['efficiency']} words/sentence"],
                ["Missing Words", len(results['missing_words'])],
                ["Processing Time", f"{results['processing_time']} seconds"],
                ["", ""],
                ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            worksheet.update('A1', summary_data)
            
            # Format
            worksheet.format('A1:B1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.4}
            })
            
            print("  ✓ Created 'Coverage Summary' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Summary tab: {str(e)}")
    
    def _create_missing_words_tab(self, spreadsheet, results: Dict):
        """Create Missing Words tab"""
        try:
            worksheet = spreadsheet.add_worksheet("Missing Words", 
                                                  max(len(results['missing_words']) + 5, 10), 
                                                  3)
            
            headers = ["French", "English", "Part of Speech"]
            rows = [headers]
            
            for word in results['missing_words']:
                rows.append([
                    word['french'],
                    word['english'],
                    word.get('pos', '')
                ])
            
            if not results['missing_words']:
                rows.append(["No missing words - 100% coverage!", "", ""])
            
            worksheet.update('A1', rows)
            
            # Format
            worksheet.format('A1:C1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.5, 'blue': 0.2}
            })
            
            print("  ✓ Created 'Missing Words' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Missing Words tab: {str(e)}")
    
    def _create_coverage_map_tab(self, spreadsheet, results: Dict):
        """Create Full Coverage Map tab"""
        try:
            coverage_map = results['coverage_map']
            worksheet = spreadsheet.add_worksheet("Full Coverage Map", 
                                                  len(coverage_map) + 5, 
                                                  5)
            
            headers = ["French", "English", "POS", "Found", "Times in Selected"]
            rows = [headers]
            
            for word_data in coverage_map:
                rows.append([
                    word_data['french'],
                    word_data['english'],
                    word_data['pos'],
                    "Yes" if word_data['found'] else "No",
                    word_data['sentence_count']
                ])
            
            # Update in batches for efficiency
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                start_row = i + 1
                end_row = start_row + len(batch) - 1
                worksheet.update(f'A{start_row}:E{end_row}', batch)
            
            # Format headers
            worksheet.format('A1:E1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.4, 'green': 0.2, 'blue': 0.8}
            })
            
            print("  ✓ Created 'Full Coverage Map' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Coverage Map tab: {str(e)}")
    
    def save_csv_backup(self, results: Dict, output_folder: str = 'output'):
        """Save CSV backup of results"""
        try:
            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save optimized sentences
            sentences_file = os.path.join(output_folder, f'optimized_sentences_{timestamp}.csv')
            with open(sentences_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Row', 'Sentence', 'Words Covered', 'New Words Count'])
                for idx, sent_data in enumerate(results['selected_sentences'], 1):
                    writer.writerow([
                        idx,
                        sent_data['sentence'],
                        ', '.join(sent_data['words_covered']),
                        sent_data['new_words_count']
                    ])
            
            print(f"  ✓ Saved: {sentences_file}")
            
            # Save summary
            summary_file = os.path.join(output_folder, f'summary_{timestamp}.csv')
            with open(summary_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Sentences', results['total_sentences']])
                writer.writerow(['Words Covered', f"{results['words_covered']}/{results['total_words']}"])
                writer.writerow(['Coverage %', results['coverage_percent']])
                writer.writerow(['Efficiency', results['efficiency']])
                writer.writerow(['Missing Words', len(results['missing_words'])])
                writer.writerow(['Processing Time', results['processing_time']])
            
            print(f"  ✓ Saved: {summary_file}")
            
            # Save missing words
            if results['missing_words']:
                missing_file = os.path.join(output_folder, f'missing_words_{timestamp}.csv')
                with open(missing_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['French', 'English', 'POS'])
                    for word in results['missing_words']:
                        writer.writerow([word['french'], word['english'], word.get('pos', '')])
                
                print(f"  ✓ Saved: {missing_file}")
            
            # Save coverage map
            coverage_file = os.path.join(output_folder, f'coverage_map_{timestamp}.csv')
            with open(coverage_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['French', 'English', 'POS', 'Found', 'Times in Selected'])
                for word_data in results['coverage_map']:
                    writer.writerow([
                        word_data['french'],
                        word_data['english'],
                        word_data['pos'],
                        'Yes' if word_data['found'] else 'No',
                        word_data['sentence_count']
                    ])
            
            print(f"  ✓ Saved: {coverage_file}")
            print(f"\n  All CSV backups saved to: {output_folder}/")
            
        except Exception as e:
            print(f"ERROR: Failed to save CSV backup: {str(e)}")
            raise