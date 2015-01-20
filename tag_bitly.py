#!/usr/bin/env python

"""
returns bitly urls for facebook and twitter based on url and tag
"""

"""import necessary packages"""
import sys, webbrowser, subprocess, urllib, urllib2, time, signal
from os.path import expanduser
from datetime import datetime
from cookielib import CookieJar

#establish home directory and make importable
try:
    u_home = expanduser("~")
    sys.path.append(u_home + "/Desktop/tag\ bitly")
    tag_path = u_home + "/Desktop/tag\ bitly/"
except Exception, e:
    print "uh oh! couldn't access file on Desktop"
    print e
    sys.exit()


"""Functions"""
"""checks and get url"""
def get_url_tag():
    """get url and tag"""
    #get url from clipboard and check it 
    try:
        url = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE).stdout.read()
        url = url.strip() #remove trailing spaces
    except Exception, e:
        print "ooops, couldn't grab the url you copied"
        print e
    
    #get tag from argument, if no tag say tag is missing
    try:
        tag = sys.argv[1]     
    except IndexError:
        tag = ""
        print "didn't include a tag, so we left it blank!"
    return url, tag

"""Getting and updating post number"""
def open_txt(): 
    #try opening post.txt file
    try:
        with open(tag_path + 'post.txt', 'r') as f:
            post_file = f.read()
        return post_file
    except Exception, e:
        print "couldn't open the post.txt file"
        print e
        sys.exit()

def compare_date(post_file):
    """returns true if post_file is marked with today's date"""
    tod_date = str(datetime.now().month) + str(datetime.now().day)
    try:
        if tod_date == post_file.split()[0]: return True
    except IndexError:
        print "no date found, reset post number!"    
        return False
    except Exception, e:
        print "oooops, trouble getting the post number"
        print e
        sys.exit()
    else:
        return False


def get_postnum():
    post_file = open_txt()
    if compare_date(post_file):
        post = str(int(post_file.split()[1]) + 1)
    else:   
        post = str(1)
    return post

def write_new_post(post):
    tod_date = str(datetime.now().month) + str(datetime.now().day)
    content = tod_date + " " + str(post)
    try:
        with open(tag_path + "post.txt", 'w') as f:
            f.write(content)
            f.close()
    except Exception, e:
        print "couldn't write post date and number"
        print e
        sys.exit()


"""full url"""        
def add_embed(url, tag, post):
    fb = url + "facebook_post" + post + "_" + tag
    tw = url + "twitter_post" + post + "_" + tag
    return fb, tw

"""check internet connection and url"""
def checkConnection():
    try:
        urllib2.urlopen("http://www.google.com").close()
        return True
    except: 
        print "poop, can't connect to the inter-web!"
        return False

def check_url(url):
    """checks url using internet if availble"""
    if connection:
        try:
            urllib2.urlopen(url).close()
        except:
            try:
                cj = CookieJar()
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                opener.open(url).close()
            except Exception, e: 
                print "uh oh, can't open your url! double check" 
                print "url: ", url
                print "error message ", e
                sys.exit()
    else:
        if "http" not in url: 
            print "check your url! doesn't contain http like it ought to"
            print "url: ", url


"""shorten"""
def shorten(url):
    #calls bitly url api to shorten
    #ADD ACCESS TOKEN
    bitly_url = "https://api-ssl.bitly.com/v3/shorten?access_token=" + urllib.quote_plus(url) + "&format=txt" 
    try:
        short_url = urllib2.urlopen(bitly_url, timeout=0.25).read()
        return short_url.strip()
    except: 
        raise ValueError("bitly didn't return shortened url")

def try_shortening(fb, tw):
    #does two calls on shorten for twitter and facebook urls 
    #sets short_fb and short_tw to False on failure
    
    try:
        short_fb = shorten(fb)
        time.sleep(0.1)
        short_tw = shorten(tw)
    except:
        try:
            time.sleep(0.1)
            short_fb = shorten(fb)
            time.sleep(0.1)
            short_tw = shorten(tw)
        except Exception, e:
            short_fb = False
            short_tw = False
            print "somethin' may be up with ol' bitly, see for your self!"
            return short_fb, short_tw
    return short_fb, short_tw

"""execute shortening links"""

def all_good(short_fb, short_tw):
    print "facebook ", short_fb
    print "twitter ", short_tw
    print short_fb
    print short_tw

def return_full(fb, tw):            
    print "full facebook ", fb
    print "full twitter", tw
    print fb
    print tw
    #open bitly in browser
    if connection:
        try:    
            webbrowser.open("https://bitly.com/", new=2, autoraise=True)
        except Exception, e:
            print "couldn't open bitly website"
    
    
def voila(fb, tw):
    #print post number and tag
    print "post ", post
    if tag: print "tag", tag
    #check connection
    if connection:
        short_fb, short_tw = try_shortening(fb, tw)
        if short_fb:
            all_good(short_fb, short_tw)
        else: return_full(fb, tw)
    else: return_full(fb, tw)
        

if __name__ == "__main__": 
    #store url and tag in variables
    url, tag = get_url_tag()
    
    #post number
    post = get_postnum()
    write_new_post(post)

    #full url
    fb, tw = add_embed(url, tag, post)
    
    #checks
    connection = checkConnection()    
    check_url(url)

    #return shortened if possible, else returns full urls 
    voila(fb, tw)

"""
applescript
    assign to shift + command + c 
using terms from application "Finder"
	display dialog "tag? " default answer "" with icon note
	set mtag to text returned of result
	
	set voila to do shell script "python ~/Desktop/tag\ bitly/tag_bitly.py " & mtag
	
	#try making links copyable
	try
		set slinks to text (paragraph -2) thru -1 of voila
		set svoila to text (paragraph -3) thru 1 of voila
	on error
		set svoila to text of voila
		set slinks to text of voila
	end try
	
	#show result
	display dialog svoila default answer slinks with title "voila voila Carrie"
end using terms from
"""

