@task(ignore_result=True)
def send_email(recepient, title, subject):
    print('sending email')

@task
def rebuild_search_index():
     time.sleep(500) # mimicking a long running process
     print('rebuilt search index')
     return 42