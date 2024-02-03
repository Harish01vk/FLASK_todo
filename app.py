from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'completed')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

with app.app_context():
    db.create_all()


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    try:
        if request.method == 'GET':
            tasks = Task.query.all()
            result = tasks_schema.dump(tasks)
            return jsonify({'tasks': result})
        elif request.method == 'POST':
            data = request.get_json()
            new_task = Task(title=data.get('title'), description=data.get('description', ''), completed=False)
            db.session.add(new_task)
            db.session.commit()
            return task_schema.jsonify(new_task), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        if request.method == 'GET':
            return task_schema.jsonify(task)
        elif request.method == 'PUT':
            data = request.get_json()
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.completed = data.get('completed', task.completed)
            db.session.commit()
            return jsonify({'message': 'Task updated successfully'})
        elif request.method == 'DELETE':
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()
        return jsonify({'message': 'Task toggled successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/clear', methods=['DELETE'])
def clear_completed_tasks():
    try:
        completed_tasks = Task.query.filter_by(completed=True).all()
        for task in completed_tasks:
            db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Completed tasks cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    return render_template('reg.html')

if __name__ == '__main__':
    app.run(debug=True)
