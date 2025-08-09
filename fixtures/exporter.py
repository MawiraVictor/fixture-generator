import pandas as pd
import json
import os

class FixtureExporter:
    def __init__(self):
        os.makedirs('output', exist_ok=True)
    
    def export(self, fixtures, formats=['csv', 'json', 'xlsx']):
        df = pd.DataFrame(fixtures['matches'])
        
        if 'csv' in formats:
            df.to_csv('output/fixtures.csv', index=False)
        
        if 'json' in formats:
            df.to_json('output/fixtures.json', orient='records', indent=2)
        
        if 'xlsx' in formats:
            df.to_excel('output/fixtures.xlsx', index=False)