#!/usr/bin/python3
import time
import requests
import random
from bs4 import BeautifulSoup
import os
import json
import platform
import re
import sys
from subprocess import call
import datetime
import configparser

version = "1.4.4"
os.chdir(os.path.dirname(os.path.realpath(__file__)))

random.seed(os.urandom)

#determine was script installed by apt-package or was clonned via git clone
if os.path.exists('./settings.cfg'):
    additional_path_for_conf = ""
else:
    additional_path_for_conf = "/etc/steam_gifts/"


def check_new_version(ver):
    """Function for check new version of this script"""
    try:
        if requests.get("https://raw.githubusercontent.com/4815162342lost/steam_gifts_bot/master/version").text.rstrip() == ver:
            print(f"You are using the latest version of the program. Your version: {ver}")
        else:
            print(
                "New version is avaliable!\nPlease, visit https://github.com/4815162342lost/steam_gifts_bot and install new version")
            print("What's new:")
            print(
                requests.get("https://raw.githubusercontent.com/4815162342lost/steam_gifts_bot/master/whats_new").text)
    except:
        print("Can not check new version. Github is not available or internet connection is not working!")


def get_settings():
    """Function for read settings from settings.cfg file"""
    conf = configparser.ConfigParser()
    conf.optionxform=str
    conf.read(additional_path_for_conf + 'settings.cfg')
    return conf


def get_requests(cookie, req_type, headers):
    """Main function for raise other functions"""
    print(f"Working with {req_type} giveaways")
    def do_requests(cookie, headers, start_link="https://www.steamgifts.com/giveaways/search?page=", end_link="", page_number = 1):
        """Function for do get requests, decide does next page exist or not and raise next functions for enter to giveaways"""
        while True:
            try:
                r = requests.get(f"{start_link}{page_number}{end_link}",cookies=cookie, headers=headers)
                get_game_links(r)
                if r.text.find("Next") == -1 or type(page_number) != int:
                    break
                page_number += 1
                time.sleep(random.randint(3, 14))
            except:
                print("Site is not available")
                time.sleep(300)
                break
    if req_type == "wishlist" or req_type=="group":
        do_requests(cookie, headers, end_link=f"&type={req_type}")
    elif req_type == "search_list":
        for current_search in what_search:
            print(f"Search giveaways which contain: {current_search}")
            do_requests(cookie, headers, end_link=f"&q={current_search}")
            time.sleep(random.randint(8, 39))
    elif req_type == "random_list" and get_coins() > threshold:
        time.sleep(random.randint(5, 11))
        do_requests(cookie, headers, start_link="https://www.steamgifts.com/", page_number="")
    elif req_type == "enteredlist":
        print("Trying to receive already entered giveaways...")
        entered_list = []
        page_number = 1
        while True:
            try:
                r = requests.get(f"https://www.steamgifts.com/giveaways/entered/search?page={page_number}", cookies=cookie, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                links = soup.find_all(class_="table__row-inner-wrap")
                for get_link in links:
                    url = get_link.find(class_="table__column__heading").get("href")
                    check_geaways_end = get_link.find(class_="table__remove-default is-clickable")
                    if check_geaways_end != None:
                        entered_list.append(url)
                    elif get_link.find(class_="table__column__deleted") != None:
                        continue
                    else:
                        return entered_list
                page_number += 1
                time.sleep(random.randint(3, 7))
            except Exception as e:
                print(f"Can not get entered list due to exception: {e}")
                time.sleep(300)
                return entered_list


def get_game_links(requests_result):
    """call enter_geaways and extract link"""
    soup = BeautifulSoup(requests_result.text, "html.parser")
    link = soup.find_all(class_="giveaway__heading__name")
    for get_link in link:
        geaway_link = get_link.get("href")
        if geaway_link not in entered_url:
            if not need_giveaways_from_banners and geaway_link in giveaways_from_banner:
                continue
            entered_url.append(geaway_link)
            geaway_link = "https://www.steamgifts.com" + geaway_link
            print(f"Working with link: {geaway_link}")
            if geaway_link not in bad_giveaways_link:
                if enter_geaway(geaway_link):
                    break
            else:
                print(f"Giveaway url on black list: {geaway_link[geaway_link.rfind('/') + 1:]}")


def enter_geaway(geaway_link):
    """enter to giveaway"""
    global i_want_to_sleep
    bad_counter = good_counter = 0
    try:
        r = requests.get(geaway_link, cookies=cookie, headers=headers)
        if r.status_code != 200:
            set_notify("Site error", f"Error code: {r.status_code}", separator=". ")
            time.sleep(300)
            return False
    except:
        print("Site is not available...")
        time.sleep(300)
        return False
    soup_enter = BeautifulSoup(r.text, "html.parser")
    for bad_word in forbidden_words:
        bad_counter += len(re.findall(bad_word, r.text, flags=re.IGNORECASE))
    if bad_counter > 0:
        for good_word in good_words:
            good_counter += len(re.findall(good_word, r.text, flags=re.IGNORECASE))
        if bad_counter > good_counter:
            print("It is a trap! Be carefully! Bad people want destroy my script!")
            do_beep("bad_words")
            with open("bad_giveaways.txt", "a") as bad_giveaways:
                bad_giveaways.write(geaway_link + "\n")
            return False
        if bad_counter == good_counter:
            set_notify("False alarm", f"All nice. Giveaway link: {geaway_link}", separator="! ")
    try:
        game = soup_enter.title.string
    except:
        game = "Unknown game"
    if game in bad_games_name:
        print(f"Game from blacklist. Ignore: {game} game")
        return False
    try:
        link = soup_enter.find(class_="sidebar").form
    except Exception as e:
        print(f"Unknown error: {e}")
        return False
    if link != None:
        link = link.find_all("input")
        params = {"xsrf_token": link[0].get("value"), "do": "entry_insert", "code": link[2].get("value")}
        try:
            r = requests.post("https://www.steamgifts.com/ajax.php", data=params, cookies=cookie, headers=headers)
            extract_coins = json.loads(r.text)
        except:
            print("Site is not available...")
            time.sleep(300)
            return False
        if extract_coins["type"] == "success":
            coins = extract_coins["points"]
            set_notify("Bot entered to giveaway with game: ", re.sub("&", '', game) + f". Coins left: {coins}", separator="")
            time.sleep(random.randint(1, 120))
            return False
        elif extract_coins["msg"] == "Not Enough Points":
            coins = get_coins()
            if coins < 10:
                i_want_to_sleep = True
                print(f"Not enough coins to enter to {geaway_link}")
                return True
            return False
    else:
        link = soup_enter.find(class_="sidebar__error is-disabled")
        if link != None and link.get_text() == " Not Enough Points":
            print(f"Not enough points to enter to {geaway_link}")
            time.sleep(random.randint(5, 60))
            if get_coins() < 10:
                i_want_to_sleep = True
                return True
        else:
            link = soup_enter.select("div.featured__column span")
            if link != None:
                print(f"Giveaway was ended. Bot has late to enter giveaway: {geaway_link}. Was ended: {link[0].text}")
                time.sleep(random.randint(5, 60))
                return False
            else:
                set_notify("Critical error!", f"Link: {link}", separator="")
                do_beep("critical")
                return False
        return False


def get_coins():
    """How many coins do we have?"""
    try:
        soup = BeautifulSoup(requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers).text, "html.parser")
        coins = int(soup.find(class_="nav__points").string)
        return coins
    except Exception as e:
        print(f"Can not get cookies count... Exception: {e}")
        time.sleep(300)
        return 0


def set_notify(head, text, separator="\n"):
    """Set notify only on Linux. If non-Linux or you do want to receive notification just print it to console"""
    print(head, text, sep=separator)
    if need_send_notify and platform.system() == "Linux":
        try:
            notify2.init('Steam_gifts_bot')
            n = notify2.Notification(head, text)
            n.set_timeout(15000)
            n.set_icon_from_pixbuf(pb)
            n.show()
        except Exception as e:
            print(f"Can not send the notification: {e}")


def work_with_win_file(need_write, count):
    """Function for read drom file or write to file won.txt"""
    with open('won.txt', 'r+') as read_from_file:
        if not need_write:
            count = read_from_file.read()
            return count
        else:
            read_from_file.seek(0)
            read_from_file.write(str(count))

def check_won(count):
    """Check new won giveaway"""
    try:
        r = requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser").find(class_="nav__right-container").find_all("a")[1].find(
            class_="nav__notification").string
    except:
        print("You did not win giveaways... But do not worry. Will luck next time!")
        work_with_win_file(True, 0)
        return 0
    if int(count) < int(soup):
        do_beep("won")
        set_notify("Congratulations! You won!", "Take your prize on website", separator=" ")
        work_with_win_file(True, soup)
        return soup
    elif int(count) > int(soup):
        work_with_win_file(True, soup)
        return soup
    return count


def do_beep(reason):
    """do beep with PC speaker. Work only on Linux and requirement motherboard speaker"""
    if not need_beep:
        return 0
    if (datetime.datetime.now().time().hour < 9 or datetime.datetime.now().time().hour > 22) and silent_mode_at_night:
        print("Not beep, because night")
        return 0
    if platform.system() == "Linux" or platform.system() == "FreeBSD":
        if reason == "coockie_exept":
            call(["beep", "-l 2000", "-f 1900", "-r 3"])
        elif reason == "critical":
            call(["beep", "-l 1000", "-r 10", "-f 1900"])
        elif reason == "won":
            os.system("./win.sh")
        elif reason == "bad_words":
            call(["beep", "-l 300", "-r 30", "-f 1900"])


def get_games_from_banners():
    try:
        soup = BeautifulSoup(requests.get("https://www.steamgifts.com/", cookies=cookie, headers=headers).text,
                             "html.parser")
        banners = soup.find(class_="pinned-giveaways__inner-wrap pinned-giveaways__inner-wrap--minimized").find_all(
            class_="giveaway__heading__name")
        for games in banners:
            if games not in giveaways_from_banner:
                giveaways_from_banner.append(games.get("href"))
                print(f"You will never win the game {games.get('href')}, because you have refused to enter giveaways from banner...")
    except Exception as e:
        print(f"Can not get games from banners...Exception: {e}")


print("I have started...\nHave a nice day!")
time.sleep(60)
func_list = []

#let's check is new version available
check_new_version(version)

#get settings from settings.cfg file and initialize the variables
settings=get_settings()
cookie = dict(settings._sections['cookies'])
headers = dict(settings._sections['user-agent'])

need_send_notify = int(settings['settings']['send_notify'])
need_giveaways_from_banners = int(settings['settings']['giveaways_from_banners'])
threshold = int(settings['settings']['threshold'])
need_beep = int(settings['settings']['beep'])
silent_mode_at_night = int(settings['settings']['silent_mode_at_night'])

temporary_tuple = ("wishlist", "search_list", "group", "random_list")
for current_temporary_tuple in temporary_tuple:
    if int(settings['settings'][current_temporary_tuple]):
        func_list.append(current_temporary_tuple)

if platform.system() == "Linux" and need_send_notify:
    try:
        import notify2
        import gi
        gi.require_version('GdkPixbuf', '2.0')
        from gi.repository.GdkPixbuf import Pixbuf
        pb = Pixbuf.new_from_file("icon.png")
    except Exception as e:
        print(f'Can not initialize variables for send notification due to exceprtion: {e}')
elif platform.system() == "Windows":
    os.system("Chcp 65001")


#test cookies
try:
    r = requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
except:
    set_notify("Cookies expired", "Please update your cookies")
    do_beep("coockie_exept")
    sys.exit(1)

#read various variables from files
with open(additional_path_for_conf + "search.txt") as f: what_search = f.read().splitlines()
with open(additional_path_for_conf + "black_list_games_name.txt") as f: bad_games_name = f.read().splitlines()
with open("bad_giveaways_link.txt") as f: bad_giveaways_link = f.read().splitlines()

#sleep and get currnt count of coins
time.sleep(random.randint(2, 10))
coins = get_coins()

entered_url = get_requests(cookie, "enteredlist", headers)
# func_list=("wishlist", "search", "someone")
won_count = work_with_win_file(False, 0)
set_notify("Steam gifts bot has started", f"Total coins: {coins}")
forbidden_words = (" ban", " fake", " bot", " not enter", " don't enter")
good_words = (" bank", " banan", " both", " band", " banner", " bang")
giveaways_from_banner = []
if not need_giveaways_from_banners:
    get_games_from_banners()
while True:
    if not need_giveaways_from_banners:
        get_games_from_banners()
    i_want_to_sleep = False
    for current_func_list in func_list:
        get_requests(cookie, current_func_list,headers)
        if i_want_to_sleep:
            set_notify("Coins are too low...", "", separator="")
            break
    won_count = check_won(won_count)
    sleep_time = random.randint(1800, 3600)
    coins = get_coins()
    if not i_want_to_sleep:
        set_notify("I entered to all giveaways...",  f"Coins left: {coins}")
    set_notify(f"I am going to sleep for {str(sleep_time // 60)} min.", f"Coins left: {coins}", separator=" ")
    time.sleep(sleep_time)
