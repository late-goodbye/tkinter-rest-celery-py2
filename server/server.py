from celery import Celery
import sqlite3

app = Celery('tasks', backend='amqp', broker='amqp://')

@app.task
def print_hello():
    print 'Hello there'
