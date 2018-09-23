from celery import Celery
from database_handler import DatabaseHandler
from time import sleep


app = Celery('tasks', broker='amqp://localhost//')
dh = DatabaseHandler()

@app.task
def add_person(person_info):
    print 'Add person'
    # return dh.add_person(person_info)

@app.task
def generate_records():
    print 'Start generating records'
    sleep(10)
    print 'Finish generating records'
    # return dh.generate_records()
