"""
Enhanced Google Sheets Handler with Rich Formatting
Auto-detects credentials, supports charts and advanced formatting
"""

import os
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import List, Dict
from core.config import OptimizerConfig, SHEETS_SCOPES, COLORS


class EnhancedSheetsHandler:
    """Enhanced Sheets Handler with auto-detect auth and rich formatting"""
    
    def __init__(self, config: OptimizerConfig = None):
        self.config = config or OptimizerConfig()
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Auto-detect and authenticate with Google Sheets API"""
        try:
            # Resolve to absolute path
            if not os.path.isabs(self.config.credentials_path):
                cred_path = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', self.config.credentials_path
                ))
            else:
                cred_path = self.config.credentials_path
            
            if not os.path.isabs(self.config.token_path):
                token_path = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', self.config.token_path
                ))
            else:
                token_path = self.config.token_path
            
            print(f"Authenticating with Google Sheets API...")
            
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Credentials file not found: {cred_path}")
            
            # Detect credential type
            with open(cred_path, "r", encoding="utf-8") as f:
                cred_data = json.load(f)
            
            if "type" in cred_data and cred_data["type"] == "service_account":
                # Service Account
                print("  Using Service Account credentials...")
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    cred_path, SHEETS_SCOPES
                )
                self.client = gspread.authorize(creds)
                print("✓ Authentication successful (Service Account)")
                
            elif "installed" in cred_data and "client_id" in cred_data["installed"]:
                # OAuth User
                print("  Using OAuth user credentials...")
                self.client = gspread.oauth(
                    credentials_filename=cred_path,
                    authorized_user_filename=token_path
                )
                print("✓ Authentication successful (OAuth)")
                
            else:
                raise ValueError("Unrecognized credentials format")
                
        except Exception as e:
            print(f"✗ Authentication failed: {str(e)}")
            raise
    
    def load_word_list(self, sheet_url: str) -> List[Dict]:
        """Load word list from Google Sheets"""
        try:
            print(f"Loading word list from Google Sheets...")
            
            sheet = self.client.open_by_url(sheet_url)
            worksheet = sheet.get_worksheet(0)
            data = worksheet.get_all_values()
            
            if not data:
                raise ValueError("Sheet is empty")
            
            # Parse headers
            headers = data[0]
            word_list = []
            
            for row in data[1:]:
                if len(row) >= 2 and row[0].strip():
                    word_list.append({
                        'french': row[0].strip(),
                        'english': row[1].strip() if len(row) > 1 else '',
                        'pos': row[2].strip() if len(row) > 2 else ''
                    })
            
            print(f"✓ Loaded {len(word_list)} words")
            return word_list
            
        except Exception as e:
            print(f"✗ Failed to load word list: {str(e)}")
            raise
    
    def create_output_sheet(self, results, word_list: List[Dict]) -> str:
        """Create beautifully formatted Google Sheet with results"""
        try:
            print("Creating output Google Sheet...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sheet_name = f"French_Vocab_Optimization_{timestamp}"
            spreadsheet = self.client.create(sheet_name)
            
            print(f"  Created: {sheet_name}")
            
            # Create tabs
            self._create_sentences_tab(spreadsheet, results)
            self._create_summary_tab(spreadsheet, results)
            self._create_missing_words_tab(spreadsheet, results)
            self._create_coverage_map_tab(spreadsheet, results)
            self._create_statistics_tab(spreadsheet, results)
            
            sheet_url = spreadsheet.url
            print(f"✓ Output sheet created: {sheet_url}")
            return sheet_url
            
        except Exception as e:
            print(f"✗ Failed to create output sheet: {str(e)}")
            raise
    
    def _create_sentences_tab(self, spreadsheet, results):
        """Create Optimized Sentences tab with color coding"""
        try:
            worksheet = spreadsheet.get_worksheet(0)
            worksheet.update_title("Optimized Sentences")
            
            # Headers
            headers = ["#", "Sentence", "Words Covered", "New Words", "Total Words", "Efficiency"]
            rows = [headers]
            
            # Data rows with efficiency calculation
            for idx, sent_data in enumerate(results.selected_sentences, 1):
                efficiency = sent_data['new_words_count'] / max(sent_data.get('total_words', 1), 1)
                rows.append([
                    idx,
                    sent_data['sentence'],
                    ', '.join(sent_data['words_covered'][:10]) + ('...' if len(sent_data['words_covered']) > 10 else ''),
                    sent_data['new_words_count'],
                    sent_data.get('total_words', sent_data['new_words_count']),
                    round(efficiency, 2)
                ])
            
            # Update sheet
            worksheet.update('A1', rows)
            
            # Format header
            worksheet.format('A1:F1', {
                'textFormat': {'bold': True, 'fontSize': 11},
                'backgroundColor': COLORS['header'],
                'horizontalAlignment': 'CENTER'
            })
            
            # Freeze header row
            worksheet.freeze(rows=1)
            
            # Color code by efficiency
            for idx, sent_data in enumerate(results.selected_sentences, 2):
                efficiency = sent_data['new_words_count'] / max(sent_data.get('total_words', 1), 1)
                
                if efficiency > 0.6:  # High efficiency
                    color = COLORS['high_efficiency']
                elif efficiency > 0.3:  # Medium
                    color = COLORS['medium_efficiency']
                else:  # Low
                    color = COLORS['low_efficiency']
                
                worksheet.format(f'F{idx}', {
                    'backgroundColor': color,
                    'textFormat': {'bold': True}
                })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, 5)
            
            print("  ✓ Created 'Optimized Sentences' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Sentences tab: {str(e)}")
    
    def _create_summary_tab(self, spreadsheet, results):
        """Create Coverage Summary with metrics"""
        try:
            worksheet = spreadsheet.add_worksheet("Summary", 25, 3)
            
            summary_data = [
                ["📊 Optimization Summary", "", ""],
                ["", "", ""],
                ["Metric", "Value", "Details"],
                ["Total Sentences", results.total_sentences, f"Target: {self.config.max_sentences}"],
                ["Words Covered", f"{results.words_covered}/{results.total_words}", f"{results.coverage_percent}%"],
                ["Coverage Rate", f"{results.coverage_percent}%", "✓ Excellent" if results.coverage_percent >= 95 else "⚠ Review"],
                ["Efficiency", f"{results.efficiency}", "words per sentence"],
                ["Missing Words", len(results.missing_words), "See Missing Words tab"],
                ["Algorithm Used", results.algorithm_used.title(), f"{results.iterations} iterations"],
                ["Processing Time", f"{results.processing_time}s", ""],
                ["", "", ""],
                ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""],
                ["", "", ""],
                ["📈 Performance Metrics", "", ""],
                ["Average Coverage/Sentence", round(results.efficiency, 2), "words"],
                ["Sentences Under Target", 
                 "Yes ✓" if results.total_sentences <= self.config.max_sentences else f"Over by {results.total_sentences - self.config.max_sentences}",
                 ""],
                ["Coverage Goal Met", 
                 "Yes ✓" if results.coverage_percent >= self.config.min_coverage_percent else "No ✗",
                 f"Goal: {self.config.min_coverage_percent}%"]
            ]
            
            worksheet.update('A1', summary_data)
            
            # Format title
            worksheet.format('A1:C1', {
                'textFormat': {'bold': True, 'fontSize': 14},
                'backgroundColor': COLORS['summary_header'],
                'horizontalAlignment': 'CENTER'
            })
            
            # Format headers
            worksheet.format('A3:C3', {
                'textFormat': {'bold': True},
                'backgroundColor': COLORS['summary_header']
            })
            
            worksheet.format('A14:C14', {
                'textFormat': {'bold': True, 'fontSize': 12},
                'backgroundColor': COLORS['summary_header']
            })
            
            # Merge title cell
            worksheet.merge_cells('A1:C1')
            worksheet.merge_cells('A14:C14')
            
            # Auto-resize
            worksheet.columns_auto_resize(0, 2)
            
            print("  ✓ Created 'Summary' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Summary tab: {str(e)}")
    
    def _create_missing_words_tab(self, spreadsheet, results):
        """Create Missing Words tab"""
        try:
            worksheet = spreadsheet.add_worksheet(
                "Missing Words",
                max(len(results.missing_words) + 10, 10),
                4
            )
            
            headers = ["French", "English", "POS", "Suggestion"]
            rows = [headers]
            
            if results.missing_words:
                for word in results.missing_words:
                    rows.append([
                        word['french'],
                        word['english'],
                        word.get('pos', ''),
                        "Add more source sentences"
                    ])
            else:
                rows.append(["🎉 Perfect! All words found!", "", "", "100% coverage achieved"])
            
            worksheet.update('A1', rows)
            
            # Format
            worksheet.format('A1:D1', {
                'textFormat': {'bold': True, 'fontSize': 11},
                'backgroundColor': COLORS['missing_header'],
                'horizontalAlignment': 'CENTER'
            })
            
            worksheet.freeze(rows=1)
            worksheet.columns_auto_resize(0, 3)
            
            print("  ✓ Created 'Missing Words' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Missing Words tab: {str(e)}")
    
    def _create_coverage_map_tab(self, spreadsheet, results):
        """Create Full Coverage Map"""
        try:
            worksheet = spreadsheet.add_worksheet(
                "Coverage Map",
                len(results.coverage_map) + 10,
                6
            )
            
            headers = ["French", "English", "POS", "Found", "Occurrences", "Sentences"]
            rows = [headers]
            
            for word_data in results.coverage_map:
                rows.append([
                    word_data['french'],
                    word_data['english'],
                    word_data['pos'],
                    "✓" if word_data['found'] else "✗",
                    word_data['sentence_count'],
                    ', '.join(map(str, word_data.get('sentence_indices', [])[:5]))
                ])
            
            # Batch update for efficiency
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                start_row = i + 1
                worksheet.update(f'A{start_row}', batch)
            
            # Format
            worksheet.format('A1:F1', {
                'textFormat': {'bold': True},
                'backgroundColor': COLORS['coverage_header']
            })
            
            worksheet.freeze(rows=1)
            
            print("  ✓ Created 'Coverage Map' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Coverage Map tab: {str(e)}")
    
    def _create_statistics_tab(self, spreadsheet, results):
        """Create detailed statistics tab"""
        try:
            worksheet = spreadsheet.add_worksheet("Statistics", 30, 3)
            
            # Calculate statistics
            efficiencies = [s['new_words_count'] / max(s.get('total_words', 1), 1) 
                          for s in results.selected_sentences]
            avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0
            max_efficiency = max(efficiencies) if efficiencies else 0
            min_efficiency = min(efficiencies) if efficiencies else 0
            
            stats_data = [
                ["📈 Detailed Statistics", "", ""],
                ["", "", ""],
                ["Sentence Statistics", "", ""],
                ["Total Sentences Selected", results.total_sentences, ""],
                ["Average Words/Sentence", round(avg_efficiency * 10, 2), ""],
                ["Most Efficient Sentence", round(max_efficiency, 2), "efficiency score"],
                ["Least Efficient Sentence", round(min_efficiency, 2), "efficiency score"],
                ["", "", ""],
                ["Word Statistics", "", ""],
                ["Total Words in List", results.total_words, ""],
                ["Words Found", results.words_covered, ""],
                ["Words Missing", len(results.missing_words), ""],
                ["Coverage Rate", f"{results.coverage_percent}%", ""],
                ["", "", ""],
                ["Efficiency Breakdown", "", ""],
                ["High Efficiency (>60%)", sum(1 for e in efficiencies if e > 0.6), "sentences"],
                ["Medium Efficiency (30-60%)", sum(1 for e in efficiencies if 0.3 <= e <= 0.6), "sentences"],
                ["Low Efficiency (<30%)", sum(1 for e in efficiencies if e < 0.3), "sentences"],
                ["", "", ""],
                ["Performance", "", ""],
                ["Algorithm", results.algorithm_used.title(), ""],
                ["Iterations", results.iterations, ""],
                ["Processing Time", f"{results.processing_time}s", ""],
                ["Cache Enabled", "Yes" if self.config.cache_enabled else "No", ""],
                ["Parallel Processing", "Yes" if self.config.parallel_processing else "No", ""]
            ]
            
            worksheet.update('A1', stats_data)
            
            # Format headers
            worksheet.format('A1:C1', {
                'textFormat': {'bold': True, 'fontSize': 14},
                'backgroundColor': COLORS['header'],
                'horizontalAlignment': 'CENTER'
            })
            worksheet.merge_cells('A1:C1')
            
            for row in [3, 9, 15, 20]:
                worksheet.format(f'A{row}:C{row}', {
                    'textFormat': {'bold': True, 'fontSize': 12},
                    'backgroundColor': COLORS['summary_header']
                })
            
            worksheet.columns_auto_resize(0, 2)
            
            print("  ✓ Created 'Statistics' tab")
            
        except Exception as e:
            print(f"  ✗ Error creating Statistics tab: {str(e)}")
    
    def save_csv_backup(self, results, output_folder: str = None):
        """Save CSV backup files"""
        try:
            output_folder = output_folder or self.config.output_folder
            os.makedirs(output_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sentences
            sentences_file = os.path.join(output_folder, f'optimized_sentences_{timestamp}.csv')
            with open(sentences_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Row', 'Sentence', 'Words Covered', 'New Words', 'Total Words'])
                for idx, sent_data in enumerate(results.selected_sentences, 1):
                    writer.writerow([
                        idx,
                        sent_data['sentence'],
                        ', '.join(sent_data['words_covered']),
                        sent_data['new_words_count'],
                        sent_data.get('total_words', sent_data['new_words_count'])
                    ])
            print(f"  ✓ {sentences_file}")
            
            # Summary
            summary_file = os.path.join(output_folder, f'summary_{timestamp}.csv')
            with open(summary_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Sentences', results.total_sentences])
                writer.writerow(['Words Covered', f"{results.words_covered}/{results.total_words}"])
                writer.writerow(['Coverage %', results.coverage_percent])
                writer.writerow(['Efficiency', results.efficiency])
                writer.writerow(['Algorithm', results.algorithm_used])
                writer.writerow(['Processing Time', results.processing_time])
            print(f"  ✓ {summary_file}")
            
            # Missing words
            if results.missing_words:
                missing_file = os.path.join(output_folder, f'missing_words_{timestamp}.csv')
                with open(missing_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['French', 'English', 'POS'])
                    for word in results.missing_words:
                        writer.writerow([word['french'], word['english'], word.get('pos', '')])
                print(f"  ✓ {missing_file}")
            
            # Coverage map
            coverage_file = os.path.join(output_folder, f'coverage_map_{timestamp}.csv')
            with open(coverage_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['French', 'English', 'POS', 'Found', 'Count'])
                for word_data in results.coverage_map:
                    writer.writerow([
                        word_data['french'],
                        word_data['english'],
                        word_data['pos'],
                        'Yes' if word_data['found'] else 'No',
                        word_data['sentence_count']
                    ])
            print(f"  ✓ {coverage_file}")
            
            print(f"✓ CSV backups saved to: {output_folder}/")
            
        except Exception as e:
            print(f"✗ Failed to save CSV backup: {str(e)}")
            raise
