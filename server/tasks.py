from celery import Celery
from database_handler import DatabaseHandler
from time import sleep


app = Celery('tasks', backend='amqp', broker='amqp://localhost//')
dh = DatabaseHandler()

@app.task
def add_person(person_info):
    print 'Start writing person info into the database'
    sleep(5)
    dh.add_person(person_info)
    print 'Finish writing person data'
    return True

@app.task
def generate_records(addr):
    print 'Start generating records'
    sleep(10)
    with open('records-{}-{}.txt'.format(*addr), 'w') as file:
        records = dh.generate_records()
        for record in records:
            print 'Record: {}'.format(record)
            file.write('{} {} {} {}\n'.format(*record))
    print 'Finish generating records'
    return True
