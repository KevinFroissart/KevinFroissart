import schedule
import time
import os

def update_artist_list():
	os.system('python3.8 artists.py')

schedule.every().friday.at('23:02').do(update_artist_list())

while 1:
	schedule.run_pending()
	time.sleep(1)
