# -*- coding: utf-8 -*-

from glob import glob
import schedule
from instabot import Bot, utils
import os
import sys
import threading
import time
import config
from sys import argv

sys.path.append(os.path.join(sys.path[0], '../../'))

bot = Bot(comments_file=config.COMMENTS_FILE,
          blacklist_file=config.BLACKLIST_FILE,
          whitelist_file=config.WHITELIST_FILE,
          friends_file=config.FRIENDS_FILE,
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
bot.logger.info("ULTIMATE script. Safe to run 24/7!")

random_user_file = utils.file(config.USERS_FILE)
random_hashtag_file_like = utils.file(config.HASHTAGS_FILE_LIKE)
random_hashtag_file_follow = utils.file(config.HASHTAGS_FILE_FOLLOW)
photo_captions_file = utils.file(config.PHOTO_CAPTIONS_FILE)
posted_pic_list = utils.file(config.POSTED_PICS_FILE).list

pics = sorted([os.path.basename(x) for x in
               glob(config.PICS_PATH + "/*.jpg")])


def stats():
    print("stats")
    #bot.save_user_stats(bot.user_id)


def like_hashtags():
    print("like_hashtag")
    bot.like_hashtag(random_hashtag_file_like.random(), amount=30)


def like_timeline():
    print("like_timeline")
    bot.like_timeline(amount=20)


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
    bot.unfollow_non_followers(n_to_unfollows=config.NUMBER_OF_NON_FOLLOWERS_TO_UNFOLLOW)

def unfollow_everyone():
    print("unfollow_everyone")
    # a = bot.delays
    # valore = a['unfollow']
    # a['unfollow'] = 100
    bot.unfollow_everyone()
    #a['unfollow'] = valore


def follow_users_from_hastag_file():
    print("follow da file hashtag")
    print(config.BLOCK)
    if config.BLOCK:
        print("non seguo nessuno")
    else:
        print("inizio a seguire")
        bot.follow_users(bot.get_hashtag_users(random_hashtag_file_follow.random()))


def block_follow():
    print("blocca follow")
    config.BLOCK = True
    print(config.BLOCK)

def allow_follow():
    print("allow follow")
    config.BLOCK = False
    print(config.BLOCK)


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
            full_caption = caption + "\n" + config.FOLLOW_MESSAGE
            bot.logger.info("Uploading pic with caption: " + caption)
            bot.upload_photo(config.PICS_PATH + pic, caption=full_caption)
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
                bot.comment(last_photo, config.PICS_HASHTAGS)
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


if (argv[1] == "print"):
    schedule.every(1).hour.do(run_threaded, stats)
    schedule.every().sunday.at("12:01").do(run_threaded, block_follow)
    schedule.every().sunday.at("12:02").do(run_threaded, follow_users_from_hastag_file)
    schedule.every().sunday.at("12:03").do(run_threaded, allow_follow)
    schedule.every().sunday.at("12:04").do(run_threaded, follow_users_from_hastag_file)
    while True:
        schedule.run_pending()
        time.sleep(1)

if (argv[1] == "whitelist"):
    print("creo whitelist")
    put_following_in_whitelist()

if (argv[1] == "hash"):
    print("Seguo utenti da file hashtag")   #prendo da limite giornaliero e delay adeguato
    follow_users_from_hastag_file()

if (argv[1] == "unfollowall"):   #impostare il delay e il limite giornaliero
    print("unfollow everyone")
    unfollow_everyone()

if (argv[1] == "unfollow"):   #limite da settare nel file config
    print("unfollow chi non mi segue")
    unfollow_non_followers()

if (argv[1] == "liketimeline"):
    print("like a timeline")
    like_timeline()

if (argv[1] == "like"):
    print("like from hashtag")
    like_hashtags()


if (argv[1] == "all"):
    schedule.every(1).hour.do(run_threaded, stats)
    schedule.every(65).minutes.do(run_threaded, like_hashtags)  #amount=30 delay=1 max_a_day=1000
    schedule.every(110).minutes.do(run_threaded, like_timeline)  #amount=20 delay=1 max_a_day=1000
    # 30*24=720  20*12=240  960 in total
    schedule.every(1).hours.do(run_threaded, follow_users_from_hastag_file)  #delay=60 max_a_day=300  (20 a volta)
    # 20*24= 480 (raggiunge i 300 dopo 15 ore circa)
    schedule.every().friday.at("1:05").do(run_threaded, block_follow)

    schedule.every().friday.at("18:07").do(run_threaded, unfollow_non_followers)  # amount=50 delay=130
    schedule.every().friday.at("20:04").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().friday.at("22:15").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().friday.at("23:58").do(run_threaded, unfollow_non_followers)  # amount=50

    schedule.every().saturday.at("00:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("2:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("4:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("6:33").do(run_threaded, unfollow_non_followers)   #amount=50
    schedule.every().saturday.at("8:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("10:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("12:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("14:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("16:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("18:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("20:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().saturday.at("22:33").do(run_threaded, unfollow_non_followers)  # amount=50

    schedule.every().sunday.at("00:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("2:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("4:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("6:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("8:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("10:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("12:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("14:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("16:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("18:33").do(run_threaded, unfollow_non_followers)  # amount=50
    schedule.every().sunday.at("20:33").do(run_threaded, unfollow_everyone)    # amount=50
    schedule.every().sunday.at("21:53").do(run_threaded, unfollow_everyone)
    schedule.every().sunday.at("23:13").do(run_threaded, unfollow_everyone)
    schedule.every().sunday.at("23:59").do(run_threaded, unfollow_everyone)
    schedule.every().sunday.at("1:33").do(run_threaded, unfollow_everyone)
    schedule.every().sunday.at("3:33").do(run_threaded, unfollow_everyone)
    schedule.every().sunday.at("4:33").do(run_threaded, unfollow_everyone)
    schedule.every().sunday.at("6:33").do(run_threaded, unfollow_everyone)
    #1700 unfollow in totale

    schedule.every().monday.at("1:05").do(run_threaded, allow_follow)





    while True:
        schedule.run_pending()
        time.sleep(1)


if (argv[1] == "day"):
    schedule.every(1).hour.do(run_threaded, stats)
    like_hashtags()
    like_timeline()
    follow_users_from_hastag_file()
    schedule.every(65).minutes.do(run_threaded, like_hashtags)  # amount=30 delay=60 max_a_day=1000
    schedule.every(113).minutes.do(run_threaded, like_timeline)  # amount=20 delay=60 max_a_day=1000
    schedule.every(1).hours.do(run_threaded, follow_users_from_hastag_file)  #25 ogni volta


    while True:
        schedule.run_pending()
        time.sleep(1)
