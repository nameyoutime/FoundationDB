import fdb
fdb.api_version(700)

db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
db.options.set_transaction_retry_limit(100)

# create a subspace
scheduling = fdb.directory.create_or_open(db, ('scheduling',))

student = fdb.directory.create_or_open(db, ('student',))

student_id_name = student['id-name']

course = scheduling['course']
attends = scheduling['attends']

@fdb.transactional
def add_class(tr, c):
    tr[course.pack((c,))] = fdb.tuple.pack((100,))

import itertools

# Generate 3 classes
levels = ['intro', 'for dummies']
types = ['chem']
times = [str(h) + ':00' for h in range(1, 3)]
class_combos = itertools.product(times, types, levels)
class_names = [' '.join(tup) for tup in class_combos]


@fdb.transactional
def init(tr):
    del tr[scheduling.range(())]  # Clear the directory
    del tr[student.range(())]  # Clear the directory
    for class_name in class_names:
        add_class(tr, class_name)

@fdb.transactional
def available_subspace(tr):
    return [scheduling.unpack(k)[0] for k, v in tr[scheduling.range(())]]

@fdb.transactional
def available_classes(tr):
    return [course.unpack(k)[0] for k, v in tr[course.range(())]]

@fdb.transactional
def available_attends(tr):
    return [attends.unpack(k)[0] for k, v in tr[attends.range(())]]

@fdb.transactional
def signup(tr, s, c):
    rec = attends.pack((s, c))
    tr[rec] = b''

@fdb.transactional
def drop(tr, s, c):
    rec = attends.pack((s, c))
    del tr[rec]
    
    
    
@fdb.transactional
def available_subspace_students(tr):
    return [student.unpack(k)[0] for k, v in tr[student.range(())]]
    
@fdb.transactional
def register_student(tr, idName):
    rec = student_id_name.pack((idName,))
    tr[rec] = b''

@fdb.transactional
def set_student_description(tr,idName):
    rec = student_id_name.pack((idName,))
    tr[rec] = f"my name is:{idName}".encode()

# get list field with subspace
@fdb.transactional
def available_subspace(tr,subspace):
    return [subspace.unpack(k)[0] for k, v in tr[subspace.range(())]]

# get invidiously value with subspace
# print(get_value(db, student_id_name, '1-thien'))
@fdb.transactional
def get_value(tr,subspace, key):
    return tr[subspace.pack((key,))].decode()

# set invidiously value with subspace
@fdb.transactional
def set_value(tr,subspace, key, value):
    rec = subspace.pack((key,))
    tr[rec] = value.encode()

@fdb.transactional
def clear_subspace(tr, subspace):
    tr.clear_range_startswith(subspace.key())
    
if __name__ == "__main__":
    init(db)
    print("initialized")
    # clear_subspace(db, course)
    print(available_subspace(db, scheduling))