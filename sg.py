#!/usr/bin/python3
import time
import requests
import random
from bs4 import BeautifulSoup
import os
import json
import platform
import re

version="1.2.9"
os.chdir(os.path.dirname(os.path.realpath(__file__)))
if platform.system()=="Linux":
	import notify2
	import gi
	gi.require_version('GdkPixbuf', '2.0') 
	from gi.repository.GdkPixbuf import Pixbuf
	pb=Pixbuf.new_from_file("icon.png")
import sys
from subprocess import call
import datetime
if platform.system()=="Windows":
	os.system("Chcp 65001")

def check_new_version(ver):
	try:
		if requests.get("https://raw.githubusercontent.com/4815162342lost/steam_gifts_bot/master/version").text.rstrip("\n")==ver:
			print("You are using the latest version of the program. You version:", version)
		else:
			print("New version avaliable!\nPlease, visit https://github.com/4815162342lost/steam_gifts_bot and update you bot")
			print("What's new:")
			print(requests.get("https://raw.githubusercontent.com/4815162342lost/steam_gifts_bot/master/whats_new").text)
	except:
		print("Can not check new version. Github not available or internet are not working")

def get_from_file(file_name):
	"""read data from files"""
	result={}
	exec(open(file_name).read(), None, result)
	return result

def get_user_agent():
	"""read user agent from user_agent.txt"""
	with open("user_agent.txt") as user_agent_from_file:
		user_agent=user_agent_from_file.readline()
		return user_agent

def get_func_list():
	"""Set necessary parameters (what type of the giveaways, need beep or not, debug mode or not, need notify or not)"""
	global sc_need; global need_giveaways_from_banners
	global need_send_notify; global need_beep
	global debug_mode; global threshold
	global silent_mode_at_night;
	if settings_list["wishlist"]:
		func_list.append("wishlist")
	if settings_list["search_list"]:
		func_list.append("search")
	if settings_list["random_list"]:
		func_list.append("someone")
	if settings_list["steam_companion_bot"]:
		sc_need=1
	if settings_list["giveaways_from_banners"]:
		need_giveaways_from_banners=1
	if settings_list["send_notify"]:
		need_send_notify=1
	if settings_list["beep"]:
		need_beep=1
	if settings_list["debug_mode"]:
		debug_mode=1
	threshold=settings_list["threshold"]
	silent_mode_at_night = settings_list["silent_mode_at_night"]


def get_requests(cookie, req_type):
	"""get first page"""
	global chose
	if req_type=="wishlist":
		print("Working with wishlist...")
		page_number=1
		need_next=True
		while need_next:
			try:
				r=requests.get("https://www.steamgifts.com/giveaways/search?page="+str(page_number)+"&type=wishlist", cookies=cookie, headers=headers)
				get_game_links(r)
				need_next = get_next_page(r)
				page_number += 1
			except:
				print("Site not avaliable")
				time.sleep(300)
				chose=0
				break
	elif req_type=="search":
		print("Working with search list")
		for current_search in what_search.values():
			debug_messages("Search giveaways contains "+str(current_search))
			page_number=1
			need_next=True
			while need_next:
				try:
					r=requests.get("https://www.steamgifts.com/giveaways/search?page="+str(page_number)+"&q="+str(current_search), cookies=cookie, headers=headers)
					get_game_links(r)
					need_next=get_next_page(r)
					page_number+=1
					time.sleep(random.randint(3, 7))
				except:
					print("Site not avaliable")
					chose=0
					time.sleep(300)	
					break
			time.sleep(random.randint(8,39))
	elif req_type=="enteredlist":
		debug_messages("Geting entered list")
		entered_list=[]
		page_number=1
		while nedd_next_page_for_entered_link:
			try:
				r=requests.get("https://www.steamgifts.com/giveaways/entered/search?page="+str(page_number), cookies=cookie, headers=headers)
				entered_list.extend(get_entered_links(r))
				page_number+=1
			except:
				print("Site not avaliable")
				chose=0
				time.sleep(300)	
				break
			debug_messages("return entered list...")
		return entered_list
	elif req_type=="someone" and int(get_coins(get_requests(cookie, "coins_check")))>int(threshold):
		print("Working with random giveaways...")
		time.sleep(random.randint(5,11))
		try:
			r=requests.get("https://www.steamgifts.com/", cookies=cookie, headers=headers)
			get_game_links(r)
		except:
			print("Site not avaliable...")
			chose=0
			time.sleep(300)
	elif req_type=="coins_check":
		try:
			r=requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
			return r
		except:
			print("Site not avaliable...")
			chose=0
			time.sleep(300)
			return 0

def get_game_links(requests_result):
	"""call enter_geaways and extract link"""
	soup=BeautifulSoup(requests_result.text, "html.parser")
	link=soup.find_all(class_="giveaway__heading__name")
	for get_link in link:
		geaway_link=get_link.get("href")
		if not geaway_link in entered_url:
			if not need_giveaways_from_banners and geaway_link in giveaways_from_banner:
				continue
			entered_url.append(geaway_link)
			geaway_link="https://www.steamgifts.com" + geaway_link
			debug_messages(geaway_link)
			if geaway_link not in bad_giveaways_link:
				if enter_geaway(geaway_link):
					break
			else:
				debug_messages("giveaway in blacklist. Ignore")
				set_notify("Giveaway url on black list, ignore", geaway_link[geaway_link.rfind("/")+1:])
def enter_geaway(geaway_link):
	"""enter to geaways"""
	global i_want_to_sleep
	global chose
	bad_counter=0; good_counter=0
	try:
		r=requests.get(geaway_link, cookies=cookie, headers=headers)
		if r.status_code!=200:
			debug_messages(r.status_code)
			set_notify("Site error", "Error  code: "+str(r.status_code))
	except:
		print("Site not avaliable...")
		chose=0
		time.sleep(300)
		return True
	soup_enter=BeautifulSoup(r.text, "html.parser")
	for bad_word in forbidden_words:
		bad_counter+=len(re.findall(bad_word, r.text, flags=re.IGNORECASE))
	if bad_counter>0:
		for good_word in good_words:
			good_counter+=len(re.findall(good_word, r.text, flags=re.IGNORECASE))
		if bad_counter>good_counter:
			debug_messages("It is a trap! Be carefull! Bad people want destroy my scripts.")
			do_beep("bad_words")
			with open("bad_giveaways.txt","a") as bad_giveaways:
				bad_giveaways.write(geaway_link+"\n")
			return False
		if bad_counter==good_counter:
			debug_messages("False alarm. All nice."+str(geaway_link))
			set_notify("False alarm", "All nice")		
	try:
		game=soup_enter.title.string
	except:
		debug_messages("No name")
		game="Unknown game"
	if game in bad_games_name:
		debug_messages("You do not like this game")
		set_notify("Game from blacklist. Ignore", game)
		return False
	link=soup_enter.find(class_="sidebar sidebar--wide").form
	if link!=None:
		link=link.find_all("input")
		params={"xsrf_token": link[0].get("value"), "do": "entry_insert", "code": link[2].get("value")}
		try:
			r=requests.post("https://www.steamgifts.com/ajax.php", data=params, cookies=cookie, headers=headers)
			extract_coins = json.loads(r.text)
		except:
			print("Site not avaliable...")
			chose=0
			time.sleep(300)	
			return True
#		print(r.text)
		if extract_coins["type"]=="success":
			coins=extract_coins["points"]
			print("Game: "+ re.sub("[^A-Za-z0-9 +-.,:!()]", "", game).rstrip(" ")+". Coins: "+coins)
			set_notify("Bot entered to giveaways with game: ", re.sub("&", '',  game)+". Coins left: "+extract_coins["points"])
			time.sleep(random.randint(1,120))
			return False
		elif extract_coins["msg"]=="Not Enough Points":
			coins=get_coins(get_requests(cookie, "coins_check"))
			if coins<10:
				chose=0
				i_want_to_sleep=True
				debug_messages("Not enough coins..." + str(geaway_link))
				return True
			else:
				return False
	else:
		link=soup_enter.find(class_="sidebar__error is-disabled")
		if link!=None and link.get_text()==" Not Enough Points":
			debug_messages("Not enough points to entered in "+str(geaway_link))
			time.sleep(random.randint(5,60))
			if int(get_coins(get_requests(cookie, "coins_check")))<10:
				chose=0
				i_want_to_sleep=True
				return True
		else:
			link=soup_enter.select("div.featured__column span")
			if link!=None:
				debug_messages("Giveaway was ended. Bot has late to enter giveaway: "+ str(geaway_link))
				debug_messages("Was ended: "+ str(link[0].text))
				time.sleep(random.randint(5,60))
				return False
			else:
				debug_messages("Critical error!")
				with open("errors.txt", "a") as error:
					error.write(link+"\n")
				do_beep("critical")
				debug_messages(link)
				return False
		return False

def get_entered_links(requests_result):
	"""Entered giveaway list. ignore it"""
	global nedd_next_page_for_entered_link
	entered_list=[]
	try:
		soup=BeautifulSoup(requests_result.text, "html.parser")
		links=soup.find_all(class_="table__row-inner-wrap")
	except:
		return entered_list
	for get_link in links:
		url=get_link.find(class_="table__column__heading").get("href")
		check_geaways_end=get_link.find(class_="table__remove-default is-clickable")
		if check_geaways_end!=None:
			entered_list.append(url)
		elif get_link.find(class_="table__column__deleted")!=None:
			continue
		else:
			nedd_next_page_for_entered_link=False
			return entered_list
	return entered_list

def get_coins(requests_result):
	"""how many coins"""
	try:
		soup=BeautifulSoup(requests_result.text, "html.parser")
		coins=soup.find(class_="nav__points").string
		return coins
	except:
		return 0

def get_next_page(requests):
	"""Next page exists?"""
	try:
		if requests.text.find("Next")!=-1:
			return True
		else:
			return False
	except:
		return  False
		
def set_notify(head, text):
	"""Set notify. Only on Linux"""
	if not need_send_notify:
		return 0
	try:
		if platform.system()!="Linux":
			return 0
		notify2.init('Steam_gifts_bot')
		n = notify2.Notification(head, text)
		n.set_timeout(15000)
		n.set_icon_from_pixbuf(pb)
		n.show()
	except:
		pass

def debug_messages(text):
	if debug_mode:	
		print(text)
	return 0

def work_with_win_file(need_write, count):
	"""Function for read drom file or write to file won.txt"""
	with open('won.txt', 'r+') as read_from_file:
		if not need_write:
			count=read_from_file.read()
			read_from_file.close()
			return count
		elif need_write:
			read_from_file.seek(0)
			read_from_file.write(str(count))
			read_from_file.close()

def check_won(count):
	"""Check new won giveaway"""
	try:
		r=requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
		soup=BeautifulSoup(r.text, "html.parser").find(class_="nav__right-container").find_all("a")[1].find(class_="nav__notification").string
	except:
		debug_messages("You did not win giveaways... But do not worry. Luck next time!")
		work_with_win_file(True, 0)
		return 0
	if int(count)<int(soup):
		do_beep("won")
		set_notify("Congratulations! You won!", "Take your prize on website")
		print("Congratulations! You won!", "Take your prize on website.")
		work_with_win_file(True, soup)
		return soup
	elif int(count)>int(soup):
		work_with_win_file(True, soup)
		return soup
	return count

def do_beep(reason):
	"""do beep with PC speacker. Work only on Linux and requrement motherboard speaker"""
	if not need_beep:
		return 0
	if (datetime.datetime.now().time().hour<9 or datetime.datetime.now().time().hour>22) and silent_mode_at_night:
		debug_messages("Not beep, because too late")
		return 0
	if  platform.system()=="Linux" or platform.system()=="FreeBSD":
		if reason=="coockie_exept":
			call(["beep", "-l 2000",  "-f 1900", "-r 3"])
		elif reason=="critical":
			call(["beep", "-l 1000", "-r 10", "-f 1900" ])
		elif reason=="won":
			os.system("./win.sh")
		elif reason=="bad_words":
			call(["beep", "-l 300", "-r 30", "-f 1900" ])

def steam_companion():
	global sc_points
	global sc_need
	try:
		r = requests.get("https://steamcompanion.com/", cookies=sc_cookie, headers=headers)
		soup = BeautifulSoup(r.text, "html.parser")
		soup = soup.find(class_="points").string
	except:
		set_notify("Steamcompanion:", "site not available...")
		print("Steamcompanion not available...")
		return 0	
	if sc_points==soup:
		sc_need=0
	else:
		sc_points=soup
		set_notify("Bot of Steam companion reports:", "Amount of coinsт: "+str(soup))

def get_games_from_banners():
	soup=BeautifulSoup(requests.get("https://www.steamgifts.com/", cookies=cookie, headers=headers).text, "html.parser")
	banners=soup.find(class_="pinned-giveaways__inner-wrap pinned-giveaways__inner-wrap--minimized").find_all(class_="giveaway__heading__name")
	for games in banners:
		if games not in giveaways_from_banner:
			giveaways_from_banner.append(games.get("href"))
			debug_messages("You will never win the game " + str(games.get("href")) + ", because you have refused to enter giveaways from banner..")

print("I am started...\nHave a nice day!")
func_list=[]
sc_need=0; sc_points=0
need_giveaways_from_banners=0
need_send_notify=0; threshold=0;
need_beep=0; debug_mode=0
silent_mode_at_night=0
check_new_version(version)
chose=0
random.seed(os.urandom)
headers = json.loads(get_user_agent())
cookie=get_from_file("cookie.txt")
sc_cookie=get_from_file("steam_companion_cookies.txt")

try:
	r=requests.get("https://www.steamgifts.com/giveaways/search?type=wishlist", cookies=cookie, headers=headers)
except:
	set_notify("Cookies expired", " Please update your cookies")
	do_beep("coockie_exept")
	sys.exit(1)
what_search=get_from_file("search.txt")
time.sleep(random.randint(2,10))
coins=get_coins(get_requests(cookie, "coins_check"))
nedd_next_page_for_entered_link=True
entered_url=get_requests(cookie, "enteredlist")
#func_list=("wishlist", "search", "someone")
won_count=work_with_win_file(False, 0)
set_notify("Steam gifts bot started", "Coins total: " + str(coins))
settings_list=get_from_file("settings.txt")
bad_games_name=get_from_file("black_list_games_name.txt").values()
bad_giveaways_link=get_from_file("bad_giveaways_link.txt").values()
get_func_list()
i_want_to_sleep=False
forbidden_words=(" ban", " fake", " bot", " not enter", " don't enter")
good_words=(" bank", " banan", " both", " band", " banner", " bang")
giveaways_from_banner=[]
if not need_giveaways_from_banners:
	get_games_from_banners()
print("Total coins:", get_coins(get_requests(cookie, "coins_check")))

while True:
	if not need_giveaways_from_banners:
			get_games_from_banners()
	i_want_to_sleep=False
	requests_result=get_requests(cookie, func_list[chose])
	chose+=1
	if i_want_to_sleep:
		won_count=check_won(won_count)
		sleep_time=random.randint(1800,3600)
		coins=get_coins(get_requests(cookie, "coins_check"))
		set_notify("Coins too low...", "Or rather: "+coins+". Deep sleep for "+str(sleep_time//60)+" min.")
		print("Coins too low: "+ str(coins)+". Deep sleep for "+str(sleep_time//60)+" min.")
		if sc_need:
			steam_companion()
		time.sleep(sleep_time)
		chose=0
	if chose==len(func_list):
		won_count=check_won(won_count)
		sleep_time=random.randint(1800,3600)
		coins=get_coins(get_requests(cookie, "coins_check"))
		set_notify("I entered to all giveaways...", "Coins left: "+ str(coins)+". I go to sleep for "+str(sleep_time//60)+" min.")
		print("Coins left: "+ str(coins)+". I go to sleep for "+str(sleep_time//60)+" min.")
		if sc_need:
			steam_companion()
		time.sleep(sleep_time)
		chose=0
