import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()
#

# item = {
#     'name': 'caiye',
#     'age': 18,
#     'city': 'huanggang',
#     'books': ['cc'],
#     'love': 'gwg',
# }
#
# values = tuple((value for _, value in item.items() if not isinstance(value, list) else value[0]))
#
# print(values)