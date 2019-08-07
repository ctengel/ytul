#!/usr/bin/env python3

import sys
import config
import pprint
import pymongo

mongo = pymongo.MongoClient(config.mongo[0])[config.mongo[1]]

mngfnd = mongo.videos.find({'site': 'youtube.com'},{'_id': 1, 'id': 1})

fullist = [x for x in mngfnd]

allids = sorted(list(set([x['id'] for x in fullist])))

for vid in allids:
    print(vid)
    myids = sorted([(x['_id'].generation_time, x['_id']) for x in fullist if x['id']==vid])
    keep = myids[0]
    delort = myids[1:]
    print('keep', keep[0])
    print('delort', [str(x[0]) for x in delort])
    for baleet in delort:
        mongo.videos.remove({'_id': baleet[1]})

