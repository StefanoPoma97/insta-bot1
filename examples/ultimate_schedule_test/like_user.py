# -*- coding: utf-8 -*-
import random
import sys
import sys
sys.path.insert(0, "/home/stefanopoma97/bot//insta-bot1")
print(sys)
from glob import glob
import schedule
from instabot import Bot, utils
import os
import sys
import threading
import time
import config_file
from sys import argv

sys.path.append(os.path.join(sys.path[0], '../../'))

bot = Bot(comments_file=config_file.COMMENTS_FILE,
          blacklist_file=config_file.BLACKLIST_FILE,
          whitelist_file=config_file.WHITELIST_FILE,
          friends_file=config_file.FRIENDS_FILE,
          followed_file='followed.txt',
          unfollowed_file='unfollowed.txt',
          skipped_file='skipped.txt',
          proxy=None,
          max_likes_per_day=1000,
          max_unlikes_per_day=1000,
          max_follows_per_day=300,
          max_unfollows_per_day=350,
          max_comments_per_day=0,
          max_blocks_per_day=0,
          max_unblocks_per_day=0,
          max_likes_to_like=450,
          max_messages_per_day=0,
          filter_users=True,
          filter_previously_followed=False,
          filter_business_accounts=False,
          filter_verified_accounts=True,
          max_followers_to_follow=3500,
          min_followers_to_follow=40,
          max_following_to_follow=10000,
          min_following_to_follow=10,
          max_followers_to_following_ratio=10,
          max_following_to_followers_ratio=2,
          min_media_count_to_follow=3,
          max_following_to_block=2000,
          like_delay=1,
          unlike_delay=10,
          follow_delay=130,
          unfollow_delay=130,
          comment_delay=60,
          block_delay=30,
          unblock_delay=30,
          message_delay=60,
          stop_words=(),
          verbosity=True,
          )
bot.login(username="stefano.nature", password="maziamazia97")
bot.logger.info("LIKE USER SCRIPT")

f = open("hashtag_database.txt", 'r')
hashtag_file_like_list = [f.read().split('\n')]

random_user_file = utils.file(config_file.USERS_FILE)
random_hashtag_file_like = utils.file(config_file.HASHTAGS_FILE_LIKE)
random_hashtag_file_follow = utils.file(config_file.HASHTAGS_FILE_FOLLOW)
photo_captions_file = utils.file(config_file.PHOTO_CAPTIONS_FILE)
posted_pic_list = utils.file(config_file.POSTED_PICS_FILE).list

pics = sorted([os.path.basename(x) for x in
               glob(config_file.PICS_PATH + "/*.jpg")])


def stats():
    print("stats")
    #bot.save_user_stats(bot.user_id)


def like_hashtags():
    print("like_hashtag")
    bot.like_hashtag(random_hashtag_file_like.random(), amount=50)
    #bot.like_hashtag(random.choice(hashtag_file_like_list), amount=30)


def like_timeline():
    print("like_timeline")
    bot.like_timeline(amount=20)

def like_user_followers():
    print("like_user_followers")
    bot.like_followers(argv[1], nlikes=3)


def like_followers_from_random_user_file():
    print("like_from_hashtag")
    #bot.like_followers(random_user_file.random(), nlikes=3)


def follow_followers():
    print("follow")
    #bot.follow_followers(random_user_file.random(), nfollows=config.NUMBER_OF_FOLLOWERS_TO_FOLLOW)


def comment_medias():
    bot.comment_medias(bot.get_timeline_medias())


def unfollow_non_followers():
    print("unfollow")
    bot.unfollow_non_followers(n_to_unfollows=config_file.NUMBER_OF_NON_FOLLOWERS_TO_UNFOLLOW)

def unfollow_everyone():
    print("unfollow_everyone")
    # a = bot.delays
    # valore = a['unfollow']
    # a['unfollow'] = 100
    bot.unfollow_everyone()
    #a['unfollow'] = valore


def follow_users_from_hastag_file():
    print("follow da file hashtag")
    print(config_file.BLOCK)
    if config_file.BLOCK:
        print("non seguo nessuno")
    else:
        print("inizio a seguire")
        bot.follow_users(bot.get_hashtag_users(random_hashtag_file_follow.random())[:20])


def block_follow():
    print("blocca follow")
    config_file.BLOCK = True
    print(config_file.BLOCK)

def allow_follow():
    print("allow follow")
    config_file.BLOCK = False
    print(config_file.BLOCK)


def comment_hashtag():
    hashtag = random_hashtag_file_like.random()
    bot.logger.info("Commenting on hashtag: " + hashtag)
    bot.comment_hashtag(hashtag)


def upload_pictures():  # Automatically post a pic in 'pics' folder
    try:
        for pic in pics:
            if pic in posted_pic_list:
                continue

            caption = photo_captions_file.random()
            full_caption = caption + "\n" + config_file.FOLLOW_MESSAGE
            bot.logger.info("Uploading pic with caption: " + caption)
            bot.upload_photo(config_file.PICS_PATH + pic, caption=full_caption)
            if bot.api.last_response.status_code != 200:
                bot.logger.error("Something went wrong, read the following ->\n")
                bot.logger.error(bot.api.last_response)
                break

            if pic not in posted_pic_list:
                # After posting a pic, comment it with all the hashtags specified
                # In config.PICS_HASHTAGS
                posted_pic_list.append(pic)
                with open('pics.txt', 'a') as f:
                    f.write(pic + "\n")
                bot.logger.info("Succesfully uploaded: " + pic)
                bot.logger.info("Commenting uploaded photo with hashtags...")
                medias = bot.get_your_medias()
                last_photo = medias[0]  # Get the last photo posted
                bot.comment(last_photo, config_file.PICS_HASHTAGS)
                break
    except Exception as e:
        bot.logger.error("Couldn't upload pic")
        bot.logger.error(str(e))


def put_non_followers_on_blacklist():  # put non followers on blacklist
    try:
        bot.logger.info("Creating non-followers list")
        followings = set(bot.following)
        followers = set(bot.followers)
        friends = bot.friends_file.set  # same whitelist (just user ids)
        non_followers = followings - followers - friends
        for user_id in non_followers:
            bot.blacklist_file.append(user_id, allow_duplicates=False)
        bot.logger.info("Done.")
    except Exception as e:
        bot.logger.error("Couldn't update blacklist")
        bot.logger.error(str(e))


def put_following_in_whitelist():  # put non followers on blacklist
    try:
        bot.logger.info("Creating whitelist")
        followings = set(bot.following)
        for user_id in followings:
            bot.whitelist_file.append(user_id, allow_duplicates=False)
        bot.logger.info("Done.")
    except Exception as e:
        bot.logger.error("Couldn't update blacklist")
        bot.logger.error(str(e))

def run_threaded(job_fn):
    job_thread = threading.Thread(target=job_fn)
    job_thread.start()


like_user_followers()