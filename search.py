import fdb

fdb.api_version(700)  # Set the appropriate API version

# Connect to FoundationDB
db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
db.options.set_transaction_retry_limit(100)
my_space = fdb.Subspace(('foo',))
student = fdb.directory.create_or_open(db, ('student',))
student_id = student['student_id']
# student_id = student['student_id']
enroll_space = fdb.Subspace(('enroll',))

@fdb.transactional
def search_by_name(tr):
    # print(student_id.pack(('1-thien','name')))
    # print(fdb.KeySelector.last_less_than(b'C'))
    # '\xFF'
    # name = 'thien'
    # range_start = f"student/".encode()    print(data_bytes)
    # range_end = f"student/\xFF".encode()
    # print('helloasdas'.encode())
    print(tr.get_range_startswith(student_id.pack((1,'name'))))
    # for k, v in tr.get_range_startswith(student_id.pack(('1-thien','name'))):
    #     print(k, v)
    # for k, v in tr.get_range(range_start,range_end):
    #     print(k, v)
# Example usage
search_by_name(db)
@fdb.transactional
def multi_set(tr, multi_space, index, value):
    tr[multi_space.pack((index, value))] = ''.encode()

@fdb.transactional
def multi_get(tr, multi_space, index):
    pairs = tr[multi_space.range((index,))]
    return [multi_space.unpack(k)[-1] for k, v in pairs]

@fdb.transactional
def multi_is_element(tr, multi_space, index, value):
    val = tr[multi_space.pack((index, value))]
    return val.present()


@fdb.transactional
def add_class(tr, student, class_name):
    multi_set(tr, enroll_space, student, class_name)

@fdb.transactional
def get_classes(tr, student):
    return multi_get(tr, enroll_space, student)
# print(get_classes(db, 'thien'))
