"""
从中国外汇交易中心拉美元/人民币中间价，写入 docs/rate.json 供前端 fetch。
GitHub Actions 每天 09:30 北京时间自动运行。
"""
import json, os, urllib.request, ssl, datetime

ssl._create_default_https_context = ssl._create_unverified_context

URL = 'https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def fetch():
    req = urllib.request.Request(URL, headers={
        'User-Agent': UA,
        'Accept': 'application/json',
        'Referer': 'https://www.chinamoney.com.cn/chinese/bkccpr/',
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    date_str = data.get('data', {}).get('lastDate', '').split(' ')[0]
    for rec in data.get('records', []):
        if rec.get('foreignCName') == 'USD':
            return date_str, float(rec['price'])
    raise RuntimeError('USD not found')


if __name__ == '__main__':
    date, rate = fetch()
    print(f'fetched: {date} rate={rate}')
    os.makedirs('docs', exist_ok=True)
    out = {
        'date': date,
        'rate': rate,
        'source': 'chinamoney.com.cn',
        'updated_at': datetime.datetime.utcnow().isoformat() + 'Z',
    }
    with open('docs/rate.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('wrote docs/rate.json')
