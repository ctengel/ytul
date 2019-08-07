#!/usr/bin/env python3

import sys
import config
import googleapiclient.discovery
import pprint
import pymongo
import os

class yt:
    def __init__(self):
        self.mongo = pymongo.MongoClient(config.mongo[0])[config.mongo[1]]


    def match_curr(self, vs):
        mngfnd = self.mongo.videos.find({'site': 'youtube.com', 'dl_fname': None}, {'id': 1, '_id': 1})
        for i in mngfnd:
            for j in vs:
                if i['id'] in j:
                    self.mongo.videos.update_one({'_id': i['_id']}, {'$set': {'dl_fname': j}})

    def get_undl_ids(self, filt=None):
        mngfnd = self.mongo.videos.find({'site': 'youtube.com', 'dl_fname': None}, {'id': 1, 'snippet.channelTitle': 1})
        for i in mngfnd:
            if filt is None or i['snippet']['channelTitle'] in filt:
                print(i['id'])


def listfiles():
    full = os.listdir()
    return [x for x in full if (x.endswith('.mp4') or x.endswith('.mkv') or x.endswith('.webm'))]



if __name__ == "__main__":
    YOUTUBE = yt()
    dirlist = listfiles()
    YOUTUBE.match_curr(dirlist)
    YOUTUBE.get_undl_ids(sys.argv[1:])
