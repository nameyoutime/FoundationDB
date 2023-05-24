import fdb
fdb.api_version(700)

db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
db.options.set_transaction_retry_limit(100)


user_space = fdb.directory.create_or_open(db, ('scheduling',))

name = user_space['name']
description = user_space['description']


@fdb.transactional
def set_user_data(tr, key, value):
    tr[user_space.pack((key,))] = value.encode()
@fdb.transactional
def get_user_data(tr, key):
    print(tr[user_space.pack((key,))].decode())
@fdb.transactional
def available_user(tr):
    return [user_space.unpack(k)[0] for k, v in tr[user_space.range(())]]
# set_user_data(db, "description", "John is home")
# get_user_data(db, "name")
print(available_user(db))
# @fdb.transactional
# def add_item_to_list(tr, index, value):
#     key = f"my_list:{index}".encode()
#     tr[key] = value.encode()

    
# @fdb.transactional
# def get_item_from_list(tr, index):
#     key = f"my_list:{index}".encode()
#     print(f"my_list:{index}".encode())
#     value = tr[key]
#     return value.decode()

# add_item_to_list(db, 0, "value0")
# add_item_to_list(db, 1, "value1")

# item = get_item_from_list(db, 0)
# item1 = get_item_from_list(db, 1)

# print(item)
# print(item1)