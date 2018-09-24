from celery import Celery
from database_handler import DatabaseHandler
from time import sleep


app = Celery('tasks', broker='amqp://localhost//')
dh = DatabaseHandler()

@app.task
def add_person(person_info):
    print 'Start writing person info into the database'
    sleep(5)
    # return dh.add_person(person_info)
    print 'Finish writing person data'

@app.task
def generate_records():
    print 'Start generating records'
    sleep(10)
    # return dh.generate_records()
    print 'Finish generating records'
