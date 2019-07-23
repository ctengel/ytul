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

    def call(self, plid, npt=None):
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
        multivids = [vids[i:i+50] for i in range(0, len(vids), 50)]
        result = {}
        for sub in multivids:
            result.update(self.details(sub))
        return result


    def taglist(self, pl):
        vids = [x['snippet']['resourceId']['videoId'] for x in pl]
        alldets = self.all_details(vids)
        for x in pl:
            x['realChanTitle'] = alldets.get(x.get('snippet',{}).get('resourceId',{}).get('videoId'),[None, None])[1]
            x['realChanId'] = alldets.get(x.get('snippet',{}).get('resourceId',{}).get('videoId'),[None, None])[0]
        return pl    

def filtbychan(pl, by):
    return [x for x in pl if x['realChanTitle'] in by or x['realChanId'] in by]

def print_readable(pl):
    for x in pl:
        print("{}\t{}\t{}\t{}\t{}\t{}".format(x['realChanId'],x['realChanTitle'],x['snippet']['resourceId']['videoId'], x['snippet']['title'], x['snippet']['publishedAt'], x['snippet'].get('thumbnails',{}).get('standard',{}).get('url')))

if __name__ == "__main__":
    YOUTUBE = yt()
    print_readable(filtbychan(YOUTUBE.taglist(YOUTUBE.call(sys.argv[1])),sys.argv[2:]))
