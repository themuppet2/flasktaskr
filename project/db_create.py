from views import db
from models import Task
from datetime import date

# create the database and the db table
db.create_all()

# insert data
db.session.add(
    Task("Finish this tutorial", date(2016, 9, 1), 10, 1)
    )
db.session.add(
    Task("Finish Real Python Course 2", date(2017, 1, 1),10, 1)
    )

# commit these changes
db.session.commit()