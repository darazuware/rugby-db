import pandas as pd
import numpy as np
import os
import re
import csv
from io import StringIO

INPUT_CSV = 'data_sources/final_master_data_v26_mlr_integrated.csv'
OUTPUT_CSV = 'data_sources/final_master_data_v27_normalized.csv'

def normalize_csv():
    print(f"Normalizing {INPUT_CSV} with multi-section header support...")
    
    sections = []
    current_section_lines = []
    
    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
        
    for line in lines:
        if ('英語名' in line or 'Player_ID' in line or 'Full_Name' in line) and len(line.split(',')) > 10:
            if current_section_lines:
                sections.append("".join(current_section_lines))
            current_section_lines = [line]
        else:
            current_section_lines.append(line)
            
    if current_section_lines:
        sections.append("".join(current_section_lines))
        
    print(f"Detected {len(sections)} data sections.")
    
    canonical_header = [
        'Full_Name', 'Name_JA', 'Position', 'Current_Team', 'League', 
        'Height', 'Weight', 'Birth_Date', 'Age', 'Nationality', 
        'Representative_Caps', 'Scraped_Url', 'Player_ID'
    ]
    
    all_dfs = []
    
    cols_map = {
        'Full_Name': ['Full_Name', '英語名', 'name_en', 'Name_en', 'First_Name', 'name', '選手名'],
        'Name_JA': ['選手名_カタカナ', '選手名', 'name_ja', 'title', 'Title'],
        'Position': ['Position', 'ポジション', 'position'],
        'Current_Team': ['Current_Team', '所属チーム', 'team', 'Team', 'current_team', '所属'],
        'League': ['League', 'リーグ', 'league'],
        'Height': ['Height', '身長', 'height'],
        'Weight': ['Weight', '体重', 'weight'],
        'Birth_Date': ['Birth_Date', '生年月日', 'birth_date', 'birthday'],
        'Age': ['Age', '年齢', 'age'],
        'Nationality': ['Nationality', '国籍', 'nationality'],
        'Representative_Caps': ['Representative_Caps', '代表キャップ数', 'International_Caps', 'caps', 'Caps'],
        'Scraped_Url': ['Scraped_Url', 'URL', 'scraped_url', 'Scraped_url']
    }
    
    for i, section_str in enumerate(sections):
        try:
            df_sec = pd.read_csv(StringIO(section_str), low_memory=False)
            df_sec.columns = [str(c).strip() for c in df_sec.columns]
            
            new_df = pd.DataFrame(index=df_sec.index)
            for final_col, aliases in cols_map.items():
                existing_aliases = [a for a in aliases if a in df_sec.columns]
                if existing_aliases:
                    combined = df_sec[existing_aliases[0]].astype(str).replace(['', 'nan', 'None', '.'], np.nan)
                    for alias in existing_aliases[1:]:
                        combined = combined.fillna(df_sec[alias].astype(str).replace(['', 'nan', 'None', '.'], np.nan))
                    new_df[final_col] = combined
                else:
                    new_df[final_col] = np.nan
            
            all_dfs.append(new_df)
            print(f"Section {i+1}: Processed {len(new_df)} rows.")
        except Exception as e:
            print(f"Error processing section {i+1}: {e}")

    if not all_dfs:
        print("No data extracted.")
        return

    full_df = pd.concat(all_dfs, ignore_index=True)
    
    # 型正規化
    for col in ['Height', 'Weight', 'Age']:
        full_df[col] = pd.to_numeric(full_df[col].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce').fillna(0)

    # 重複排除
    initial_count = len(full_df)
    full_df = full_df.dropna(subset=['Full_Name'])
    full_df = full_df[full_df['Full_Name'] != ""]
    
    full_df['Scraped_Url'] = full_df['Scraped_Url'].replace(['', 'nan'], np.nan)
    full_df = full_df.sort_values(by=['Scraped_Url', 'Full_Name'], ascending=False)
    full_df = full_df.drop_duplicates(subset=['Scraped_Url'], keep='first')
    
    mask_no_url = full_df['Scraped_Url'].isna()
    unique_no_url = full_df[mask_no_url].drop_duplicates(subset=['Full_Name', 'Current_Team'], keep='first')
    full_df = pd.concat([full_df[~mask_no_url], unique_no_url])
    
    print(f"Total: Extracted {initial_count} -> Deduplicated {len(full_df)} players.")
    full_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"Final normalized CSV saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    normalize_csv()
