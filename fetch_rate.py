"""
从中国外汇交易中心拉美元/人民币中间价，写入 docs/rate.json 供前端 fetch。
GitHub Actions 每天北京时间 10:00 自动运行。
"""
import json, os, urllib.request, ssl, datetime, re

ssl._create_default_https_context = ssl._create_unverified_context

URL_PRIMARY = 'https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json'
URL_FALLBACK = 'https://kylc.com/huilv/d-safe-usd.html'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def fetch_chinamoney():
    req = urllib.request.Request(URL_PRIMARY, headers={
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


def fetch_kylc():
    req = urllib.request.Request(URL_FALLBACK, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2})\s*</td>\s*<td[^>]*>\s*([\d.]+)\s*</td>')
    matches = pattern.findall(html)
    if not matches:
        raise RuntimeError('kylc parse failed')
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches[0][0], float(matches[0][1])


if __name__ == '__main__':
    date, rate = None, None
    for name, fn in [('chinamoney', fetch_chinamoney), ('kylc', fetch_kylc)]:
        try:
            print(f'trying {name}...')
            date, rate = fn()
            print(f'fetched: {date} rate={rate}')
            break
        except Exception as e:
            print(f'{name} failed: {e}')
    if rate is None:
        print('ALL SOURCES FAILED')
        raise SystemExit(1)
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
