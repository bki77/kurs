
from app import app, db

with app.app_context():
    db.create_all()
    print("Все таблицы успешно созданы в базе данных!")
    print("Таблицы: teachers, rooms, disciplines, groups, schedule")
