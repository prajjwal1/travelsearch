import json

def get_jsonl():
    with open('travel.json', 'r') as f:
        json_data = json.load(f)

    with open('travel.jsonl', 'w') as outfile:
        for entry in json_data:
            json.dump(entry, outfile)
            outfile.write('\n')

get_jsonl()
