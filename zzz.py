#!/usr/bin/env python3

import sys
import config
import pprint
import pymongo
import json

class zzz:
    def __init__(self):
        self.mongo = pymongo.MongoClient(config.mongo[0])[config.mongo[1]]

    def loadpl(self, site, plid, datafile):
        with open(datafile) as fd:
            rawdata = json.load(fd)
        info = {'site': site,
                'playlistId': plid,
                'items': rawdata}
        return self.mongo.lists.insert_one(info).inserted_id

    def getpl(self, query):
        return self.mongo.lists.find_one(query)

    def createvids(self, pldata):
        bla = []
        for i in pldata['items']:
            j = {'site': pldata['site']}
            j.update(i)
            bla.append(j)
        return self.mongo.videos.insert_many(bla).inserted_ids

    def print_readable(self, pldata):
        print('<ul>')
        newlist = pldata['items']
        newlist.sort(key = lambda i: i['videoName'])
        for x in newlist:
            s = pldata['site']
            n = pldata['playlistId'] + ' ' + x['videoName']
            print('<li><a href="https://{}/assets/videos/{} low.mp4">{}</a> <a href="https://{}/assets/videos/{} high.mp4"><img src="https://{}/assets/images/{}.jpg" alt="{}" /></a></li>'.format(s,n,n,s,n,s,n,n))
        print('</ul>')

if __name__ == "__main__":
    YOUTUBE = zzz()
    #listy = YOUTUBE.loadpl(*sys.argv[1:])
    #fullist = YOUTUBE.getpl({'_id': listy})
    fullist = YOUTUBE.getpl({'site': sys.argv[1], 'playlistId': sys.argv[2]})
    #YOUTUBE.createvids(fullist)
    YOUTUBE.print_readable(fullist)
