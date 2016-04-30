#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
from StringIO import StringIO
import xml.etree.ElementTree as ET
import binascii
import time
from datetime import datetime
import hashlib
import random
import md5

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
debuging=""
# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'episodes')
baseurl="http://www.myvideo.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")

#if xbmcvfs.exists(temp):
#  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level)    

def rename_name(name,url):
  m = md5.new()
  m.update(url)
  urlnr=m.hexdigest()
  fname=temp+"/"+urlnr
  if xbmcvfs.exists(fname):
        f=open(fname,'r') 
        for line in f:           
           if urlnr in line:           
              felder = line.split(",")
              mode=felder[0]
              hash=felder[1]
              new_name=felder[2]
              new_name=new_name[:-1]
              if mode=="=":
                name=new_name           
  return name   
def delete_name(url,orgurlnow):
  m = md5.new()
  m.update(url)
  urlnr=m.hexdigest()
  fname=temp+"/"+urlnr
  if xbmcvfs.exists(fname):
        f=open(fname,'r') 
        for line in f:           
           if urlnr in line:           
              felder = line.split(",")
              mode=felder[0]
              hash=felder[1]
              orgurl=felder[2].replace("\n","")  
              debug (":orgurl  :"+orgurl+"#")
              debug (":orgurlnow :"+orgurlnow+"#")              
              if mode=="-" and orgurl==orgurlnow:
                debug("Ist zu löschen")
                return 0       
  return 1   
  
def addDir(name, url, mode, iconimage, desc="",offset="",tab="",genre="",id="",duration="",filename="",orgurl=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&filename="+filename
  if offset!="":
     u=u+"&offset="+str(offset)
  if tab!="":
     u=u+"&tab="+str(tab)
  ok = True
  name=rename_name(name,url)
  if delete_name(url,orgurl)==0:
     return 
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  commands = []
  filename=temp+"/favorit.txt"
  addfav = "plugin://plugin.video.myvideo2/?mode=addfav&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+urllib.quote_plus(name) +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addDir&filename="+filename
  delfav = "plugin://plugin.video.myvideo2/?mode=delfav&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+urllib.quote_plus(name) +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addDir&filename="+filename
  delete = "plugin://plugin.video.myvideo2/?mode=delete&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+urllib.quote_plus(name) +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addDir&filename="+filename+"&orgurl="+orgurl
  undelete = "plugin://plugin.video.myvideo2/?mode=undelete&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+urllib.quote_plus(name) +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addDir&filename="+filename+"&orgurl="+orgurl
  rename = "plugin://plugin.video.myvideo2/?mode=rename&url="+urllib.quote_plus(url)+"&name="+name+"&orgurl="+orgurl
  commands.append(( "Favoriten Hinzufügen", 'XBMC.RunPlugin('+ addfav +')'))   
  commands.append(( "von Favoriten löschen" , 'XBMC.RunPlugin('+ delfav +')')) 
  commands.append(( "Rename" , 'XBMC.RunPlugin('+ rename +')'))
  if orgurl=="deltemenu":
     commands.append(( "Undelete" , 'XBMC.RunPlugin('+ undelete +')'))
  
  else:
     commands.append(( "Delete" , 'XBMC.RunPlugin('+ delete +')'))
  liz.addContextMenuItems( commands )  
           
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
 
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',id="",offset="",tab="",filename="",orgurl=""):  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&filename="+filename
  if id != "" :
    u=u+"&id="+str(id)
    
  ok = True
  name=rename_name(name,url)
  if delete_name(url,orgurl)==0:
     return 
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  commands = []
  file=temp+"/favorit.txt"
  addfav = "plugin://plugin.video.myvideo2/?mode=addfav&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+name +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addLink&filename="+filename
  delfav = "plugin://plugin.video.myvideo2/?mode=delfav&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+name +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addLink&filename="+filename
  delete = "plugin://plugin.video.myvideo2/?mode=delete&url="+urllib.quote_plus(url)+"&modus="+ mode  +"&iconimage="+iconimage +"&desc=" +urllib.quote_plus(desc)+ "&name="+name +"&tab=" +str(tab) +"&offset="+ str(offset)+"&duration="+ str(duration)+"&genre="+genre +"&id="+str(id)+"&funktion=addLink&filename="+filename+"&orgurl="+orgurl
  rename = "plugin://plugin.video.myvideo2/?mode=rename&url="+urllib.quote_plus(url)+"&name="+name+"&orgurl="+orgurl
  commands.append(( "Favoriten Hinzufügen", 'XBMC.RunPlugin('+ addfav +')'))   
  commands.append(( "von Favoriten löschen" , 'XBMC.RunPlugin('+ delfav +')')) 
  commands.append(( "Rename" , 'XBMC.RunPlugin('+ rename +')'))
  commands.append(( "Delete" , 'XBMC.RunPlugin('+ delete +')'))  
  if "musik" in url:
    kuenstler_reg=match=re.compile('http://www.myvideo.de/musik/(.+?)/', re.DOTALL).findall(url)
    kuenstler=kuenstler_reg[0]
    musikurl="http://www.myvideo.de/musik/"+ kuenstler
    mehr = "plugin://plugin.video.myvideo2/?mode=mischseite&url="+urllib.quote_plus(musikurl)
    commands.append(( "Mehr vom Künstler" , 'ActivateWindow(Videos,'+ mehr +')'))     
  liz.addContextMenuItems( commands )
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict
  
 
def geturl(url):
   cj = cookielib.CookieJar()
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt
   
def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()    
    return title
    
def abisz(url):
  letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
  for letter in letters:
    if letter=="a":
     lettern=""
    else:
      lettern=letter
    urln=url+lettern+"/"
    addDir(letter.lower(), urln, 'Buchstabe', "",orgurl=url)
  addDir("0-9", "0-9", 'Buchstabe', "")
  xbmcplugin.endOfDirectory(addon_handle)
  
def Buchstabe(url):
  debug(url)
  content=geturl(url)
  match=re.compile('window.MV.contentListTooltipData = {(.+?)};', re.DOTALL).findall(content)
  jsonf=match[0]
  struktur = json.loads("{"+jsonf+"}") 
  videos=struktur["items"]
  for video in videos:
    url= video["linkTarget"]
    try :
      desc= unicode(video["description"]).encode("utf-8")
    except:
      desc=""
    title=unicode(video["title"]).encode("utf-8")
    thump= video["thumbnail"]
    thump=thump.replace("ez","mv")
    if "musik" in url:
       addDir(title, "http://www.myvideo.de"+url, 'mischseite', thump,desc,orgurl=url)
    else:
       addDir(title, "http://www.myvideo.de"+url, 'Staffel', thump,desc,orgurl=url)
  try:            
      match=re.compile('<a href="([^"]+)" class="button as-next">', re.DOTALL).findall(content)
      vor=match[0]
      addDir("Haupt Menu", "Haupt Menu", '', "")
      addDir("Next", "http://www.myvideo.de"+vor, 'Buchstabe',"",orgurl=url)      
  except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

  
def Staffel(url):
    debug("Staffel : "+ url)
    content=geturl(url)
    match=re.compile('data-list-name="season_tab([^"]+)" data-url="(.+?)"', re.DOTALL).findall(content)  
    for staffel,url in match:      
       try:
          xy=int(staffel)
          staffel= "Staffel "+staffel
       except:
          pass
       addDir(staffel, "http://www.myvideo.de"+url, 'Serie',"","",orgurl=url)
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def Serie(url):
  content=geturl(url)
  debug("URL :" + url)
  folgen = content.split('<div class="videolist--item">')
  for i in range(1, len(folgen), 1):
    folge=folgen[i]                   
    match=re.compile('href="(.+?)"', re.DOTALL).findall(folge)  
    url=match[0]
    match=re.compile('title="(.+?)"', re.DOTALL).findall(folge)
    name=cleanTitle(match[0])
    match=re.compile('src="(.+?)"', re.DOTALL).findall(folge)
    thumnail=match[0]
    match=re.compile('"thumbnail--subtitle">(.+?)</div>', re.DOTALL).findall(folge)   
    sub=match[0]
    addLink(name + " ( "+ sub +" )", "http://www.myvideo.de"+url, 'playvideo',thumnail,"",orgurl=url)
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def playvideo(url):  
 
 debug("-----------")
 debug(" URL : "+url)
 match=re.compile('.+?-m-(.+)', re.DOTALL).findall(url)
 video_id=match[0]
 salt = "dfCc3ca+3baf2e8%beGa508!cbcdbG0f"
 client_location = urllib.quote_plus(url)
 access_token = "MVKolibri"
 client_name = "kolibri-2.6.16"
 #callback = "_player1_mvas0"
 
 url = "https://mls.myvideo.de/mvas/videos?access_token="+ access_token+"&client_location="+client_location+"&client_name="+client_name+"&ids="+video_id+"&callback="
 content=geturl(url)
 debug(content)
 struktur = json.loads(content)
 title = struktur[0]["title"];
 struct=struktur[0]["sources"]
 debug(struct)
 ids =""
 for element in struct:
    ids=ids + str(element["id"])
    ids=ids +","
 ids=ids[:-1]
	
 debug("ids : "+ ids)
 m1 = hashlib.sha1()
 m1.update(video_id + salt + access_token + client_location + salt +client_name)
 name=m1.hexdigest()
 client_id =  salt[0:2] + name
 newurl="https://mls.myvideo.de/mvas/videos/"+ video_id +"/server?access_token="+ access_token +"&client_location="+ client_location+"&client_name="+ client_name +"&client_id="+ client_id +"&callback="
 content=geturl(newurl)
 struktur = json.loads(content)
 server_id=struktur["server_id"]
 m2 = hashlib.sha1()
 m2.update(salt +  video_id + access_token +server_id + client_location+ ids + salt + client_name)
 name=m2.hexdigest()
 client_id = salt[0:2] +name
 url="https://mls.myvideo.de/mvas/videos/"+ video_id +"/sources?access_token="+ access_token +"&client_location="+ client_location +"&client_name="+ client_name +"&client_id="+ client_id +"&server_id="+ server_id +"&ids="+ ids +"&callback="
 content=geturl(url)
 struktur = json.loads(content)
 struct=struktur["sources"]
 urlm3u8=""
 for name in struct:
     if name["mime_type"]=="application/x-mpegURL" :
        urlm3u8=name["url"]
 if urlm3u8=="":
   for name in struct:
      debug(name)
      debug("-----")
      if name["mime_type"]=="video/x-flv" :
         stream=name["url"]
         reg_str = re.compile('rtmpe?://(.*?)/(.*?)/(.*)', re.DOTALL).findall(stream)         
         server=reg_str[0][0]
         pfad=reg_str[0][1]
         datei=reg_str[0][2]
         swf = "http://component.p7s1.com/kolibri/2.12.9/myvideo/premium/kolibri.swf";
         urlm3u8="rtmp://"+ server +"/"+pfad +"/ swfVfy=1 swfUrl=" + swf +" playpath="+ datei
         debug("-+-+-+")
         debug(urlm3u8)
         
   
 listitem = xbmcgui.ListItem(title, path=urlm3u8, thumbnailImage="")
 xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
 debug(" ENDE : "+ urlm3u8)

def allfilms(url):
 content=geturl(url)
 folgen = content.split('<div class="grid--item as-')
 for i in range(1, len(folgen), 1):
     try:
      debug("-----")
      folge=folgen[i]
      match=re.compile('<img class="thumbnail--pic" src=".+?" data-src="(.+?)"', re.DOTALL).findall(folge) 
      thump=match[0]
      match=re.compile('<a href="(.+?)" class="grid--item-title">(.+?)</a> ', re.DOTALL).findall(folge) 
      name=cleanTitle(match[0][1])
      url=match[0][0]
      try:
        match=re.compile('<use xlink:href="#icon-duration">.+?([0-9]+?)h ([0-9]+?)m</div>', re.DOTALL).findall(folge) 
        std=match[0][0]
        min=match[0][1]
        laenge=int(std)*60*60 + int(min)*60     
      except:
        laenge=""
      addLink(name , "http://www.myvideo.de"+url, 'playvideo',thump,duration=laenge,orgurl=url)
     except:
       pass
 try:            
      match=re.compile('<a href="([^"]+)" class="button as-next">', re.DOTALL).findall(content)
      vor=match[0]
      addDir("Haupt Menu", "Haupt Menu", '', "",orgurl=url)
      addDir("Next", "http://www.myvideo.de"+vor, 'allfilms',"",orgurl=url)
      
 except:
      pass
 xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)     

def  top100():
  addDir("Top Music Genres", "Top Music Genres", 'topgenres', "",orgurl="top100")
  addDir("Top 100 Music Clips", "http://www.myvideo.de/top_100/top_100_musik_clips", 'top_zeit', "",orgurl="top100")  
  addDir("Top 25 Single Charts", "http://www.myvideo.de/top_100/top_100_single_charts", 'topliste', "",orgurl="top100")  
  addDir("Top 100 Entertainment", "http://www.myvideo.de/top_100/top_100_entertainment", 'top_zeit', "",orgurl="top100")
  addDir("Top 100 Serien", "http://www.myvideo.de/top_100/top_100_serien", 'top_zeit', "",orgurl="top100")
  addDir("Top 100 Filme", "http://www.myvideo.de/filme/top_100_filme", 'allfilms', "",orgurl="top100")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def topgenres():
  addDir("Top 100 Pop", "http://www.myvideo.de/top_100/top_100_pop", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Rock", "http://www.myvideo.de/top_100/top_100_rock", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Hip Hop", "http://www.myvideo.de/top_100/top_100_hiphop", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Electro", "http://www.myvideo.de/top_100/top_100_elektro", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Schlager", "http://www.myvideo.de/top_100/top_100_schlager", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Metal", "http://www.myvideo.de/top_100/top_100_metal", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 RnB", "http://www.myvideo.de/top_100/top_100_rnb", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Indie", "http://www.myvideo.de/top_100/top_100_indie", 'topliste', "",orgurl="topgenres")
  addDir("Top 100 Jazz", "http://www.myvideo.de/top_100/top_100_jazz", 'topliste', "",orgurl="topgenres")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def filme_menu():
   addDir("Alle Filme", "http://www.myvideo.de/filme/alle_filme", 'allfilms', "",orgurl="filme_menu")
   addDir("Alle Filme - Datum", "http://www.myvideo.de/filme/alle_filme/datum", 'allfilms', "",orgurl="filme_menu")
   addDir("Top Filme", "http://www.myvideo.de/filme/top_100_filme", 'allfilms', "",orgurl="filme_menu")
   addDir("Kino Trailer", "http://www.myvideo.de/filme/kino-dvd-trailer", 'mischseite', "",orgurl="filme_menu")
   addDir("Film Genres", "Film Genres", 'filmgenres', "",orgurl="filme_menu")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def filmgenres():
   addDir("Action", "http://www.myvideo.de/filme/action", 'allfilms', "",orgurl="filmgenres")
   addDir("Horror", "http://www.myvideo.de/filme/horror", 'allfilms', "",orgurl="filmgenres")
   addDir("Sci-Fi", "http://www.myvideo.de/filme/sci-fi", 'allfilms', "",orgurl="filmgenres")
   addDir("Thriller", "http://www.myvideo.de/filme/thriller", 'allfilms', "",orgurl="filmgenres")
   addDir("Drama", "http://www.myvideo.de/filme/drama", 'allfilms', "",orgurl="filmgenres")
   addDir("Comedy", "http://www.myvideo.de/filme/comedy", 'allfilms', "",orgurl="filmgenres")
   addDir("Western", "http://www.myvideo.de/filme/western", 'allfilms', "",orgurl="filmgenres")
   addDir("Dokumentationen", "http://www.myvideo.de/filme/dokumentation", 'allfilms', "",orgurl="filmgenres")
   addDir("Erotik", "http://www.myvideo.de/filme/erotik", 'allfilms', "",orgurl="filmgenres")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def top_zeit(url):
  addDir("Heute", url, 'topliste', "",orgurl="top_zeit")  
  addDir("Woche", url+"/woche", 'topliste', "",orgurl="top_zeit")
  addDir("Monat",  url+"/monat", 'topliste', "",orgurl="top_zeit")
  addDir("Ewig",  url+"/ewig", 'topliste', "",orgurl="top_zeit")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def topliste(url): 
   debug(" topliste url : "+url)
   content=geturl(url)   
   match=re.compile('data-list-name="chartlist".+?data-url="(.+?)"', re.DOTALL).findall(content) 
   url="http://www.myvideo.de"+match[0]
   misch_cat(url,0)
   
def mischseite(url):
   debug("URL: mischseite :"+url)
   content=geturl(url)
   liste=[]
   match2=re.compile('</use> </svg>([^<]+?)</h3> <div class="videolist.+?data-url="(.+?)"', re.DOTALL).findall(content)    
   for name, urll in match2:       
      debug("mschseiten misch_cat_auto: " + name +" URL: "+ url)
      addDir(cleanTitle(name), "http://www.myvideo.de"+ urll, 'misch_cat_auto', "",offset=0,orgurl=url)
   match=re.compile('sushibar.+?-url="(.+?)"', re.DOTALL).findall(content)        
   for urll in match:
      if "_partial" in urll:
         debug("--- URLL :"+urll)
         content2=geturl( "http://www.myvideo.de"+urll)
         match=re.compile('<h2 class="sushi--title">(.+?)</h2>', re.DOTALL).findall(content2)           
         name=cleanTitle(match[0])
         if "sushi--title-link" in name:
           match=re.compile('>(.+?)</a>', re.DOTALL).findall(name)           
           name=cleanTitle(match[0])
         if "</svg>" in name:
            match=re.compile('\<\/svg\>(.+)', re.DOTALL).findall(name)       
            name=match[0]            
         if '<h2 class="sushi--title">' in name:
           match=re.compile('<h2 class="sushi--title">(.+?)</h2>', re.DOTALL).findall(name)           
           name=cleanTitle(match[0])            
         if "icon-label-live" in name:
             continue
         if not name in liste:
           liste.append(name) 
           if  not "http://www.myvideo.de" in urll:
              urll="http://www.myvideo.de"+urll
           name=cleanTitle(name)
           debug("mschseiten misch_cat: "+ name +" URL: "+ urll)
           addDir(name, urll, 'misch_cat', "",offset=0,orgurl=url)
   namen_comedy=re.compile('<span class="tabs--tab.+?" data-linkout-label="" data-linkout-url="" >(.+?)</span>', re.DOTALL).findall(content)   
   url_comedy=re.compile('data-list-name=".+Videos" data-url="(.+?)"', re.DOTALL).findall(content)   
   debug(url_comedy)
   for i in range(0, len(url_comedy), 1): 
       name=cleanTitle(namen_comedy[i])
       urll="http://www.myvideo.de"+url_comedy[i]
       addDir(name, urll, 'misch_cat_auto', "",offset=0,orgurl=url)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
   debug("Mischseite Ende")

def misch_tab(url,tab): 
   orgurl=url
   debug(" misch_tab url "+ url)
   debug(" misch_tab tab "+ str(tab))
   content=geturl(url)   
   if '<div class="tabs--content' in content:
       Tabs = content.split('<div class="tabs--content">')
   else:
       Tabs = content.split('<div class="videolist')   
   liste=Tabs[int(tab)]
   if '<a class="thumbnail is-video sushi--item' in liste:
      videos = liste.split('<a class="thumbnail is-video sushi--item')
   else :
      videos = liste.split('<div class="videolist--item">')   
   for i in range(1, len(videos), 1): 
         url_reg=re.compile('href="(.+?)"', re.DOTALL).findall(videos[i])            
         url=url_reg[0]
         thump_reg=re.compile('src="(.+?)"', re.DOTALL).findall(videos[i])   
         thump=thump_reg[0]
         namen=re.compile('<div class="thumbnail--maintitle">(.+?)</div>', re.DOTALL).findall(videos[i])   
         name=cleanTitle(namen[0])
         try:
           subt_reg=re.compile('<div class="thumbnail--subtitle">(.+?)</div> ', re.DOTALL).findall(videos[i])   
           sub=cleanTitle(subt_reg[0])
           name=name +" ( "+ sub +" )"
         except:
           pass 
         if  not "http://www.myvideo.de" in url:
             url="http://www.myvideo.de"+url
         if "-m-" in url:
           addLink(name , url, 'playvideo',thump,orgurl=orgurl)
         else:
           addDir(name , url, 'mischseite',thump,orgurl=orgurl)
         

   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   #<div class="sushibar
   #data-url="/_partial/sushibar/11932"
   #<h2 class="sushi--title"> DVD/BluRay </h2>
def misch_cat_auto(url,offset):
   urln=url+"?ajaxoffset="+ offset
   debug("URL misch_cat_auto: "+ urln)
   content=geturl(urln)
   folgen = content.split('<a class')
   i=0
   count=0
   for i in range(1, len(folgen), 1):
        folge=folgen[i]
        match=re.compile('href="(.+?)" title="(.+?)"', re.DOTALL).findall(folge)
        urlname=match[0][0]
        name=cleanTitle(match[0][1])
        try:
          match=re.compile('src="(.+?)"', re.DOTALL).findall(folge)
          thump=match[0]
        except:
          thump=""        
        try:
           match=re.compile('class="thumbnail--subtitle">(.+?)</div>', re.DOTALL).findall(folge)
           name= name + " ( "+ cleanTitle(match[0]) + " )"
        except:
           pass
        if  not "http://www.myvideo.de" in urlname:
            urlname="http://www.myvideo.de"+urlname
        count=count+1
        debug("urlname: "+urlname)
        if "/serien/" in urlname:
             type="Staffel"
             
        else:        
             type="mischseite"
        if "-m-" in urlname:
           addLink(name , urlname, 'playvideo',thump,orgurl=url)
        else:
           addDir(name , urlname, type,thump,orgurl=url)
   addDir("Haupt Menu", "Haupt Menu", '', "")
   addDir("Next" , url, 'misch_cat_auto',"",offset=str(int(offset)+count))   
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
   
def misch_cat(url,offset):
   if "http://www.myvideo.de/search" not in url:
     urln=url+"?ajaxoffset="+ str(offset) + "&_format=ajax"
   else:
     urln=url+"&start="+str(offset)+ "&_format=ajax"
   debug("misch_cat URL : "+ urln)   
   content=geturl(urln)
   try:
       debug("Except falsche suche")
       match=re.compile('Ergebnisse für <a href="/search.+?">(.+?)</a>', re.DOTALL).findall(content)
       neusuch=match[0]
       debug("NEU :"+neusuch)
       match=re.compile('q=([^&]+)', re.DOTALL).findall(url)
       oldsuch=match[0]     
       debug("Oldsuch :"+oldsuch)              
       if oldsuch!=neusuch:
          addDir("Kein Ergebnis", "Suche", 'searchmenu', "",offset=0,orgurl=url) 
          xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
          return
   except:
       pass   
   try:
     match=re.compile('data-page-size="(.+?)"', re.DOTALL).findall(content)   
     anz=int(match[0])
   except:
     anz=0
   if 'list-item">' in content:
     folgen = content.split('list-item">')
   else :
     folgen = content.split('<a class')
   i=0
   count=0
   for i in range(1, len(folgen), 1):
        debug("---------")
        debug(folgen[i])        
        debug("---------")
        debug("Offset : "+ str(offset))
        folge=folgen[i]
        match=re.compile('href="(.+?)"', re.DOTALL).findall(folge)
        urlname=match[0]
        try:
          match=re.compile('alt="(.+?)"', re.DOTALL).findall(folge)        
          name=cleanTitle(match[0])
        except:
           continue
        try:
          match=re.compile('data-src="(.+?)"', re.DOTALL).findall(folge)
          thump=match[0]
        except:
          match=re.compile('src="(.+?)"', re.DOTALL).findall(folge)
          thump=match[0]
        try:
          match=re.compile('<div class="thumbnail--subtitle">(.+?)</div>', re.DOTALL).findall(folge)
          sub=cleanTitle(match[0])
          name= sub +" -- "+ name
        except:
          pass  
        try:
           nr_reg=re.compile('-item-position"> (.+?) </div>', re.DOTALL).findall(folge)   
           nr=cleanTitle(nr_reg[0])
           debug("NR :"+str(nr))
           debug("offset: "+ str(offset))
           name=str(int(offset)+int(nr)) +". "+ name
        except:
           pass                     
        if  not "http://www.myvideo.de" in urlname:
            urlname="http://www.myvideo.de"+urlname           
        count=count+1
        debug("urlname: "+urlname)
        if "/serien/" in urlname:
             type="Staffel"
             
        else:        
             type="mischseite"
        if "-m-" in urlname:
           addLink(name , urlname, 'playvideo',thump,orgurl=url)
        else:
           addDir(name , urlname, type,thump,orgurl=url) 
   if i>=anz:
       addDir("Haupt Menu", "Haupt Menu", '', "",orgurl=url)        
       addDir("Next" , url, 'misch_cat',"",offset=str(int(offset)+count),orgurl=url)                
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def tvmenu():
    addDir("Alle Serien", "http://www.myvideo.de/serien/alle_serien_a-z/", 'abisz', "",orgurl="tvmenu")
    addDir("Anime", "http://www.myvideo.de/serien/anime_tv", 'mischseite', "",orgurl="tvmenu")
    addDir("Top 100 Serien", "http://www.myvideo.de/top_100/top_100_serien", 'top_zeit', "",orgurl="tvmenu")
    addDir("Serien Highlight", "http://www.myvideo.de/serien/weitere_serien", 'mischseite', "",orgurl="tvmenu")    
    addDir("Serien in OV", "http://www.myvideo.de/serien/serien-in-ov", 'mischseite', "",orgurl="tvmenu") 
    addDir("Kids", "http://www.myvideo.de/serien/kids", 'mischseite', "",orgurl="tvmenu") 
    addDir("BBC", "http://www.myvideo.de/serien/bbc", 'mischseite', "",orgurl="tvmenu")    
    addDir("Pro 7", "http://www.myvideo.de/serien/prosieben", 'mischseite', "",orgurl="tvmenu")    
    addDir("Sat 1", "http://www.myvideo.de/serien/sat_1", 'mischseite', "",orgurl="tvmenu")    
    addDir("Sixx", "http://www.myvideo.de/serien/sixx", 'mischseite', "",orgurl="tvmenu")    
    addDir("Pro 7 Maxx", "http://www.myvideo.de/serien/prosieben_maxx", 'mischseite', "",orgurl="tvmenu")    
    addDir("Pro 7 Maxx Anime", "http://www.myvideo.de/serien/prosieben_maxx_anime", 'mischseite', "",orgurl="tvmenu")    
    addDir("Kabel Eins", "http://www.myvideo.de/serien/kabel_eins", 'mischseite', "",orgurl="tvmenu")    
    addDir("Sat 1 Gold", "http://www.myvideo.de/serien/sat_1_gold", 'mischseite', "",orgurl="tvmenu")    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
def themenmenu():
    addDir("Aktuelles", "http://www.myvideo.de/themen", 'mischseite', "",orgurl="themenmenu")
    addDir("WWE", "http://www.myvideo.de/themen/wwe", 'mischseite', "",orgurl="themenmenu")
    addDir("Webstars", "http://www.myvideo.de/webstars", 'mischseite', "",orgurl="themenmenu")
    addDir("Fußball", "http://www.myvideo.de/themen/sport/fussball", 'mischseite', "",orgurl="themenmenu")
    addDir("Fashion", "http://www.myvideo.de/service/editorcontentlist/themen/videofashion/creationDate?page=1", 'misch_cat_auto', "",offset=0,orgurl="themenmenu")    
    addDir("Auto &Motor", "http://www.myvideo.de/themen/auto-und-motor", 'mischseite', "",orgurl="themenmenu")
    addDir("TV und Film", "http://www.myvideo.de/themen/tv-und-film", 'mischseite', "",orgurl="themenmenu")
    addDir("Games", "http://www.myvideo.de/games", 'mischseite', "",orgurl="themenmenu")
    addDir("Infotainment", "http://www.myvideo.de/themen/infotainment", 'mischseite', "",orgurl="themenmenu")
    addDir("Sport", "http://www.myvideo.de/themen/sport", 'mischseite', "",orgurl="themenmenu")
    addDir("Comedy", "http://www.myvideo.de/themen/comedy", 'mischseite', "",orgurl="themenmenu")
    addDir("Webisodes", "http://www.myvideo.de/themen/webisodes", 'mischseite', "",orgurl="themenmenu")
    addDir("Telente", "http://www.myvideo.de/themen/talente", 'mischseite', "",orgurl="themenmenu")
    addDir("Livestyle", "http://www.myvideo.de/themen/lifestyle", 'mischseite', "",orgurl="themenmenu")
    addDir("Sexy", "http://www.myvideo.de/themen/sexy", 'mischseite', "",orgurl="themenmenu")
    addDir("Erotik", "http://www.myvideo.de/Erotik", 'mischseite', "",orgurl="themenmenu")
    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    
def musikmenu():
    addDir("Neueste Musik Videos", "http://www.myvideo.de/musik/neue_musik_videos", 'allfilms', "",orgurl="musikmenu")
    addDir("Music Charts", "http://www.myvideo.de/top_100/top_100_single_charts", 'topliste', "",orgurl="musikmenu")
    addDir("Alle Künstler", "http://www.myvideo.de/musik/musik_kuenstler/", 'abisz', "",orgurl="musikmenu")
    addDir("Rock", "http://www.myvideo.de/musik/rock", 'mischseite', "",orgurl="musikmenu")
    addDir("Pop", "http://www.myvideo.de/musik/pop", 'mischseite', "",orgurl="musikmenu")
    addDir("Hip Hop", "http://www.myvideo.de/musik/hiphop", 'mischseite', "",orgurl="musikmenu")
    addDir("Electro", "http://www.myvideo.de/musik/elektro", 'mischseite', "",orgurl="musikmenu")
    addDir("Schlager", "http://www.myvideo.de/musik/schlager", 'mischseite', "",orgurl="musikmenu")
    addDir("Metal", "http://www.myvideo.de/musik/metal", 'mischseite', "",orgurl="musikmenu")
    addDir("RNB", "http://www.myvideo.de/musik/rnb", 'mischseite', "",orgurl="musikmenu")
    addDir("Indie", "http://www.myvideo.de/musik/indie", 'mischseite', "",orgurl="musikmenu")
    addDir("Jazz und Klasik", "http://www.myvideo.de/musik/jazzklassik", 'mischseite', "",orgurl="musikmenu")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    


def searchmenu():
  addDir("Search Musik", "MUSIC", 'search', "",orgurl="searchmenu")
  addDir("Search Tv", "TV", 'search', "",orgurl="searchmenu")
  addDir("Search Film", "FILM", 'search', "",orgurl="searchmenu")
  addDir("Search Channel", "CHANNEL", 'search', "",orgurl="searchmenu")
  addDir("Search All", "ALL", 'search', "",orgurl="searchmenu")
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def search(url):
  urlname="http://www.myvideo.de/search?sortField=&category=" + url +"&rows=10&spellCheckRejected=true&nextButtonCounter=1"
  dialog = xbmcgui.Dialog()
  d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
  url=urlname+"&q=" + d
  misch_cat(url,offset=0)
def  addfav(filename,url,modus,iconimage,desc,name,tab,offset,genre,id,funktion,duration):   
   zeilen=[]
   if xbmcvfs.exists(filename):
        f=open(filename,'r') 
        for line in f:
            if not url in line:
                zeilen.append(line)
        f.close() 
   f=open(filename,'w') 
   for line in zeilen:   
       f.write(line)
   f.write(url+","+modus+","+iconimage+","+desc+","+name+","+tab+","+offset+","+genre+","+id+","+funktion +","+ duration+"\n") 
   f.close()  

def delfav(filename,url,modus,iconimage,desc,name,tab,offset,genre,id,funktion,duration):
   if xbmcvfs.exists(filename):
     zeilen=[]
     f=open(filename,'r') 
     for line in f:
      if not url in line:
         zeilen.append(line)
     f.close() 
   f=open(filename,'w') 
   for line in zeilen:   
       f.write(line)
   f.close() 
   xbmc.executebuiltin("Container.Refresh")
def Favoriten(filename,orgurl=""):
   orgurln="Favoriten"
   debug("++++"+filename)
   f=open(filename) 
   for line in f:
       debug("ZEILE:")
       felder = line.split(",")
       url=felder[0]
       mode=felder[1]
       iconimage=felder[2]
       desc=felder[3]
       name=felder[4]
       tab=felder[5]
       offset=felder[6]
       genre=felder[7]
       id=felder[8]
       funktion=felder[9]       
       if (orgurl!="deltemenu"):
           orgurln="deltemenu"
       debug("-----" + funktion)
       if funktion=="addDir" :
         debug ("addDir("+name+","+ url+","+ mode+","+ iconimage+","+ desc+","+offset+","+tab+","+genre+","+id+","+duration+")")
         addDir(name, url, mode, iconimage, desc,offset,tab,genre,id,duration,orgurl=orgurln)
       if funktion=="addLink" :
         debug ("addLink("+ name +","+ url +","+ mode +","+ iconimage +","+ duration +","+ desc +","+ genre +","+ id +","+ offset+ ","+tab+")")
         addLink(name, url, mode, iconimage, duration, desc, genre,id,offset,tab,orgurl=orgurln)
   f.close() 
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   

def rename(url,name):
   debug("Start rename")
   m = md5.new()
   m.update(url)
   urlnr=m.hexdigest()
   dialog = xbmcgui.Dialog()
   d = dialog.input("Umbenennen",name, type=xbmcgui.INPUT_ALPHANUM)
   zeilen=[]
   filename=temp+"/"+urlnr
   if xbmcvfs.exists(filename):
        f=open(filename,'r') 
        for line in f:
            if not "=,"+urlnr in line:
                zeilen.append(line)
        f.close() 
   f=open(filename,'w')
   for line in zeilen:   
       f.write(line)
   f.write("=,"+urlnr+","+d+"\n") 
   f.close()  
   xbmc.executebuiltin("Container.Refresh")
   
   
def delete(filename,url,modus,iconimage,desc,name,tab,offset,genre,id,funktion,duration,orgurl):
   debug("Start delte")
   m = md5.new()
   m.update(url)   
   urlnr=m.hexdigest()
   filename=temp+"/"+urlnr
   zeilen=[]
   if xbmcvfs.exists(filename):
        f=open(filename,'r') 
        for line in f:
            if not "-,"+urlnr in line:
                zeilen.append(line)
        f.close() 
   f=open(filename,'w')
   for line in zeilen:   
       f.write(line)
   f.write("-,"+urlnr+","+orgurl+"\n") 
   f.close()    
   zeilen=[]
   filename=temp+"/"+"delete.ordner"
   if xbmcvfs.exists(filename):
        f=open(filename,'r') 
        for line in f:
            if not url in line:
                zeilen.append(line)
        f.close() 
   f=open(filename,'w') 
   for line in zeilen:   
       f.write(line)
   f.write(url+","+modus+","+iconimage+","+desc+","+name+","+tab+","+offset+","+genre+","+id+","+funktion +","+ duration+"\n") 
   f.close()  
   xbmc.executebuiltin("Container.Refresh")

   
def undelete(filename,url,modus,iconimage,desc,name,tab,offset,genre,id,funktion,duration,orgurl):
   debug("Start delte")
   m = md5.new()
   m.update(url)   
   urlnr=m.hexdigest()
   filename=temp+"/"+urlnr
   xbmcvfs.delete(filename)
   xbmc.executebuiltin("Container.Refresh")
   filename=temp+"/"+"delete.ordner"
   zeilen=[]
   if xbmcvfs.exists(filename):
        f=open(filename,'r') 
        for line in f:
            if not url in line:
                zeilen.append(line)
        f.close() 
   f=open(filename,'w') 
   for line in zeilen:   
         f.write(line)            
   xbmc.executebuiltin("Container.Refresh")
def showdeletemenu():
  filename=temp+"/"+"delete.ordner"
  if xbmcvfs.exists(filename):
      zeilen=[]
      f=open(filename,'r') 
      for line in f:           
                zeilen.append(line)
      f.close() 
      if len(zeilen) >0:
          return 1
      else :
          return 0
  else:
    return 0
  
  
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
id = urllib.unquote_plus(params.get('id', ''))
offset = urllib.unquote_plus(params.get('offset', ''))
tab = urllib.unquote_plus(params.get('tab', ''))
modus = urllib.unquote_plus(params.get('modus', ''))
iconimage=urllib.unquote_plus(params.get('iconimage', ''))
desc=urllib.unquote_plus(params.get('desc', ''))
name=urllib.unquote_plus(params.get('name', ''))
tab=urllib.unquote_plus(params.get('tab', ''))
genre=urllib.unquote_plus(params.get('genre', ''))
funktion=urllib.unquote_plus(params.get('funktion', ''))
duration=urllib.unquote_plus(params.get('duration', ''))
filename=urllib.unquote_plus(params.get('filename', ''))
orgurl=urllib.unquote_plus(params.get('orgurl', ''))
debug("Filename"+filename)
# Haupt Menu Anzeigen      

if mode is '':    
    addDir("Filme", "Filme", 'filme_menu', "",orgurl="myvideo2")
    addDir("Top Listen", "Top 100", 'top100', "",orgurl="myvideo2")
    addDir("TV & Serien", "TV & Serien", 'tvmenu', "",orgurl="myvideo2")   
    addDir("Themen", "Themen", 'themenmenu', "",orgurl="myvideo2")    
    addDir("Musik", "Musik", 'musikmenu', "",orgurl="myvideo2")  
    addDir("Suche", "Suche", 'searchmenu', "",offset=0,orgurl="myvideo2")          
    filenamen=temp+"/favorit.txt"    
    addDir("Favoriten", "Favoriten", 'Favoriten', "",filename=filenamen,orgurl="myvideo2")     
    if showdeletemenu()==1:
      filenamen=temp+"/"+"delete.ordner"    
      addDir("Delete Menu", "Delete Menu", 'Favoriten', "",filename=filenamen,orgurl="deltemenu") 
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'abisz':
          abisz(url)
  if mode == 'Buchstabe':
          Buchstabe(url)
  if mode == 'Serie':
          Serie(url)
  if mode == 'Staffel':
          Staffel(url)          
  if mode == 'playvideo':
          playvideo(url)
  if mode == 'allfilms':
          allfilms(url)          
  if mode == 'top100':
          top100()               
  if mode == 'topliste':
          topliste(url)   
  if mode == 'topgenres':
          topgenres()                       
  if mode == 'top_zeit':
          top_zeit(url)       
  if mode == 'filme_menu':
          filme_menu()                 
  if mode == 'filmgenres':
          filmgenres()    
  if mode == 'mischseite':
          mischseite(url)    
  if mode == 'misch_cat':
          misch_cat(url,offset) 
  if mode == 'misch_cat_auto':
          misch_cat_auto(url,offset)                   
  if mode == 'misch_tab':
          misch_tab(url,tab)   
  if mode == 'tvmenu':
          tvmenu()       
  if mode == 'themenmenu':
          themenmenu()    
  if mode == 'musikmenu':
          musikmenu()
  if mode == 'searchmenu':
          searchmenu()          
  if mode == 'search':
          search(url)              
  if mode == 'addfav':
          addfav(url=url,modus=modus,iconimage=iconimage,desc=desc,name=name,tab=tab,offset=offset,genre=genre,id=id,funktion=funktion,duration=duration,filename=filename)
  if mode == 'delfav':
          delfav(url=url,modus=modus,iconimage=iconimage,desc=desc,name=name,tab=tab,offset=offset,genre=genre,id=id,funktion=funktion,duration=duration,filename=filename)       
  if mode == 'Favoriten':
          Favoriten(filename=filename,orgurl=orgurl)                        
  if mode == 'rename':
          rename(url,name) 
  if mode == 'delete':
          delete(url=url,modus=modus,iconimage=iconimage,desc=desc,name=name,tab=tab,offset=offset,genre=genre,id=id,funktion=funktion,duration=duration,filename=filename,orgurl=orgurl)       
  if mode == 'undelete':
          undelete(url=url,modus=modus,iconimage=iconimage,desc=desc,name=name,tab=tab,offset=offset,genre=genre,id=id,funktion=funktion,duration=duration,filename=filename,orgurl=orgurl)                     