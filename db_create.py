# db_create.py

from project import db

# create the database and the db table
db.create_all()

# insert data
#db.session.add(
#    User("admin", "ad@min.com", "admin", "admin")
#)

#db.session.add(
#    Task("Finish this tutorial", date(2016, 9, 1), 10, date(2016, 7, 31), 1, 1)
#)
#db.session.add(
#    Task("Finish Real Python Course 2", date(2017, 1, 1), 10, date(2016, 7, 31), 1, 1)
#)

# commit these changes
db.session.commit()