#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib, zlib,json
import twitter,shutil
import webbrowser
import re
from requests_oauthlib import OAuth1Session
from thread import start_new_thread
from requests.packages import urllib3
import math

urllib3.disable_warnings()

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'
consumer_key = "X54OL8ozrRMQWmYrQJV2Ihirr"
consumer_secret = "0RHD0CRm7noPvwVYvPL5FAaqazBu49JUecUN7tWam7yaMqeLZi"
oauth_token=""
oauth_token_secret=""


__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('path') )
background = os.path.join(__addondir__,"bg.png")
inhalt=__addon__.getSetting("inhalt")
profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

if inhalt=="TV" or inhalt=="Hash":
  ratlimit=8
else :
  ratlimit=60

  
  
wid = xbmcgui.getCurrentWindowId()        
window=xbmcgui.Window(wid)
window.show()  
  
# Einlesen von Parametern, Notwendig für Reset der Twitter API
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

# Soll Twitter Api Resetter Werden
if len(sys.argv) > 1:
    params = parameters_string_to_dict(sys.argv[2])
    mode = urllib.unquote_plus(params.get('mode', ''))
    if mode=="clear":      
      xbmc.log("Twitter : CLEAR AUTH")            
      # ES wird mit dem Service ueber ein Verstecktes Feld Kommuiniziert
      __addon__.setSetting(id='clear', value='CLEARIT')
      # Meldung das der Settings gelöscht werden
      dialog2 = xbmcgui.Dialog()      
      ok = xbmcgui.Dialog().ok( "Neu Configuration", "Nach verlassen des Einstellungen wird Twitter neu Configuriert" )   
      exit()
  

def showTweet(tweet,image=""):
    global alles_anzeige
    global urlfilter
    global lesezeit
    global background
    global greyout
    xbmc.log("Twitter : showTweet start")    
    if xbmc.getCondVisibility('Pvr.IsPlayingTv') or alles_anzeige=="true" :   
        global window
        tw=unicode(tweet).encode('utf-8')    
        xbmc.log("showTweet")
        if urlfilter=="true":
             xbmc.log("Filter URLS")
             match=re.compile('(http[s]*://[^ ]+)', re.DOTALL).findall(tw)
             if match:
               for furl in match:
                 tw=tw.replace(furl,"")
                 xbmc.log("Filter Url : "+ furl)            
        xbmc.log("Tweet:" +tw)        
        wid = xbmcgui.getCurrentWindowId()        
        window=xbmcgui.Window(wid)
        res=window.getResolution()      
        if len(tw) > 100 :
           bis=100
           for i in range(90,110):        
             if tw[i]==' ':
               bis=i
        else:
            bis=len(tw)
        if greyout=="true":
           bg=xbmcgui.ControlImage(0,10,3000,100,"")
           bg.setImage(background)
           window.addControl(bg) 
           
        twitterlabel1=xbmcgui.ControlLabel (111, 31, 3000, 100, tw[:bis],textColor='0xFF000000')
        twitterlabel2=xbmcgui.ControlLabel (110, 30, 3000, 100, tw[:bis],textColor='0xFFFFFFFF')        
        window.addControl(twitterlabel1)
        window.addControl(twitterlabel2)
        
        if len(tw) > 100:
         twitterlabel3=xbmcgui.ControlLabel (111, 61, 3000, 100, tw[bis:],textColor='0xFF000000')        
         twitterlabel4=xbmcgui.ControlLabel (110, 60, 3000, 100, tw[bis:],textColor='0xFFFFFFFF') 
         window.addControl(twitterlabel3)
         window.addControl(twitterlabel4)         
        avatar=xbmcgui.ControlImage(0,10,100,100,"")
        avatar.setImage(image)
        window.addControl(avatar)        
        time.sleep(int(lesezeit))
        
        window.removeControl(twitterlabel1)
        window.removeControl(twitterlabel2)
        if len(tw) > 100:
           window.removeControl(twitterlabel3)
           window.removeControl(twitterlabel4)
        window.removeControl(avatar)
        if greyout=="true":
           window.removeControl(bg)
        
        
        
# Get Token        
def get_access_token(consumer_key, consumer_secret):
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret)
    xbmc.log("Twitter: Requesting temp token from Twitter")
    try:
        resp = oauth_client.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError, e:
        xbmc.log("Twitter: Invalid respond from Twitter requesting temp token: %s" % e)
        return
    url = oauth_client.authorization_url(AUTHORIZATION_URL)

    # Will der User das gleich ein Browser aufgerufen wird    
    __addon__.setSetting(id='clear', value='')
    dialog = xbmcgui.Dialog()
    if dialog.yesno("message", "Twitter Auth im Browser?"):
        webbrowser.open(url)
    else:                 
        xbmc.log("Twitter: URL ---> "+url)
        # Zeige Url als Text an
        dialog = xbmcgui.Dialog()
        dialog.ok("Bitte URL im Browser Aufrufen", url[:40] +"\n"+ url[40:80] +"\n" +url[80:120] )
    
    # Eingabe des Pins
    keyboard = xbmc.Keyboard('')
    keyboard.setHeading('Twitter: Pin Eingeben')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      PIN=keyboard.getText()
    else:
      PIN='0000'
    if  PIN=='0000':
       return 1
    xbmc.log("PIn: "+ PIN)
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret,
                                 resource_owner_key=resp.get('oauth_token'),
                                 resource_owner_secret=resp.get('oauth_token_secret'),
                                 verifier=PIN
    )
    try:
        resp = oauth_client.fetch_access_token(ACCESS_TOKEN_URL)
    except ValueError, e:  
         return 1   
    xbmc.log("Twitter: Setze oauth"   )
    xbmc.log("Twitter Token : " + resp.get('oauth_token'))
    xbmc.log("Twitter Secret : "+ resp.get('oauth_token_secret'))
    
    global oauth_token
    global oauth_token_secret
    oauth_token= resp.get('oauth_token')
    oauth_token_secret=resp.get('oauth_token_secret') 
    
    #Speicher Token fürs naechste mal
    f = open(temp+"init.ok", 'w')        
    zeile="oauth_token: "+ oauth_token +"#"    
    f.write(zeile)    
    zeile="oauth_token_secret: "+ oauth_token_secret +"#"    
    f.write(zeile)
    f.close()    


    


if __name__ == '__main__':
    xbmc.log("Twitter:  Starte Plugin")
        
    x=0   
    
    #Directory für Token Anlegen
    if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
    # Starte Service
    monitor = xbmc.Monitor()
    
    sinceid=None
    auth=0
    # Solange der Service läuft
    while not monitor.abortRequested():
      # Wenn kein Token oder Authentifizerung löschen wurde Neu Authentifizieren
      if not xbmcvfs.exists(temp+"/init.ok") or __addon__.getSetting("clear")=="CLEARIT":        
        x=get_access_token(consumer_key, consumer_secret)       
        auth=0
      else:         
        if auth==0:
          # Alten Token Laden
          f=xbmcvfs.File(temp+"/init.ok","r")   
          daten=f.read()
          match=re.compile('oauth_token: ([^#]+)', re.DOTALL).findall(daten)
          oauth_token=match[0]
          match=re.compile('oauth_token_secret: ([^#]+)', re.DOTALL).findall(daten)
          oauth_token_secret=match[0]              
      if auth==0 :
         xbmc.log("Twitter: Starte Auth")                  
         api = twitter.Api(consumer_key=consumer_key,consumer_secret=consumer_secret,access_token_key=oauth_token,access_token_secret=oauth_token_secret)       
         auth=1
      # Warten damit wir nicht zuviel absetzen
      xbmc.log("Sleep")
      if monitor.waitForAbort(ratlimit):
        break      
      # Nur wenn ein Fernsehnder an ist      
      if xbmc.getCondVisibility('Pvr.IsPlayingTv'):
        xbmc.log("Hole Ferseh tweets")
        now = xbmc.getInfoLabel('Player.Title')
        channel = xbmc.getInfoLabel('VideoPlayer.ChannelName')
        if channel=="" :
             break
        if "Erste" in channel:
           channel="ard"
        if "ProSieben" in channel:
           channel="pro7"
        
        channel=channel.replace(".","")  

        match=re.compile('([^-]+)', re.DOTALL).findall(now)        
        if match:
          now=match[0]
        match=re.compile('([^:]+)', re.DOTALL).findall(now)
        if match:        
          now=match[0]
        now=now.replace(" ","")        
        now=now.replace("ä","ae") 
        now=now.replace("ö","oe") 
        now=now.replace("ü","ue") 
        now=now.replace("?","") 
        now=now.replace(",","") 
        now=now.replace("’","")         
        now=now.lower()

        if "werwirdmillionaer" in now:
           now="wwm"
        if "deutschlandsuchtdensuperstar" in now:
            now="dsds"
        if "alleswaszaehlt" in now:
            now="awz"
        if "gutezeitenschlechtezeiten" in now:
            now="gzsz"
        if "ichbineinstar" in now:
            now="ibes"
        if "germanysnexttopmodel" in now:
            now="gntm"
        if "diesimpsons" in now:
            now="simpsons"
       

        channel=channel.replace(" HD","")
        channel=channel.replace(" ","")        
        if now :
          search="#"+ channel +" OR "+ "#"+ now
        else:
           search="#"+ channel               
        xbmc.log("SEARCH :"+ search + " ID: " +str(sinceid))
        xbmc.log("loading new data")         
        xbmc.log("inhalt :"+ inhalt)
      xbmc.log("Hole Umgebung")
      country=__addon__.getSetting("country").lower()        
      limit=__addon__.getSetting("limit")         
      alles_anzeige=__addon__.getSetting("alles_anzeige")   
      hashtag=__addon__.getSetting("hashtag") 
      bild=__addon__.getSetting("bild") 
      inhalt=__addon__.getSetting("inhalt")
      urlfilter=__addon__.getSetting("urls")
      lesezeit=__addon__.getSetting("lesezeit")
      greyout=__addon__.getSetting("greyout")
      if inhalt=="Hash":
          if hashtag :
             if inhalt=="Hash":
                 xbmc.log("#Hastag :" + hashtag)
                 search=hashtag
          else:
             xbmc.log("Setze Kodi")
             search="kodi"
      if xbmc.getCondVisibility('Pvr.IsPlayingTv') or alles_anzeige=="true" :
        xbmc.log("Suche Tweets")
        try:          
          if   country=="" :
              country=None   
          if inhalt=="TV" or inhalt=="Hash":
               xbmc.log("SEARCH:")
               xbmc.log("SEARCH:   "+search)
               tweets=api.GetSearch(search,since_id=sinceid,lang=country,result_type="recent")
          else:
              tweets = api.GetHomeTimeline(since_id=sinceid)             
          for tweet in tweets:
             #print name.text              
              xbmc.log("--")
              text= tweet.user.name +" : "+ tweet.text.replace("\n"," ")
              if  tweet.id > sinceid :
                 sinceid=tweet.id              
              xbmc.log("######" + str(tweet.id))
              
              block=0
              blockwort=""
              blacklist=__addon__.getSetting("blacklist")
              xbmc.log("Blacklist"+ blacklist)
              blacklist=blacklist.split(",")
              if blacklist:
                for blocked in blacklist:
                  xbmc.log("Block Wort " + blocked +" Suchen")
                  if blocked.lower() in text.encode('utf-8').lower() and not blocked == "":
                     block=1
                     blockwort=blockwort +","+ blocked
              
              if block==0:
                 if bild=="true":
                   userimage=tweet.user.profile_image_url    
                 else :
                    userimage=""                   
                 showTweet(text,userimage) 
              else :
                  xbmc.log("Blocked : "+ blockwort + "Text :"+ text.encode('utf-8'))
              time.sleep(int(lesezeit))
        except :
                xbmc.log("Errror")        
      else:
         sinceid=None      