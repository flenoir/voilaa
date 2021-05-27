import datetime
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./dbdir/todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(200))
    completed = db.Column(db.Boolean)
    category = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    position = db.Column(db.Integer, autoincrement=True)
    priority = db.Column(db.Integer)

def get_times():
    """
    get all durations of todos
    """
    uncompleted = Todo.query.filter_by(completed=False).all()
    completed = Todo.query.filter_by(completed=True).all()
    week_time = Todo.query.all()
    week_restime = [x.duration for x in week_time]
    todo_restime = [x.duration for x in uncompleted]
    done_restime = [x.duration for x in completed]
    total_time = str(datetime.timedelta(minutes=sum(week_restime)))[:-3]
    todo_total_time = str(datetime.timedelta(minutes=sum(todo_restime)))[:-3]
    done_total_time = str(datetime.timedelta(minutes=sum(done_restime)))[:-3]
    current_week = str(datetime.date.today().strftime("%V"))
    return total_time, todo_total_time, done_total_time, current_week

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    display all activities
    """
    uncompleted = Todo.query.filter_by(completed=False).order_by(Todo.priority.desc()).all()
    completed = Todo.query.filter_by(completed=True).all()
    total_time = get_times()[0]
    todo_total_time = get_times()[1]
    done_total_time = get_times()[2]
    week = get_times()[3]

    if request.method == 'POST':
        json_data = request.json
        # print(json_data)
        x = json_data.replace('item[]=', ',')
        y = x.replace('&,', '')
        final = y.replace(',', '')
        final = list(final)
        # print(final)
        sort = Todo.query.filter_by(completed=False).all()
        for i, s in enumerate(sort):
            # print(s.id, i, s, final[i])
            s.position = final[i]
            # print("the new position is :",s.position)
        db.session.commit()
        # sort.data = final


    return render_template("pages/home.html",uncompleted=uncompleted, completed=completed, time=total_time, todo_time = todo_total_time, done_time = done_total_time, week = week )
    # return render_template("pages/home.html",uncompleted=uncompleted, completed=completed )


@app.route('/about')
def about():
    time = get_times()[0]
    return render_template("pages/about.html", time=time)

@app.route('/contact')
def contact():
    return render_template("pages/contact.html")

@app.route('/add', methods=['POST'])
def add():
    """
    add an activity

    """
    job_duration = request.form['duration']
    job_completion = request.form['duration']

    # check if duration is empty
    if job_duration == "":
        job_duration = 30
    else:
        # check if duration is an integer
        try:
            isinstance(int(request.form['duration']), int)

        except (ValueError, TypeError):
            print('Duration value entered is not correct')

    if job_completion == "":
        job_completion = False
    else:
        job_completion = bool(int(request.form['completed']))




    todo = Todo(text=request.form['todoitem'], completed=job_completion, category=request.form['category'], duration=job_duration, priority=request.form['priority'])
    db.session.add(todo)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/complete/<id>')
def complete(id):
    """
    change activity status du complete
    """
    todo = Todo.query.filter_by(id=int(id)).first()
    todo.completed = True
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/edit/<id>')
def edit(id):
    """
    search an edit an activity
    """
    todo = Todo.query.filter_by(id=int(id)).first()
    # return "{}".format(todo.text)
    return render_template("pages/edit.html", todo=todo)

@app.route('/update/<id>', methods=['POST'])
def update(id):
    """
    update an activity
    """

    todo = Todo.query.filter_by(id=int(id)).first()
    textvalue = request.form['todoitem']
    categoryvalue = request.form['category']
    durationvalue = request.form['duration']
    completedvalue = request.form['completed']
    priorityvalue = request.form['priority']
    print("from form", completedvalue)
    todo.text = textvalue
    todo.category = categoryvalue
    todo.duration = durationvalue
    # convert Flase or True string to corresponding boolean values
    todo.completed = json.loads(completedvalue.lower())
    todo.priority = priorityvalue
    # if completedvalue is True:
    #     todo.completed = False
    # else:
    #     todo.completed = True

    print("after", todo.completed)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/delete/<id>')
def delete(id):
    """
    delete an activity
    """

    todo = Todo.query.filter_by(id=int(id)).first()
    db.session.delete(todo)
    db.session.commit()

    return redirect(url_for('home'))

def text_file_creation():
    """
    create text file for the current week
    """
    dt = datetime.date.today()
    week = dt.isocalendar()[1]
    file_path  = os.path.abspath(os.path.join(".","files","CR_FL_{}.txt".format(week)))
    # print(file_path)
    return file_path


@app.route('/write/<id>')
def write(id):
    """
    write individual completed todo
    """

    todo = Todo.query.filter_by(id=int(id)).first()
    # dt = datetime.date.today()
    # week = dt.isocalendar()[1]
    # file_path  = os.path.abspath(os.path.join(".","files","CR_FL_{}.txt".format(week)))
    fpath = text_file_creation()

    def writeAndDeleteFromDb(file_out):
        # file_out.write("c " + todo.category + "\n\n")
        file_out.write("=> " + todo.text + "\n\n")
        db.session.delete(todo)
        db.session.commit()

    if os.path.exists(fpath):
        with open(fpath,"a") as file_out:
            writeAndDeleteFromDb(file_out)

    else:
        with open(fpath, "w") as file_out:
            writeAndDeleteFromDb(file_out)


    return redirect(url_for('home'))

@app.route('/fullWrite')
def fullWrite():
    """
    write all completed todo in the text file
    """
    completed_todo = Todo.query.filter_by(completed=True)
    for t in completed_todo:
        print(t.text)

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)


