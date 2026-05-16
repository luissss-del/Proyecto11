import json

with open('datos.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

for obj in datos:
    if obj.get('model') == 'login.user':
        ti = obj['fields'].get('Ti', 0)
        if isinstance(ti, int) and ti > 2147483647:
            obj['fields']['Ti'] = 0

with open('datos.json', 'w', encoding='utf-8') as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

print("Listo!")