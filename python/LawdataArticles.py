import os
import json
import base64
import tempfile
import requests
import xmltodict
import datetime
import shutil

class LawdataArticles:
    @classmethod
    def extract_base64encoded_zip(cls, base64_encoded_str, extract_dir_path_name = None):
        with tempfile.TemporaryDirectory() as dname:
            zip_file_name_path = os.path.join(dname, "attached.zip")
            with open(zip_file_name_path, "wb") as f:
                f.write(base64.b64decode(base64_encoded_str))
            if extract_dir_path_name is None:
                extract_dir_path_name = os.path.join(os.path.dirname(__file__),f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_extract")
            os.makedirs(extract_dir_path_name, exist_ok=True)
            shutil.unpack_archive(zip_file_name_path, extract_dir_path_name)
        return extract_dir_path_name
    
    @classmethod
    def analyse_response(cls, response):
        result = None
        extract_dir_path_name = None
        if response.ok:
            result = xmltodict.parse(response.text)
            if "DataRoot" in result and "Result" in result['DataRoot'] and 'Code' in result['DataRoot']['Result'] and result['DataRoot']['Result']['Code'] == '0':
                if "ApplData" in result['DataRoot']:
                    if "ImageData" in result['DataRoot']['ApplData']:
                        image_data = result['DataRoot']['ApplData'].pop("ImageData")
                        extract_dir_path_name = cls.extract_base64encoded_zip(image_data)
        return {'result_obj':result, 'extract_dir':extract_dir_path_name}


    # https://elaws.e-gov.go.jp/api/1/lawdata/{法令番号又は法令ID}
    @classmethod
    def get_by_id(cls, law_id):
        result = None
        url = f"https://elaws.e-gov.go.jp/api/1/lawdata/{law_id}"
        return cls.analyse_response(requests.get(url))
    
    # https://elaws.e-gov.go.jp/api/1/articles;lawNum={法令番号};lawId={法令ID};article={条};paragraph={項};appdxTable={別表}
    @classmethod
    def get_by_id_article(cls, law_id, article):
        url = f"https://elaws.e-gov.go.jp/api/1/articles;lawId={law_id};article={article}"
        return cls.analyse_response(requests.get(url))

    @classmethod
    def get_by_id_article_paragraph(cls, law_id, article, paragraph):
        url = f"https://elaws.e-gov.go.jp/api/1/articles;lawId={law_id};article={article};paragraph={paragraph}"
        return cls.analyse_response(requests.get(url))

    @classmethod
    def get_by_id_appendix_table(cls, law_id, appendix_table):
        pass

if __name__ == "__main__":
#    print(json.dumps(LawdataArticles.get_by_id("411AC0000000127"), indent=2, ensure_ascii=False))
    print(json.dumps(LawdataArticles.get_by_id_article("411AC0000000127", 1), indent=2, ensure_ascii=False))
    print(json.dumps(LawdataArticles.get_by_id_article_paragraph("411AC0000000127", 1, 2), indent=2, ensure_ascii=False))
#    LawdataArticles.get_by_id_article("411AC0000000127", 1)
