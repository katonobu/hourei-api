import os
import json
import re
import requests
import xmltodict


# [法令名一覧取得API](https://laws.e-gov.go.jp/docs/law-data-basic/8529371-law-api-v1/#%E6%B3%95%E4%BB%A4%E5%90%8D%E4%B8%80%E8%A6%A7%E5%8F%96%E5%BE%97api)
class Lawlists:
    def __init__(self, category=1):
        self.low_name_ids = None
        self.bit_tbl = None
        if category in [1,2,3,4]:
            """
            1: 全法令
            2: 憲法・法律
            3: 政令・勅令
            4: 府省令・規則
            """
            url = f"https://elaws.e-gov.go.jp/api/1/lawlists/{category}"
            response = requests.get(url)
            if response.ok:
                result = xmltodict.parse(response.text)
                if "DataRoot" in result and "Result" in result['DataRoot'] and 'Code' in result['DataRoot']['Result'] and result['DataRoot']['Result']['Code'] == '0':
                    if "ApplData" in result['DataRoot'] and 'LawNameListInfo' in result['DataRoot']['ApplData']:
                        self.low_name_ids = result['DataRoot']['ApplData']['LawNameListInfo']

        bit_tbl_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"ministry_bit_tbl.json"))
        if os.path.isfile(bit_tbl_path):
            with open(bit_tbl_path) as f:
                self.bit_tbl = json.load(f)
    
    def get_LawNameListInfo_by_name(self, name_str):
        result_objs = []
        if self.low_name_ids is not None:
            for low_name_id in self.low_name_ids:
                if name_str in low_name_id['LawName']:
                    result_objs.append(low_name_id)
        return result_objs

    def get_LawNameListInfo_by_id(self, id_str):
        result_objs = []
        if self.low_name_ids is not None:
            for low_name_id in self.low_name_ids:
                if id_str == low_name_id['LawId']:
                    result_objs.append(low_name_id)
        return result_objs
    
    def analyse_id(self, id_str):
        #https://laws.e-gov.go.jp/docs/law-data-basic/607318a-lawtypes-and-lawid/#lawid
        result_obj = {}
        if re.match(r"[1-5][0-9]{2}", id_str):
            nengo_id = int(id_str[0], 10)
            result_obj.update({'nengo':["","明治","大正","昭和","平成","令和"][nengo_id]})
            nen = int(id_str[1:3], 10)
            result_obj.update({'nen':nen})
            year = ["", 1867, 1911,1925,1988,2018][nengo_id] + nen
            result_obj.update({'year':year})

            syubetsu = "unknown"
            if id_str[3:] == 'CONSTITUTION':
                syubetsu = "憲法"
            else:
                # 号番号
                result_obj.update({'go_number':int(id_str[12:], 10)})
                type_obj_2letters = {
                    'AC':"法律",
                    'CO':"政令",
                    'IO':"勅令",
                    'DF':"太政官布告",
                    'DT':"太政官達",
                    'DH':"太政官布達"
                }
                if id_str[3:5] in type_obj_2letters:
                    syubetsu = type_obj_2letters.get(id_str[3:5])
                    if syubetsu == "法律":
                        houritsu_type_tbl = {
                            '0000000':"閣法",
                            '1000000':"衆議院議員立法",
                            '0100000':"参議院議員立法"
                        }
                        if id_str[5:12] in houritsu_type_tbl:
                            # 閣法と議員立法の区別
                            result_obj.update({'houritsu_type':houritsu_type_tbl[id_str[5:12]]})
                        else:
                            print(id_str)
                    else:
                        kouryoku_tbl = {
                            '0000000':"政令",
                            '1000000':"法律"
                        }
                        if id_str[5:12] in kouryoku_tbl:
                            # 効力を表す種別コード
                            result_obj.update({'kouryoku_type':kouryoku_tbl[id_str[5:12]]})
                        else:
                            print(id_str)

                elif re.match(r"M[1-6]", id_str[3:5]):
                    syubetsu = "府省令"
                    bit_tbl = self.bit_tbl[id_str[3:5]]
                    bits_int = int(id_str[5:12], 16)
                    ministries = []
                    for bit in range(28):
                        if (2**bit & bits_int) != 0:
                            ministries.append(bit_tbl[bit])
                    # 府省令・委員会
                    result_obj.update({'ministries':ministries})

                elif id_str[3] == 'R':
                    if id_str[4:7] == "JNJ":
                        syubetsu = "人事院規則"
                        # 号番号 対象外
                        result_obj.pop('go_number')
                        result_obj.update({
                            # 規則の分類
                            'rule_type':int(id_str[7:9], 10),
                            # 規則の分類中の連番
                            'rule_type_seq_num':int(id_str[9:12], 10),
                            # 改正規則の連番 
                            'update_seq_num':int(id_str[12:], 10)
                        })
                    elif id_str[4:7] == "PMD":
                        syubetsu = "内閣総理大臣決定"
                        # 号番号 対象外
                        result_obj.pop('go_number')
                        result_obj.update({
                            # 決定月 
                            'decided_month':int(id_str[7:9], 10),
                            # 決定日 
                            'decided_day':int(id_str[9:11], 10),
                            # 同一決定日内の連番
                            'seq_num':int(id_str[11:], 10)
                        })
                    else:
                        iin_tbl = {
                            '00000001':"会計検査院規則",
                            '00000002':"海上保安庁令",
                            '00000003':"日本学術会議規則",
                            '00000004':"土地調整委員会規則",
                            '00000005':"金融再生委員会規則",
                            '00000006':"首都圏整備委員会規則",
                            '00000007':"地方財政委員会規則",
                            '00000008':"司法試験管理委員会規則",
                            '00000009':"公認会計士管理委員会規則",
                            '00000010':"外資委員会規則",
                            '00000011':"文化財保護委員会規則",
                            '00000012':"日本ユネスコ国内委員会規則",
                            '00000013':"最高裁判所規則",
                            '00000014':"衆議院規則",
                            '00000015':"参議院規則",
                            '00000016':"船員中央労働委員会規則",
                            '00000017':"司法試験管理委員会規則",
                            '00000018':"電波監理委員会規則",
                            '00000019':"カジノ管理委員会規則"
                        }
                        if id_str[4:12] in iin_tbl:
                            # 会計検査院規則、行政機関の規則（人事院規則を除く）及びその他機関の規則
                            syubetsu = "会計検査院規則、行政機関の規則（人事院規則を除く）及びその他機関の規則"
                            # 対象機関
                            result_obj.update({'kikan':iin_tbl.get(id_str[4:12])})
                        else:
                            print(id_str)
                else:
                    print(id_str)
            result_obj.update({'syubetsu':syubetsu})
        else:
            print(f're.match(r"[1-5][0-9]{2}", id_str):{id_str}')

        return result_obj
    
if __name__ == "__main__":
    name_ids = Lawlists()
#    search_result = name_ids.get_LawNameListInfo_by_name("建物の区分所有等に関する法律")
#    print(json.dumps(search_result, indent=2, ensure_ascii=False))

#    search_result = name_ids.get_LawNameListInfo_by_id("337AC0000000069")
#    print(json.dumps(search_result, indent=2, ensure_ascii=False))

    results = []
    for name_id in name_ids.low_name_ids:
        analyse_result = name_ids.analyse_id(name_id['LawId'])
        if 'syubetsu' not in analyse_result:
            print(json.dumps(name_id, indent=2, ensure_ascii=False))
        elif 'syubetsu' in analyse_result and analyse_result['syubetsu'] == "unknown":
            print(json.dumps(name_id, indent=2, ensure_ascii=False))
        else:
            name_id.update(analyse_result)
            results.append(name_id)
            if 'PromulgationDate' in name_id and int(name_id['PromulgationDate'][:4], 10) != analyse_result['year']:
                print(json.dumps(name_id, indent=2, ensure_ascii=False))
    with open("result2.json","w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

#    print(json.dumps(name_ids.analyse_id("337AC0000000069"), indent=2, ensure_ascii=False))