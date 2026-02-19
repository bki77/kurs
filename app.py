from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, Teacher, Room, Discipline, Group, Schedule

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)

@app.route('/')
def index():
    return redirect(url_for('schedule'))


@app.route('/schedule')
def schedule():
    group_id = request.args.get('group_id')
    
    query = Schedule.query
    
    if group_id:
        query = query.filter_by(group_id=int(group_id))
    
    schedules = query.order_by(Schedule.day_of_week, Schedule.lesson_number).all()
    groups = Group.query.all()
    
    return render_template('schedule.html', schedules=schedules, groups=groups)


@app.route('/schedule/add', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        group_id = int(request.form.get('group_id'))
        discipline_id = int(request.form.get('discipline_id'))
        teacher_id = int(request.form.get('teacher_id'))
        room_id = int(request.form.get('room_id'))
        day_of_week = int(request.form.get('day_of_week'))
        lesson_number = int(request.form.get('lesson_number'))
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        lesson_type = request.form.get('lesson_type')
        week_type = request.form.get('week_type', 'все')
        
        existing_room = Schedule.query.filter(
            Schedule.room_id == room_id,
            Schedule.day_of_week == day_of_week,
            Schedule.lesson_number == lesson_number,
            or_(Schedule.week_type == 'все', Schedule.week_type == week_type)
        ).first()
        
        if existing_room:
            flash('Ошибка: Аудитория занята в это время!', 'error')
            return redirect(url_for('add_schedule'))
        
        existing_teacher = Schedule.query.filter(
            Schedule.teacher_id == teacher_id,
            Schedule.day_of_week == day_of_week,
            Schedule.lesson_number == lesson_number,
            or_(Schedule.week_type == 'все', Schedule.week_type == week_type)
        ).first()
        
        if existing_teacher:
            flash('Ошибка: Преподаватель занят в это время!', 'error')
            return redirect(url_for('add_schedule'))
        
        new_schedule = Schedule(
            group_id=group_id,
            discipline_id=discipline_id,
            teacher_id=teacher_id,
            room_id=room_id,
            day_of_week=day_of_week,
            lesson_number=lesson_number,
            start_time=start_time,
            end_time=end_time,
            lesson_type=lesson_type,
            week_type=week_type
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        flash('Занятие успешно добавлено в расписание!', 'success')
        return redirect(url_for('schedule'))
    
    groups = Group.query.all()
    teachers = Teacher.query.all()
    rooms = Room.query.all()
    disciplines = Discipline.query.all()
    
    return render_template('add_schedule.html', 
                           groups=groups, 
                           teachers=teachers, 
                           rooms=rooms, 
                           disciplines=disciplines)


@app.route('/schedule/delete/<int:id>')
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Занятие удалено из расписания!', 'success')
    return redirect(url_for('schedule'))


@app.route('/teachers')
def teachers_list():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)


@app.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        teacher = Teacher(
            last_name=request.form.get('last_name'),
            first_name=request.form.get('first_name'),
            middle_name=request.form.get('middle_name'),
            position=request.form.get('position'),
            phone=request.form.get('phone'),
            email=request.form.get('email')
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Преподаватель добавлен!', 'success')
        return redirect(url_for('teachers_list'))
    return render_template('add_teacher.html')


@app.route('/teachers/delete/<int:id>')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Преподаватель удалён!', 'success')
    return redirect(url_for('teachers_list'))


@app.route('/rooms')
def rooms_list():
    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms)


@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room = Room(
            room_number=request.form.get('room_number'),
            building=request.form.get('building'),
            capacity=int(request.form.get('capacity') or 0),
            has_equipment=request.form.get('has_equipment')
        )
        db.session.add(room)
        db.session.commit()
        flash('Аудитория добавлена!', 'success')
        return redirect(url_for('rooms_list'))
    return render_template('add_room.html')


@app.route('/rooms/delete/<int:id>')
def delete_room(id):
    room = Room.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    flash('Аудитория удалена!', 'success')
    return redirect(url_for('rooms_list'))


@app.route('/disciplines')
def disciplines_list():
    disciplines = Discipline.query.all()
    return render_template('disciplines.html', disciplines=disciplines)


@app.route('/disciplines/add', methods=['GET', 'POST'])
def add_discipline():
    if request.method == 'POST':
        discipline = Discipline(
            name=request.form.get('name'),
            code=request.form.get('code'),
            hours=int(request.form.get('hours') or 0)
        )
        db.session.add(discipline)
        db.session.commit()
        flash('Дисциплина добавлена!', 'success')
        return redirect(url_for('disciplines_list'))
    return render_template('add_discipline.html')


@app.route('/disciplines/delete/<int:id>')
def delete_discipline(id):
    discipline = Discipline.query.get_or_404(id)
    db.session.delete(discipline)
    db.session.commit()
    flash('Дисциплина удалена!', 'success')
    return redirect(url_for('disciplines_list'))


@app.route('/groups')
def groups_list():
    groups = Group.query.all()
    return render_template('groups.html', groups=groups)


@app.route('/groups/add', methods=['GET', 'POST'])
def add_group():
    if request.method == 'POST':
        group = Group(
            name=request.form.get('name'),
            specialty=request.form.get('specialty'),
            course=int(request.form.get('course') or 1),
            students_count=int(request.form.get('students_count') or 0)
        )
        db.session.add(group)
        db.session.commit()
        flash('Группа добавлена!', 'success')
        return redirect(url_for('groups_list'))
    return render_template('add_group.html')


@app.route('/groups/delete/<int:id>')
def delete_group(id):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    flash('Группа удалена!', 'success')
    return redirect(url_for('groups_list'))


@app.route('/init-db')
def init_database():
    db.create_all()
    flash('База данных инициализирована!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
