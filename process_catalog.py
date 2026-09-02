import csv
import json
import re
import urllib.request
import urllib.parse
import os
import time

os.makedirs('images', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_bing_image(query):
    try:
        url = 'https://www.bing.com/images/search?q=' + urllib.parse.quote(query) + '&first=1'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode('utf-8', errors='ignore')
            murls = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', html)
            if not murls:
                murls = re.findall(r'\"murl\":\"([^\"]+)\"', html)
            for m in murls:
                m_clean = m.split('?')[0]
                if any(m_clean.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    return m
            if murls:
                return murls[0]
    except Exception as e:
        print(f"Error searching {query}: {e}")
    return None

def download_image(url, local_path):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as res:
            data = res.read()
            if len(data) > 3000:
                with open(local_path, 'wb') as f:
                    f.write(data)
                return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return False

# Mapping for specific search queries to get accurate product pictures
query_map = {
    1: 'LuxPower SNA 6000 WPV hybrid inverter',
    2: 'LuxPower SNA PRO 6.5K inverter',
    3: 'LuxPower SNA2-EU-LT 14K inverter',
    4: 'Solis S6-EO1P5K-48-EU inverter',
    5: 'Solis S6-EH1P6K-L-PLUS inverter',
    6: 'Solis S6-EH1P8K-L-PLUS inverter',
    7: 'Deye SUN-6K-SG05LP1-AM2-PLUS inverter',
    8: 'Deye SUN-8K-SG05LP1-EU-AM2-PLUS inverter',
    9: 'Deye SUN-12K-SG02LP1-EU-AM3-PLUS inverter',
    10: 'Solis S6-EH3P12K02-NV-YD-L inverter',
    11: 'Solis S6-EH3P15K02-NV-YD-L inverter',
    12: 'Solis S6-EH3P15K-H inverter',
    13: 'Solis S6-EH3P20K-H inverter',
    14: 'Deye SUN-12K-SG05LP3-EU-SM2 inverter',
    15: 'Deye SUN-15K-SG05LP3-EU-SM2 inverter',
    16: 'Deye SUN-16K-SG01LP1-EU inverter',
    17: 'Deye SUN-20K-SG05LP3-EU-SM2 inverter',
    18: '2E LFP48100 battery 48V 100Ah',
    19: 'BYD BatteryBox LV5.0+ LiFePO4',
    20: 'Leapton EL-A05 51.2V 100Ah battery',
    21: 'Dyness DL5.0C LiFePO4 battery',
    22: 'Dyness DL5.0C Pro LiFePO4 battery',
    23: 'Dyness PowerHaus 5.12kWh battery',
    24: 'Dyness Powerbrick Plus 16.07kWh',
    25: 'Deye SE-F5 Pro-C battery',
    26: 'Deye SE-F16-C battery',
    27: 'Dyness Stack100 SBDU100 control box',
    28: 'Dyness SBDU200 control box',
    29: 'Dyness Stack100 S51100 Heat battery',
    30: 'Dyness Stack280 S51280 battery',
    31: 'Dyness Stack314 S51314 battery',
    32: 'Solis S6-EH3P30K-H hybrid inverter',
    33: 'Solis S6-EH3P50K-H hybrid inverter',
    34: 'JA Solar JAM72D40-610/LB 610W panel',
}

products = []

with open('products.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader) # header

    idx = 1
    for row in reader:
        if not row or not row[0].strip():
            continue
        raw_name = row[0].strip()
        price_val = int(row[1].strip()) if row[1].strip().isdigit() else 0
        status_val = row[2].strip() if len(row) > 2 else '+'

        # Category detection
        if 'інвертор' in raw_name.lower() or 'инвертор' in raw_name.lower():
            category = 'inverter'
            cat_name = 'Інвертори'
        elif 'панель' in raw_name.lower():
            category = 'solar'
            cat_name = 'Сонячні панелі'
        elif 'система керування' in raw_name.lower() or 'sbdu' in raw_name.lower():
            category = 'bms'
            cat_name = 'Системи керування'
        elif 'акб' in raw_name.lower() or 'акумулятор' in raw_name.lower() or 'батарея' in raw_name.lower():
            category = 'battery'
            cat_name = 'Акумулятори'
        else:
            category = 'other'
            cat_name = 'Обладнання'

        # Brand detection
        brand = 'SolarTech'
        for b in ['LuxPower', 'Solis', 'Deye', 'Dyness', 'BYD', 'Leapton', '2E', 'JA Solar', 'Huawei', 'Growatt']:
            if b.lower() in raw_name.lower():
                brand = b
                break

        # Status parsing
        if status_val == '+':
            stock_status = 'in_stock'
            stock_label = 'В наявності'
            stock_badge_class = 'badge-in-stock'
        elif status_val == '-':
            stock_status = 'out_of_stock'
            stock_label = 'Під замовлення'
            stock_badge_class = 'badge-out-stock'
        else:
            stock_status = 'preorder'
            stock_label = f"Очікується {status_val}"
            stock_badge_class = 'badge-preorder'

        # Specs parsing
        specs = {}
        # Power
        m_power = re.search(r'(\d+(?:[.,]\d+)?)\s*(кВт\*?год|кВт·год|кВтч|кВт|Вт|W|kWh|kW)', raw_name, re.IGNORECASE)
        if m_power:
            specs['power'] = f"{m_power.group(1)} {m_power.group(2)}"

        # Phases
        if '1 фаз' in raw_name.lower() or 'однофаз' in raw_name.lower() or '1p' in raw_name.lower():
            specs['phases'] = '1 фаза'
        elif '3 фаз' in raw_name.lower() or 'трифаз' in raw_name.lower() or '3p' in raw_name.lower():
            specs['phases'] = '3 фази'

        # Voltage / Battery type
        if 'lifepo4' in raw_name.lower():
            specs['type'] = 'LiFePO4'
        elif 'bifacial' in raw_name.lower():
            specs['type'] = 'Bifacial N-type'

        if '51.2в' in raw_name.lower() or '51,2 в' in raw_name.lower() or '51.2v' in raw_name.lower():
            specs['voltage'] = '51.2 В'
        elif '48v' in raw_name.lower() or '48в' in raw_name.lower() or '48 в' in raw_name.lower():
            specs['voltage'] = '48 В'

        if 'hv' in raw_name.upper():
            specs['batt_type'] = 'HV (Високовольтний)'
        elif 'lv' in raw_name.upper():
            specs['batt_type'] = 'LV (Низьковольтний)'

        # MPPT
        m_mppt = re.search(r'(\d+x?|\d+\s*)MPPT', raw_name, re.IGNORECASE)
        if m_mppt:
            specs['mppt'] = f"{m_mppt.group(1).strip()} MPPT"

        # Search & Download image
        q = query_map.get(idx, f"{brand} {raw_name}")
        local_img = f"images/item_{idx}.jpg"

        img_url = None
        if not os.path.exists(local_img) or os.path.getsize(local_img) < 3000:
            print(f"[{idx}/34] Searching image for: {q}")
            found_url = search_bing_image(q)
            if found_url:
                print(f"   Downloading: {found_url[:80]}...")
                if download_image(found_url, local_img):
                    img_url = local_img
                else:
                    img_url = found_url # fallback to remote
            time.sleep(0.5)
        else:
            img_url = local_img

        products.append({
            'id': idx,
            'category': category,
            'catName': cat_name,
            'brand': brand,
            'name': raw_name,
            'price': price_val,
            'status': stock_status,
            'statusLabel': stock_label,
            'statusBadgeClass': stock_badge_class,
            'specs': specs,
            'image': img_url if img_url else local_img
        })
        idx += 1

with open('products_data.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Successfully processed {len(products)} products and saved to products_data.json")
