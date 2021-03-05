from app import db, User
from datetime import datetime

db.create_all()
print('Database created!')
print('Populating...')

## create User resource to db
user1 = User(username='username',
             email='test@email.com',
             pw_hash='12345')
db.session.add(user1)
db.session.commit()
print('Added User')
