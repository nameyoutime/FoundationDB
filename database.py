import fdb
import itertools

fdb.api_version(700)
db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
db.options.set_transaction_retry_limit(100)

scheduling = fdb.directory.create_or_open(db, ('scheduling',))
course = scheduling['course']
attends = scheduling['attends']


student = fdb.directory.create_or_open(db, ('student',))
student_id = student['id']
# Generate 3 classes
levels = ['intro', 'for dummies']
types = ['chem']
times = [str(h) + ':00' for h in range(1, 3)]
class_combos = itertools.product(times, types, levels)
class_names = [' '.join(tup) for tup in class_combos]
print('init database')
@fdb.transactional
def add_class(tr, c):
    tr[course.pack((c,))] = fdb.tuple.pack((15,))

@fdb.transactional
def search_name_student(tr,keyword):
    studentList = available_unique_subspace(db, student_id)
    for i in range(len(studentList)):
        searchResult = get_value_decode(db, student_id.pack((int(i+1),)))
        searchResult = dict(zip(searchResult[::2], searchResult[1::2]))
        if keyword in searchResult['name']:
            return searchResult
    return None

# get list field with subspace
@fdb.transactional
def available_subspace(tr,subspace):
    return [subspace.unpack(k)[0] for k, v in tr[subspace.range(())]]

# get list field with subspace
@fdb.transactional
def available_unique_subspace(tr,subspace):
    result = [subspace.unpack(k)[0] for k, v in tr[subspace.range(())]]
    # get only unique value
    result = list(dict.fromkeys(result))
    return result

# get invidiously value with subspace
@fdb.transactional
def get_value_decode(tr,subKey):
    try:
        return fdb.tuple.unpack((tr[subKey]),)
    except:
        return tuple('',)
# get invidiously value with subspace
@fdb.transactional
def set_value_decode(tr,subKey,value):
    tr[subKey] = value
    
# get invidiously value with subspace
@fdb.transactional
def delete_value(tr,subKey):
    del tr[subKey]

# clear subspace
@fdb.transactional
def clear_subspace(tr, subspace):
    tr.clear_range_startswith(subspace.key())
@fdb.transactional
def get_range_startswith(tr,subspaceMix):
    result = {}
    for k, v in tr.get_range_startswith(subspaceMix):
        print(k.decode(), v)
        result = {**result, **{k.decode(): v.decode()}}
    return result

@fdb.transactional
def init(tr):
    print('init')
    # del tr[scheduling.range(())]
    # del tr[attends.range(())]
    # del tr[student.range(())]
    # del tr[student_id.range(())]
    
    for class_name in class_names:
        add_class(tr, class_name)