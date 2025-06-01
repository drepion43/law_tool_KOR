import requests
import xml.etree.ElementTree as ET
from typing import Dict

class lawSearch:
    def __init__(self):
        pass
        
    async def search(self,
                     query: str) -> Dict:
        
        base_url = "https://www.law.go.kr"
        api_url = "http://www.law.go.kr/DRF/lawSearch.do"

        params = {
            'OC': 'drepion43',
            'types': 'XML',
            'target': 'law',
            'query': query
        }
        response = requests.post(api_url, data=params)
        response.raise_for_status()
        text = response.text
        root = ET.fromstring(text)
        law_dict = dict()
        for law in root.findall('law'):
            isCurrent = law.find('현행연혁코드').text
            name = law.find('법령명한글').text.strip()
            date = law.find('시행일자').text
            code = law.find('법령일련번호').text
            link = law.find('법령상세링크').text
            law_dict[name] = {"시행일자": int(date), "현행여부": isCurrent, "link":base_url + link, "code": int(code)}
        
        return law_dict
