from flask import Flask,request, jsonify
import itertools
import fdb
app = Flask(__name__)
fdb.api_version(700)

db = fdb.open()
db.options.set_transaction_timeout(60000)  # 60,000 ms = 1 minute
db.options.set_transaction_retry_limit(100)

# create a subspace
scheduling = fdb.directory.create_or_open(db, ('scheduling',))
course = scheduling['course']
attends = scheduling['attends']


student = fdb.directory.create_or_open(db, ('student',))
student_id = student['student_id']

student_name = student.create_or_open(db, ('name',))
student_description = student.create_or_open(db, ('description',))

# Generate 3 classes
levels = ['intro', 'for dummies']
types = ['chem']
times = [str(h) + ':00' for h in range(1, 3)]
class_combos = itertools.product(times, types, levels)
class_names = [' '.join(tup) for tup in class_combos]

@fdb.transactional
def add_class(tr, c):
    tr[course.pack((c,))] = fdb.tuple.pack((100,))



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
    return (tr[subKey]).decode()

# get invidiously value with subspace
@fdb.transactional
def set_value_decode(tr,subKey,value):
    tr[subKey] = value.encode()
    
# get invidiously value with subspace
@fdb.transactional
def delete_value(tr,subKey):
    del tr[subKey]

# clear subspace
@fdb.transactional
def clear_subspace(tr, subspace):
    tr.clear_range_startswith(subspace.key())


@app.route('/')
def hello_world():
    return jsonify(message='Hello, World!')

@app.route('/signup', methods=['POST'])
def signup_course():
    data = request.json
    idName = data["idName"]
    courseName = data["courseName"]
    courseList = available_subspace(db, attends)
    courseIdName = f'{len(courseList)+1}-{courseName}'
    set_value_decode(db, scheduling['attends'][idName]['name'], idName)
    set_value_decode(db, scheduling['attends'][idName]['description'], courseIdName)

    return jsonify(data='success')

@app.route('/courses')
def get_courses():
    name = request.args.get('name')
    if name is not None:
        result = get_value(db, course, name)
    else:
        result = available_subspace(db, course)
    return jsonify(data=result)

@app.route('/attends')
def get_attends():
    name = request.args.get('name')
    if name is not None:
        resultName = get_value_decode(db, scheduling['attends'][name]['name'])
        print(resultName)
        resultDescription = get_value_decode(db, scheduling['attends'][name]['description'])
        response = {'data':{
        'description': resultDescription,
        'name': resultName
        }}
        return jsonify(response)
    result = available_unique_subspace(db, attends)
    return jsonify(data=result)

@app.route('/students')
def get_students():
    name = request.args.get('name')
    if name is not None:
        resultName = get_value_decode(db, student_id[name]['name'])
        resultDescription = get_value_decode(db, student_id[name]['description'])
        response = {'data':{
        'description': resultDescription,
        'name': resultName
        }}
        return jsonify(response)
    result = available_unique_subspace(db, student_id)
    return jsonify(data=result)

@app.route('/register', methods=['POST'])
def reset():
    data = request.json
    description = data["description"]
    studentList = available_unique_subspace(db, student)
    studentData = f'{len(studentList)+1}-{data["name"]}'
    set_value_decode(db, student_id[studentData]['name'], data["name"])
    set_value_decode(db, student_id[studentData]['description'], data["description"])
    return jsonify(data='successfully register')

@app.route('/attend/<idName>', methods=['DELETE'])
def delete_attends(idName):
    delete_value(db, attends[idName]['name'])
    delete_value(db, attends[idName]['description'])
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
    # del tr[student_description.range(())]
    # del tr[student.range(())]
    # del tr[student_name.range(())]
    # del tr[student_id.range(())]
    
    for class_name in class_names:
        add_class(tr, class_name)


@fdb.transactional
def test(tr):
    result = tr[student['1-thien']]
    print(result)
    
if __name__ == '__main__':  
    # init(db)
    # test(db) 
    # print(available_unique_subspace(db,student))
    app.run()
