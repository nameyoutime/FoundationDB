from flask import Flask,request, jsonify
from database import scheduling,course,attends,student,student_id,db,init, add_class, search_name_student, available_subspace, available_unique_subspace, get_value_decode, set_value_decode, delete_value
import json
import fdb

app = Flask(__name__)

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
    result = available_subspace(db, attends)
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
    result = available_subspace(db, student_id)
    return jsonify(data=result)

@app.route('/register', methods=['POST'])
def reset():
    data = request.json
    name = data["name"]
    description = data["description"]
    studentList = available_subspace(db, student)
    newStudent = {'id':int(len(studentList)+1),'name':name,'description':description}
    set_value_decode(db, student_id.pack((int(len(studentList)+1),)), fdb.tuple.pack(tuple(newStudent.items())))
    return jsonify(data='successfully register')

@app.route('/attend/<courseName>', methods=['DELETE'])
def delete_attends(courseName):
    set_value_decode(db, attends[courseName], fdb.tuple.pack(('',)))
    return jsonify(data='successfully remove')

@app.route('/subspace/<subspace>')
def get_subspace(subspace):
    if subspace == 'scheduling':
        result = available_subspace(db, scheduling)
    elif subspace == 'student':
        result = available_subspace(db, student)
    elif subspace == 'attends':
        result = available_subspace(db, attends)
    elif subspace == 'course':
        result = available_subspace(db, course)

    return jsonify(data=result)

if __name__ == '__main__':  
    # init(db)
    app.run()
