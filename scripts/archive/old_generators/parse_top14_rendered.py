import json
import os
import re
import time
from player_utils import PlayerDataProcessor

# top14 などの JS レンダリングが必要なページは read_url_content を通じて取得し、
# その結果（Markdown or HTML）をパースする戦略に切り替える。
# ※スクリプト単体で動かす場合は Selenium 等が必要なため、
# ここでは「取得済みデータ」を処理するか、Antigravity 自身のツール利用を前提とする。

def parse_top14_player_markdown(md_content, url):
    """read_url_content の出力をパース"""
    info = {
        "name": "Unknown",
        "url": url,
        "age": None,
        "height": None,
        "weight": None,
        "caps": None,
        "career": []
    }
    
    # 名前 (H1)
    name_match = re.search(r'# (.*)', md_content)
    if name_match: info["name"] = name_match.group(1).strip()
    
    # 年齢/身長/体重 (テキストから)
    age_match = re.search(r'(\d+)\s*ans', md_content)
    if age_match: info["age"] = int(age_match.group(1))
    
    height_match = re.search(r'(\d+)\s*cm', md_content)
    if height_match: info["height"] = int(height_match.group(1))
    
    weight_match = re.search(r'(\d+)\s*kg', md_content)
    if weight_match: info["weight"] = int(weight_match.group(1))
    
    # キャリア履歴 (表形式 or リスト)
    # Markdown 内の表 [2024-2025 | Aviron Bayonnais] 的なものを探す
    career_lines = re.findall(r'\|\s*(\d{4}[-\d]*)\s*\|\s*([^|]+)\s*\|', md_content)
    for year, team in career_lines:
        info["career"].append({"year": year.strip(), "team": team.strip()})
        
    return info

# 本スクリプトは Antigravity が read_url_content で取得した内容を流し込む用途
if __name__ == "__main__":
    # テスト用ダミー
    print("This script is intended to be called with content from read_url_content.")
