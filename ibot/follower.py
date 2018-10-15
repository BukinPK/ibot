import os
import numpy as np
from random import randrange
from time import sleep
import json
from datetime import datetime
from .bot import basedir


class Follower:
    
    like_wait = 5
    all_likes = None

    def __init__(self, follower_id, api):
        self.id = follower_id
        self.api = api

    def __getattr__(self, item):
        return None

    def getInfo(self):
        if self.api.getUsernameInfo(self.id):
            self._info = self.api.LastJson['user']
            return self._info
        else:
            self.info_error = True
            return False


    @property
    def info(self):
        if not self._info:
            self.getInfo()
        return self._info

    @property
    def username(self):
        if self.info:
            return self.info['username']

    def getFeed(self):
        if self.api.getUserFeed(self.id, maxid=self.maxid):
            self._feed = self.api.LastJson
            return self._feed
        else:
            self.feed_error = True
            return False
        
    @property
    def feed(self):
        if not self._feed:
            self.getFeed()
        return self._feed

    def print_info(self):
        print(json.dumps(self.info, indent=2))

    def print_feed(self):
        print(json.dumps(self.feed, indent=2))

    def checkInfo(self):
        if self.info['media_count'] <= 1:
            self.is_media_homeless = True
        else:
            self.is_media_homeless = False
        if self.info['follower_count'] > self.info['following_count'] * 3:
            self.is_attention_whore = True
        else:
            self.is_attention_whore = False
        if self.info['follower_count'] * 3 < self.info['following_count']:
            self.is_shit_eater = True
        else:
            self.is_shit_eater = False
        #self.is_business = self.info['is_business']
        self.is_private = self.info['is_private']
        self.media_count = self.info['media_count']
        self.follower_count = self.info['follower_count']
        self.following_count = self.info['following_count']
        if self.follower_count > 1000 or self.following_count > 1000:
            self.activity_overload = True
        else:
            self.activity_overload = False

        if self.is_media_homeless is True or \
            self.is_attention_whore is True or \
            self.is_shit_eater is True or \
            self.activity_overload is True: # or \
            #self.is_business is True:
                with open(os.path.join(basedir, 'bot_data', 'bad_user'), 'a') as f:
                    f.write(str(self.id) + '\n')
                return False
        else:
            return True

    def getFriendship(self):
        if self.api.userFriendship(self.id):
            self.friendship = self.api.LastJson
            return True
        else:
            self.friendship = None
            self.friendship_error = True
            return False

    def checkFriendship(self, unfollowing=False):
        if not self.getFriendship():
            return False
        self.followed_by = self.friendship['followed_by']
        criterions = ('followed_by', 'following', 'outgoing_request')
        if unfollowing:
            criterions = ('following', 'outgoing_request')
        for criterion in criterions:
            try:
                if self.friendship[criterion] is True:
                    self.is_friend = True
                    return True
                continue
            except KeyError as ex:
                print('Unknown error:', ex)
            self.is_friend = False
            return False
            
    def follow(self):
        self.api.follow(self.id)
        with open(os.path.join(basedir, 'bot_data', 'user_fol'), 'a') as f:
            f.write(str(self.id)+'\n')

    def randomPicLike(self):
        while True:
            like_count = randrange(1,4)
            pic_count = self.feed['num_results']
            if like_count <= pic_count:
                self._liked = []
                break
        for like in range(like_count):
            media_number = randrange(0, pic_count)
            media_choice = self.feed['items'][media_number]
            if media_choice['has_liked'] is True:
                continue
            else: 
                picture_id = media_choice['pk']
                self.api.like(picture_id)
                with open(os.path.join(basedir, 'bot_data', 'pic_like'), 'a') as f:
                    f.write(str(picture_id) + '\n')
                sleep(randrange(2, self.like_wait))
                self._liked.append(media_number+1)

    def action(self):
        if self.checkFriendship() is True:
            print('is friend [%s]' % self.username)
            return False
        if self.checkInfo() is False:
            print('bad info [%s]:' % self.username, end=' ')
            if self.is_attention_whore:
                print('whore', end=' ') 
            if self.is_media_homeless:
                print('homeless', end=' ') 
            #if self.is_business:
            #   print('business', end=' ') 
            if self.is_shit_eater:
                print('shit_eater', end=' ') 
            if self.activity_overload:
                print('activity_overload', end=' ') 
            print()
            return False
        if self.is_private is False:
            self.randomPicLike()
            print('pic liked:', self.liked, end=' ')
        else:
            print('no pic liked, is private', end=' ')
            sleep(randrange(2, self.like_wait))
        self.follow()
        print('following [%s]' % self.username)
        self.is_friend = True
        return True

    def getLiked(self):
        if self.getFeed():
            self._liked = []
            for pic in self.feed['items']:
                if pic['has_liked']:
                    self._liked.append(pic['pk'])
            return self._liked
        else:
            self._liked = None
            return None

    @property
    def liked(self):
        if not self._liked:
            self.getLiked()
        return self._liked

    def getAllLikes(self):
        with open(os.path.join(basedir, 'bot_data', 'pic_like'), 'r') as f:
            all_likes = f.readlines()
        self.all_likes = np.array(all_likes, dtype='int64')

    def unlike(self, pages=9):
        if self.all_likes is None:
            self.getAllLikes()
        self.unlikes = []
        for page in range(pages):
            self.content_lists = page+1
            if self.getLiked() is None:
                return True
            for like in self.liked:
                if like in self.all_likes:
                    self.api.unlike(like)
                    with open(os.path.join(basedir, 'bot_data',
                                           'pic_unlike'), 'a') as f:
                        f.write(str(like) + '\n')
                        self.unlikes.append([pic['pk'] for pic in \
                            self.feed['items']].index(like)+1 + 18*page)
                    sleep(randrange(2, self.like_wait))
                else:
                    print(f'I liked [{like}] of user: {self.username}', end=', ')
                    with open(os.path.join(basedir, 'bot_data',
                                           'user_unfol_exceptions'), 'a') as f:
                        f.write(str(self.id) + '\n')
                    return False
            if self.feed.get('more_available'):
                self.maxid = self.feed['next_max_id']
            else:
                self.maxid = ''
                return True
        return True
                

    def unfollow(self):
        if self.checkFriendship(unfollowing=True) is False:
            print('is not friend: %s [%s]' % (self.username, self.id))
            with open(os.path.join(basedir, 'bot_data',
                                   'user_unfol'), 'a') as f:
                f.write(str(self.id) + '\n')
                print('delete from base: %s [%s]' % (self.username, self.id))
                if self.unlike():
                    print('deleted %s [%s], unlikes: %s, content lists: %s, my follower: %s' % (
                          self.username, self.id,
                          self.unlikes, self.content_lists,
                          self.followed_by))
            return False
        if self.unlike():
            self.api.unfollow(self.id)
            with open(os.path.join(basedir, 'bot_data',
                                   'user_unfol'), 'a') as f:
                f.write(str(self.id) + '\n')
                print('unfollow: %s [%s],' % (self.username, self.id), end=' ')
        print('unlikes: %s, content lists: %s, my follower: %s' % (
            self.unlikes, self.content_lists, self.followed_by))
        if True in (self.info_error, self.feed_error, self.friendship_error):
            print('^ got error in process ^')
        return True
