import os
import json

file_name_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ministry_tbl.txt"))
with open(file_name_path) as f:
    is_valid = False
    result = []
    sub_result = []
    index = 0
    for line in f.readlines():
        if line.startswith("#--"):
            index += 1
            reversed_list = list(reversed(sub_result))
            for _ in range(28 - len(reversed_list)):
                reversed_list.append("（空き）")
            result.append(reversed_list)
            sub_result=[]
        elif line.startswith('"""'):
            is_valid = not is_valid
        else:
            sub_result.append(line.strip())


#print(json.dumps(result, indent=2, ensure_ascii=False))

for bit in range(28):
    bit_strings = []
    for m in range(index):
        bit_strings.append(result[m][bit])
    print(f"bit:{bit+1},{json.dumps(bit_strings, indent=2, ensure_ascii=False)}")

print("--------------")
file_name_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","ministry_bit_tbl.json"))
with open(file_name_path,"w") as f:
    json.dump({
        f"M{m+1}":result[m] for m in range(index)
    }, f, indent=2, ensure_ascii=False)
