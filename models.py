from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, verbose_name="Логин")
    password_hash = db.Column(db.String(200), nullable=False, verbose_name="Хэш пароля")
    role = db.Column(db.String(20), nullable=False, default='user', verbose_name="Роль (admin/user)")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, verbose_name="Дата создания")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    # Для Flask-Login
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"{self.username} ({self.role})"


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False, verbose_name="Фамилия")
    first_name = db.Column(db.String(100), nullable=False, verbose_name="Имя")
    middle_name = db.Column(db.String(100), verbose_name="Отчество")
    position = db.Column(db.String(100), verbose_name="Должность")
    phone = db.Column(db.String(20), verbose_name="Телефон")
    email = db.Column(db.String(100), verbose_name="Email")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, verbose_name="Дата создания")

    schedule = db.relationship('Schedule', back_populates='teacher', lazy=True)

    def __repr__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}"

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False, unique=True, verbose_name="Номер аудитории")
    building = db.Column(db.String(50), verbose_name="Корпус")
    capacity = db.Column(db.Integer, verbose_name="Вместимость")
    has_equipment = db.Column(db.Text, verbose_name="Оборудование")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, verbose_name="Дата создания")

    schedule = db.relationship('Schedule', back_populates='room', lazy=True)

    def __repr__(self):
        return f"Ауд. {self.room_number}"


class Discipline(db.Model):
    __tablename__ = 'disciplines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, verbose_name="Название дисциплины")
    code = db.Column(db.String(20), verbose_name="Код дисциплины")
    hours = db.Column(db.Integer, verbose_name="Часы")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, verbose_name="Дата создания")

    schedule = db.relationship('Schedule', back_populates='discipline', lazy=True)

    def __repr__(self):
        return self.name


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, verbose_name="Название группы")
    specialty = db.Column(db.String(200), verbose_name="Специальность")
    course = db.Column(db.Integer, verbose_name="Курс")
    students_count = db.Column(db.Integer, verbose_name="Количество студентов")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, verbose_name="Дата создания")

    schedule = db.relationship('Schedule', back_populates='group', lazy=True)

    def __repr__(self):
        return self.name


class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, verbose_name="Группа")
    discipline_id = db.Column(db.Integer, db.ForeignKey('disciplines.id'), nullable=False, verbose_name="Дисциплина")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False, verbose_name="Преподаватель")
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False, verbose_name="Аудитория")
    
    day_of_week = db.Column(db.Integer, nullable=False, verbose_name="День недели (1=Понедельник)")
    lesson_number = db.Column(db.Integer, nullable=False, verbose_name="Номер пары")
    start_time = db.Column(db.String(10), nullable=False, verbose_name="Время начала")
    end_time = db.Column(db.String(10), nullable=False, verbose_name="Время окончания")
    lesson_type = db.Column(db.String(20), nullable=False, verbose_name="Тип занятия (лекция/практика)")
    week_type = db.Column(db.String(20), verbose_name="Тип недели (четная/нечетная/все)")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, verbose_name="Дата создания")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, verbose_name="Дата обновления")

    group = db.relationship('Group', back_populates='schedule')
    discipline = db.relationship('Discipline', back_populates='schedule')
    teacher = db.relationship('Teacher', back_populates='schedule')
    room = db.relationship('Room', back_populates='schedule')

    def __repr__(self):
        return f"{self.group.name} - {self.discipline.name} - {self.day_of_week}/{self.lesson_number}"


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Таблицы базы данных успешно созданы!")
