import json

with open('C:/Users/wenyu/moodring/data/snapshot_latest.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

with open('C:/Users/wenyu/moodring/data/retail_commentary.txt', 'r', encoding='utf-8') as f:
    d['retail_sentiment_commentary'] = f.read().strip()

with open('C:/Users/wenyu/moodring/data/snapshot_latest.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print('Injected retail_sentiment_commentary into snapshot_latest.json')
