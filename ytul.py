#!/usr/bin/env python3

import sys
import config
import googleapiclient.discovery
import pprint
import pymongo

class yt:
    def __init__(self):
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = config.ytkey
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)
        self.mongo = pymongo.MongoClient(config.mongo[0])[config.mongo[1]]

    def call(self, plid, npt=None):
        if npt is None:
            chkmng = self.mongo.lists.find_one({'site': 'youtube.com', 'playlistId': plid})
            if chkmng:
                return chkmng['items'], chkmng['_id']
        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=plid,
            maxResults=50,
            pageToken=npt
        )
        response = request.execute()
        mines = response.pop('items')
        if response.get('nextPageToken'):
            mines = mines + self.call(plid, response['nextPageToken'])[0]
            del response['nextPageToken']
        mngid = None
        if npt is None:
            response['site'] = 'youtube.com'
            response['items'] = mines
            response['paginated'] = True
            response['playlistId'] = plid
            mngid = self.mongo.lists.insert_one(response).inserted_id
        return mines, mngid
    def details(self, vids):
        request = self.youtube.videos().list(
            part="snippet",
            id=",".join(vids)
        )
        response = request.execute()
        return response['items']

    def all_details(self, vids):
        vids = sorted(list(set(vids)))
        result = {}
        for v in vids.copy():
            mngfnd = self.mongo.videos.find_one({'site': 'youtube.com', 'id': v})
            if mngfnd:
                result[v] = (mngfnd['snippet'].get('channelId'), mngfnd['snippet'].get('channelTitle'), mngfnd['_id'])
                vids.remove(v)
        multivids = [vids[i:i+50] for i in range(0, len(vids), 50)]
        newresult = []
        for sub in multivids:
            newresult = list(newresult + self.details(sub))
        for i in newresult:
            i['site'] = 'youtube.com'
        newdict = {}
        if newresult:
            newids = list(self.mongo.videos.insert_many(newresult).inserted_ids)
            newdict = {x[0]['id']: (x[0]['snippet'].get('channelId'), x[0]['snippet'].get('channelTitle'), x[1]) for x in list(zip(newresult, newids))}
        result.update(newdict)
        return result


    def taglist(self, pl):
        # TODO actually tag the list within Mongo... this is not doing that
        mngfnd = self.mongo.lists.find_one(pl)['items']
        vids = [x['snippet']['resourceId']['videoId'] for x in mngfnd]
        alldets = self.all_details(vids)
        newdict = {}
        for x in mngfnd:
            rawdets = alldets.get(x['snippet']['resourceId']['videoId'], (None, None, None))
            x['realChanTitle'] = rawdets[1]
            x['realChanId'] = rawdets[2]
            x['video'] = rawdets[2]
            newdict[x['snippet']['resourceId']['videoId']] = x
        return newdict

    def ytsearch(self, string):
        mngfnd = self.mongo.searches.find_one({'site': 'youtube.com', 'q': string})
        if mngfnd:
            print('gotit')
            return [x['id']['playlistId'] for x in mngfnd['items']], mngfnd
        request = self.youtube.search().list(
                part='id',
                maxResults=50,
                q=string,
                type='playlist',
                safeSearch='none'
                )
        response = request.execute()
        answer =  [x['id']['playlistId'] for x in response['items']]
        response['site'] = 'youtube.com'
        response['paginated'] = False
        response['q'] = string
        self.mongo.searches.insert_one(response)
        return answer, response

def filtbychan(pl, by):
    return {k: v for k,v in pl.items() if v['realChanTitle'] in by or v['realChanId'] in by}

def print_readable(pl):
    print('<ul>')
    newlist = [x for x in pl.values()]
    newlist.sort(key = lambda i: (i['realChanTitle'], i['snippet']['title']))
    for x in newlist:
        print('<li><a href="https://www.youtube.com/embed/{}">{}</a> <a href="https://www.youtube.com/watch?v={}">{}</a> <a href="https://www.youtube.com/embed/{}"><img src="{}" alt="{}" /></a></li>'.format(x['realChanId'],x['realChanTitle'],x['snippet']['resourceId']['videoId'], x['snippet']['title'], x['snippet']['resourceId']['videoId'],x['snippet'].get('thumbnails',{}).get('standard',{}).get('url'),  x['snippet']['title']))
    print('</ul>')

if __name__ == "__main__":
    YOUTUBE = yt()
    listy = sys.argv[1:]
    fullist = {}
    pllist = []
    for i in listy:
        pllist = pllist + YOUTUBE.ytsearch(i)[0]
    pllist = sorted(list(set(pllist)))
    for i in pllist:
        fullist.update(filtbychan(YOUTUBE.taglist(YOUTUBE.call(i)[1]),listy))
    print_readable(fullist)
