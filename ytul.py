#!/usr/bin/env python3

import sys
import config
import googleapiclient.discovery
import pprint

class yt:
    def __init__(self):
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = config.ytkey
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)
        self.scache = {}
        self.pcache = {}
        self.vcache = {}

    def call(self, plid, npt=None):
        if npt is None and plid in self.pcache:
            return self.pcache[plid]
        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=plid,
            maxResults=50,
            pageToken=npt
        )
        response = request.execute()
        mines = response['items']
        if response.get('nextPageToken'):
            mines = mines + self.call(plid, response['nextPageToken'])
        if npt is None:
            self.pcache[plid] = mines
        return mines
    def details(self, vids):
        request = self.youtube.videos().list(
            part="snippet",
            id=",".join(vids)
        )
        response = request.execute()
        return {x['id']: (x['snippet'].get('channelId'), x['snippet'].get('channelTitle')) for x in response['items']}

    def all_details(self, vids):
        vids = sorted(list(set(vids)))
        result = {}
        for v in vids:
            if v in self.vcache:
                result[v] = self.vcache[v]
                vids.remove(v)
        multivids = [vids[i:i+50] for i in range(0, len(vids), 50)]
        for sub in multivids:
            result.update(self.details(sub))
        self.vcache.update(result)
        return result


    def taglist(self, pl):
        vids = [x['snippet']['resourceId']['videoId'] for x in pl]
        alldets = self.all_details(vids)
        newdict = {}
        for x in pl:
            x['realChanTitle'] = alldets.get(x.get('snippet',{}).get('resourceId',{}).get('videoId'),[None, None])[1]
            x['realChanId'] = alldets.get(x.get('snippet',{}).get('resourceId',{}).get('videoId'),[None, None])[0]
            newdict[x['snippet']['resourceId']['videoId']] = x
        return newdict

    def ytsearch(self, string):
        if string in self.scache:
            return self.scache[string]
        request = self.youtube.search().list(
                part='id',
                maxResults=50,
                q=string,
                type='playlist',
                safeSearch='none'
                )
        response = request.execute()
        answer =  [x['id']['playlistId'] for x in response['items']]
        self.scache[string] = answer
        return answer

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
        pllist = pllist + YOUTUBE.ytsearch(i)
    pllist = sorted(list(set(pllist)))
    for i in pllist:
        fullist.update(filtbychan(YOUTUBE.taglist(YOUTUBE.call(i)),listy))
    print_readable(fullist)
