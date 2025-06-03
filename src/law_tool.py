import requests
import datetime
import json
import urllib.parse
from typing import Dict, Optional, List, Tuple
from law_search import lawSearch

from pathlib import Path
import pdfplumber
from io import BytesIO
import logging
logging.getLogger('').setLevel(logging.CRITICAL)

class lawPDF:
    def __init__(self):
        self.lawSerach = lawSearch()
    
    def _transform_string(self,
                          input_string: str) -> str:
        first_part = input_string[:8]
        transform_part = first_part[:-2] + first_part[-2:]
        return transform_part
    
    def _load_content(self,
                      url: str,
                      form_data: Dict):
        response = requests.post(url, data=form_data)
        response.raise_for_status()
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def _download_file(self,
                       url: str,
                       form_data: Dict,
                       file_path: str,
                       file_name: str):
        response = requests.post(url, data=form_data)
        response.raise_for_status()
        file_name = Path(file_path) / file_name
        with open(file_name, 'wb') as file:
            file.write(response.content)

    def _get_download_parameter(self,
                                response: requests.models.Response) -> Tuple[List, List]:
        jonum_list = []
        output_list = []
        text = response.text
        datas = json.loads(text)
        for data in datas:
            joYn = data['joYn']
            nwYn = data['nwYn']
            output_No = data['chapNo']
            if joYn == "Y" and nwYn == "Y":
                jonum = data['joLink'].split(':')
                joLink = jonum[0].zfill(4) + ":" + jonum[1].zfill(2)
                joLink = urllib.parse.quote(string=joLink)
            elif joYn == "Y" and nwYn == "N":
                jonum = data['joLink'].split(':')
                joLink = jonum[0].zfill(4) + ":" + jonum[1].zfill(2)
                joLink = urllib.parse.quote(string=joLink)
                joLink += "+YE"
            elif joYn == "N" and nwYn == "Y":
                joLink = data['chapNo']
                output_No = self._transform_string(input_string=data['chapNo']) + "JO"
            elif joYn == "N" and nwYn == "N":
                print("all NaN")
            jonum_list.append(joLink)
            output_list.append(output_No)
        return jonum_list, output_list
    
    def _setting_paramter(self,
                          yyyymmdd: int,
                          code: int,
                          chrClsCd: str,
                          now: datetime.datetime.timestamp):
        base_api_url = f"https://www.law.go.kr/LSW/joListRInc.do"

        param1 = {
            "lsiSeq": code,
            "mode": 99,
            "chapNo": 1,
            "nwYn": 1,
            "efYd": yyyymmdd,
            "gubun": "save",
            "ancYnChk": 0,
            "timeStamp": now,
        }
        response = requests.post(url=base_api_url,
                                data=param1)
        response.raise_for_status()
        
        jonum_list, output_list = self._get_download_parameter(response=response)
        
        root_url = "https://www.law.go.kr/LSW/lsPdfPrint.do?ancYnChk=0"
        root_url += f"&lsiSeq={code}&chrClsCd={chrClsCd}&outPutTitleYn=&joAllCheck=&onlyEfYd=&efLsGubun=&efDvPop=&nwJoYnInfo="
        root_url += f"&arSeqs=%2C%2C10534591%23&mokChaChk=N&bylChaChk=N"
        root_url += f"&arIds=check_outPut_10534591&bylAllSeq=&efYd={yyyymmdd}"
        root_url += f"&efGubun=&test1=on&joEfOutPutYn=on"
        
        for idx, (jo, out) in enumerate(zip(jonum_list, output_list)):
            jo_params = f"&joNo={jo}"
            if "JO" in out:
                output_params = f"&outPut_{out}=outPut_{out[:-2]}TOP{idx}OutPutDIV"
            else:
                output_params = f"&outPut_{out}=outPut_{out}JO{idx}"
            root_url += jo_params + output_params
        root_url += f"&coverDpYn=1&lsNmFont=goThic&lsJoSize=10&lsJoFont=smyoungjo&spaceCls=2&fileType=pdf"
        
        return root_url
    
    async def download_pdf(self,
                           query: str,
                           output_path: str):
        
        base_pdf_url = "https://www.law.go.kr/LSW/lsPdfPrint.do"

        laws = await self.lawSerach.search(query=query)
        for title, values in laws.items():
            # 파일 디렉 생성
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            
            yyyymmdd = values['시행일자']
            code = values['code']
            title = title
            chrClsCd = "010202"
            now = int(datetime.datetime.now().timestamp())
            
            url = self._setting_paramter(yyyymmdd=yyyymmdd,
                                               code=code,
                                               chrClsCd=chrClsCd,
                                               now=now)
            parsed_url = urllib.parse.urlparse(url)
            form_data = urllib.parse.parse_qs(parsed_url.query)
            self._download_file(url=base_pdf_url,
                                form_data=form_data,
                                file_path=output_path,
                                file_name=f"{title}.pdf")
            
    async def read_content(self,
                           query: str):
        
        base_pdf_url = "https://www.law.go.kr/LSW/lsPdfPrint.do"

        laws = await self.lawSerach.search(query=query)
        for title, values in laws.items():
            yyyymmdd = values['시행일자']
            code = values['code']
            title = title
            chrClsCd = "010202"
            now = int(datetime.datetime.now().timestamp())
            
            url = self._setting_paramter(yyyymmdd=yyyymmdd,
                                               code=code,
                                               chrClsCd=chrClsCd,
                                               now=now)
            parsed_url = urllib.parse.urlparse(url)
            form_data = urllib.parse.parse_qs(parsed_url.query)
            text = self._load_content(url=base_pdf_url,
                                      form_data=form_data)
            return text
            
    