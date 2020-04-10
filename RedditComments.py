import time
import re
import csv
import requests
import requests.auth
import praw
from praw.models import MoreComments

start = time.time()
quickMode = True

DEFAULT = 'DEFAULT'
DEFAULT_ENABLED = True
COMMENT = 'COMMENT'
COMMENT_ENABLED = True

def getTimeFromStart():
    return str(time.time() - start) + 's since script start'

def plog(s, logType=DEFAULT):
    showLog = False
    if (logType == 'DEFAULT' and DEFAULT_ENABLED == True):
        showLog = True
    elif (logType =='COMMENT' and COMMENT_ENABLED == True):
        showLog = True
    
    if showLog:
        print(s)

# setup praw client
reddit = praw.Reddit('fire-scraper')
prawTime = 'praw end: ' + getTimeFromStart()

# get the list of top level comments (from the sp 500 guess thread)
submission = reddit.submission(id='fwnrpt')
if not quickMode:
    submission.comments.replace_more(limit=None)

submissionFetchTime = 'submission end: ' + getTimeFromStart()

top_level_comments = list(submission.comments)
tlc_num = len(top_level_comments)
tlcTime = 'tlc end: ' + getTimeFromStart()

plog(f'tlc #: {tlc_num}')
plog('=' * 20)

realValueList = list()
clean = list()

for comment in top_level_comments:
    if isinstance(comment, MoreComments):
        plog('MoreComments skipped')
        continue

    # print(comment.body)
    retemp = re.findall(r'[0-9.]*[0-9]+', comment.body)
    refloat = [float(s) for s in re.findall(r'-?\d+\.?\d*', comment.body.replace(',', ''))]
    plog('-' * 15, COMMENT)
    plog(f'id: {comment}', COMMENT)
    plog(f'comment: {comment.body}', COMMENT)
    plog(f'retemp: {retemp}', COMMENT)
    plog(f'refloat: {refloat}', COMMENT)

    try:
        # relist = list(map(float, retemp))
        relist = refloat
    except:
        plog(f'error - comment: {comment.body}', COMMENT)
        continue

    # filter out a couple of scenarios:
    for ele in relist:
        if ele > 9999:
            if len(relist) == 1:
                continue
            relist.remove(ele)
        elif ele == 2020 and len(relist) > 1:
            relist.remove(ele)
        elif ele == 2019 and len(relist) > 1:
            relist.remove(ele)
            
    if len(relist) > 0:

        if max(relist) > 9999:
            plog(f'num is bigger than 5k: {max(relist)} - ignoring', COMMENT)
            continue
        
        clean.append(max(relist))
        plog(f'appended: {max(relist)}', COMMENT)
        
loopEndTime = 'submission end: ' + getTimeFromStart()

plog(f'# in final list: {len(clean)}')
#print(clean)
plog('writing to csv...')

with open('fire-test.csv', mode='w') as fire_file:
    fire_writer = csv.writer(fire_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for row in clean:
        fire_writer.writerow([row])

plog(f'finished writing to csv! total values: {len(clean)}')

plog('*' * 20)
plog('Time stats: ')
plog('*' * 20)

plog(prawTime)
plog(submissionFetchTime)
plog(tlcTime)
plog(loopEndTime)