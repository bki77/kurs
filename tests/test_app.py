import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Teacher, Room, Discipline, Group, Schedule


@pytest.fixture
def test_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


class TestModels:
    def test_create_teacher(self, test_app):
        with test_app.app_context():
            teacher = Teacher(
                last_name='Иванов',
                first_name='Иван',
                middle_name='Иванович',
                position='Доцент'
            )
            db.session.add(teacher)
            db.session.commit()
            
            assert teacher.id is not None
            assert teacher.last_name == 'Иванов'
            assert teacher.full_name() == 'Иванов Иван Иванович'
    
    def test_create_room(self, test_app):
        with test_app.app_context():
            room = Room(
                room_number='101',
                building='Главный',
                capacity=30,
                has_equipment='Проектор'
            )
            db.session.add(room)
            db.session.commit()
            
            assert room.id is not None
            assert room.room_number == '101'
            assert str(room) == 'Ауд. 101'
    
    def test_create_discipline(self, test_app):
        with test_app.app_context():
            discipline = Discipline(
                name='Высшая математика',
                code='ВМ',
                hours=72
            )
            db.session.add(discipline)
            db.session.commit()
            
            assert discipline.id is not None
            assert discipline.name == 'Высшая математика'
    
    def test_create_group(self, test_app):
        with test_app.app_context():
            group = Group(
                name='ИС-21',
                specialty='Информационные системы',
                course=1,
                students_count=25
            )
            db.session.add(group)
            db.session.commit()
            
            assert group.id is not None
            assert group.name == 'ИС-21'


class TestRoutes:
    def test_index_redirect(self, client):
        response = client.get('/')
        assert response.status_code == 302
    
    def test_schedule_page(self, client):
        response = client.get('/schedule')
        assert response.status_code == 200
    
    def test_teachers_list(self, client):
        response = client.get('/teachers')
        assert response.status_code == 200
    
    def test_rooms_list(self, client):
        response = client.get('/rooms')
        assert response.status_code == 200
    
    def test_disciplines_list(self, client):
        response = client.get('/disciplines')
        assert response.status_code == 200
    
    def test_groups_list(self, client):
        response = client.get('/groups')
        assert response.status_code == 200


class TestScheduleConflict:
    def test_room_conflict_detection(self, test_app, client):
        with test_app.app_context():
            room = Room(room_number='101', building='Главный', capacity=30)
            teacher = Teacher(last_name='Петров', first_name='Петр')
            discipline = Discipline(name='Математика')
            group = Group(name='ИС-21')
            
            db.session.add_all([room, teacher, discipline, group])
            db.session.commit()
            
            schedule1 = Schedule(
                group_id=group.id,
                discipline_id=discipline.id,
                teacher_id=teacher.id,
                room_id=room.id,
                day_of_week=1,
                lesson_number=1,
                start_time='08:30',
                end_time='10:05',
                lesson_type='лекция',
                week_type='все'
            )
            db.session.add(schedule1)
            db.session.commit()
            
            teacher2 = Teacher(last_name='Сидоров', first_name='Сидор')
            db.session.add(teacher2)
            db.session.commit()
            
            existing_room = Schedule.query.filter(
                Schedule.room_id == room.id,
                Schedule.day_of_week == 1,
                Schedule.lesson_number == 1,
                (Schedule.week_type == 'все')
            ).first()
            
            assert existing_room is not None


class TestFunctionality:
    
    def test_add_teacher_form(self, client):
        response = client.get('/teachers/add')
        assert response.status_code == 200
    
    def test_add_room_form(self, client):
        response = client.get('/rooms/add')
        assert response.status_code == 200
    
    def test_add_discipline_form(self, client):
        response = client.get('/disciplines/add')
        assert response.status_code == 200
    
    def test_add_group_form(self, client):
        response = client.get('/groups/add')
        assert response.status_code == 200
    
    def test_add_schedule_form(self, client):
        response = client.get('/schedule/add')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
