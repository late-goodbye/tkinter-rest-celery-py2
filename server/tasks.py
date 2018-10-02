from celery import Celery
from database_handler import DatabaseHandler


app = Celery('tasks', backend='amqp', broker='amqp://localhost//')
dh = DatabaseHandler()

@app.task
def add_person(person_info):
    """ Add person task """
    print 'Start writing person info into the database'
    dh.add_person(person_info)
    print 'Finish writing person data'
    return True

@app.task
def generate_records(filename):
    """ Generation records txt file task """
    print 'Start generating records'
    print '{}.txt'.format(filename)
    with open('{}.txt'.format(filename), 'w') as file:
        records = dh.generate_records()
        for record in records:
            print 'Record: {}'.format(record)
            file.write('{} {} {} {}\n'.format(*record))
    print 'Finish generating records'
