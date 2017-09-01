# -*- coding:utf-8 -*-
import keys
import tweepy
import facebook
import re
import urllib.request

auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)
api = tweepy.API(auth)

graph = facebook.GraphAPI(access_token=keys.facebook_token)
profile = graph.get_object(id='ramenberavo')
recentId = -1

class MyStreamListener( tweepy.StreamListener ):
    def on_status( self, status ):
        checkTweet( status )
    def on_error( self,status_code ):
        if status_code == 420:
            return False

def checkTweet( status ):
    try:
        tweetFilter = re.compile(u"^@ymfact\s*(베라보우?)?\s*특선봇?$")
        if( tweetFilter.match( status.text ) ):
            post = getPost()
            if( post ):
                tweetSuccess( status, post )
            else:
                tweetFailed( status )
                
    except Exception as e:
        print ( e.args[0] )

def getPost():
    global recentId
    
    data = graph.get_connections(profile['id'], connection_name='posts', fields='id,link,message,full_picture')
    posts = data['data']
    for post in posts:
        if( post['id'] == recentId ):
            return post
        if( isContainKeywords( post['message'] ) ):
            recentId = post['id']
            return post
    return None
        
def isContainKeywords( string ):
    return (u"특선" in string) and (u"효자점" in string)

def tweetSuccess( tweet, post ):
    fileName = "beravo.jpg"
    urllib.request.urlretrieve( post['full_picture'], fileName )
    status = post['message'][:113] + "...\n" + post['link']
    api.update_with_media( filename=fileName, status=status, in_reply_to_status_id=tweet.id )

def tweetFailed( tweet ):
    status = u"특선 검색에 실패했습니다."
    api.update_status( status=status, in_reply_to_status_id=tweet.id )

myStreamListener = MyStreamListener()
myStream = tweepy.Stream( auth = api.auth, listener=myStreamListener )
myStream.userstream( encoding='utf8', async=True )

