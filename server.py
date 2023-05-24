from flask import Flask,request, jsonify
import itertools
import fdb
app = Flask(__name__)
fdb.api_version(700)
import json

db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
db.options.set_transaction_retry_limit(100)

# create a subspace
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

@fdb.transactional
def add_class(tr, c):
    tr[course.pack((c,))] = fdb.tuple.pack((15,'test'))

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
    return fdb.tuple.unpack((tr[subKey]),)

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

@app.route('/')
def hello_world():
    return jsonify(message='Hello, World!')

@app.route('/signup', methods=['POST'])
def signup_course():
    data = request.json
    studentId = data["studentId"]
    courseName = data["courseName"]
    prevArray = []
    try:
        studentsIdList = get_value_decode(db, attends[courseName])
        prevArray = dict(studentsIdList)['studentIds']
    except:
        pass
    data = {'studentIds':appendTuple(prevArray,int(studentId))}
    set_value_decode(db, attends[courseName], fdb.tuple.pack(tuple(data.items())))
    return jsonify(data='success')

def appendTuple(my_tuple,appendValue):
    my_list = list(my_tuple)
    my_list.append(appendValue)
    result_tuple = tuple(my_list)
    return result_tuple

@app.route('/courses')
def get_courses():
    name = request.args.get('name')
    if name is not None:
        result = get_value_decode(db, course[name])
    else:
        result = available_subspace(db, course)
    return jsonify(data=result)

@app.route('/attends')
def get_attends():
    name = request.args.get('name')
    if name is not None:
        result = get_value_decode(db, attends[name])
        result = dict(result)
        return jsonify({'data':result})
    result = available_unique_subspace(db, attends)
    return jsonify(data=result)

@app.route('/students')
def get_students():
    id = request.args.get('id')
    if id is not None:
        result = get_value_decode(db, student_id.pack((int(id),)))
        result = dict(result)
        return jsonify({'data':result})
    name = request.args.get('name')
    if name is not None:
        result = search_name_student(db, name)
        return jsonify({'data':result})
    result = available_unique_subspace(db, student_id)
    return jsonify(data=result)

@app.route('/register', methods=['POST'])
def reset():
    data = request.json
    name = data["name"]
    description = data["description"]
    studentList = available_unique_subspace(db, student)
    newStudent = {'id':int(len(studentList)+1),'name':name,'description':description}
    set_value_decode(db, student_id.pack((int(len(studentList)+1),)), fdb.tuple.pack(tuple(newStudent.items())))
    return jsonify(data='successfully register')

@app.route('/attend/<id>', methods=['DELETE'])
def delete_attends(id):
    delete_value(db, attends[int(id)]['courseName'])
    delete_value(db, attends[int(id)]['studentId'])
    return jsonify(data='successfully remove')

@app.route('/subspace/<subspace>')
def get_subspace(subspace):
    if subspace == 'scheduling':
        result = available_unique_subspace(db, scheduling)
    elif subspace == 'student':
        result = available_unique_subspace(db, student)
    elif subspace == 'attends':
        result = available_unique_subspace(db, attends)
    elif subspace == 'course':
        result = available_unique_subspace(db, course)

    return jsonify(data=result)

@fdb.transactional
def init(tr):
    del tr[scheduling.range(())]
    del tr[attends.range(())]
    # del tr[student.range(())]
    # del tr[student_id.range(())]
    
    for class_name in class_names:
        add_class(tr, class_name)

if __name__ == '__main__':  
    # init(db)
    app.run()
