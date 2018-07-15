import os
from random import randrange
from time import sleep
from .bot import basedir
from .follower import Follower


class Target:

    follow_limit = int(60*60 // 20)
    max_time = int(follow_limit * 1.5)
    min_time = int(follow_limit // 1.5)

    def __init__(self, target_id, api):
        self.id = target_id
        self.api = api

    def getFollowerList(self, force=False):
        if 'end_list' not in dir(self) or \
            self.end_list is True and \
            force is True:
                self.next_max_id = ''
                self.followers_stack = []
                self.end_list = False
        self.followers = []
        if self.end_list is False:
            self.api.getUserFollowers(self.id, self.next_max_id)
            temp = self.api.LastJson
            for user in temp['users']:
                self.followers.append(user['pk'])
            self.followers_stack.extend(self.followers)
        else: return
        if temp['big_list'] is False:
            self.next_max_id = ''
            self.end_list = True
        else:
            self.big_list = True
            self.next_max_id = temp['next_max_id']

    def followerListClean(self, force=False):
        if 'cache' not in dir(self) or force is True:
            self.cache = []
            passed = 0
            for file in (os.path.join('bot_data', 'user_fol'), os.path.join('bot_data', 'bad_user')):
                try:
                    with open(os.path.join(basedir, file), 'r') as f:
                        for cached_follower in f.readlines():
                            cached_follower = int(cached_follower)
                            self.cache.append(cached_follower)
                            if 'followers' not in dir(self):
                                self.getFollowerList()
                            for num, follower in enumerate(self.followers):
                                if follower == cached_follower:
                                    del self.followers[num]
                                    passed += 1
                except FileNotFoundError:
                        print('Bot data is clear.')
            print('passed in checker:', passed)

    def followerSelect(self, follower_id):
        self.follower = Follower(follower_id, self.api)

    def followingProtocol(self):
        while True:
            self.getFollowerList()
            self.followerListClean(force=True)
            if self.followers is []: break
            for follower_id in self.followers:
                self.followerSelect(follower_id)
                if self.follower.action() is True:
                    wait = randrange(self.min_time,self.max_time)
                    print('wait:', wait)
                    sleep(wait)
                else: sleep(randrange(1,10))
        print('end of list')
