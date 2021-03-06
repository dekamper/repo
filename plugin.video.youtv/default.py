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
import time
import datetime

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
defaultBackground = ""
defaultThumb = ""
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       

icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATEADDED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)


def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def holejson(url,token=""):  
  empty=[]
  if token=="":
    token=login()
  content=getUrl(url,token=token)
  if content=="":
    return empty
  else:
    struktur = json.loads(content) 
    return struktur

def addDir_fav(name, url, mode, iconimage, desc="",ids=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&ids="+str(ids)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  commands = []
  favdel= "plugin://plugin.video.youtv/?mode=favdel&ids="+urllib.quote_plus(str(ids))
  commands.append(( translation(30139), 'XBMC.RunPlugin('+ favdel +')'))   
  liz.addContextMenuItems( commands )
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addDir(name, url, mode, iconimage, desc="",ids=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&ids="+str(ids)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground
    liz.setProperty("fanart_image", iconimage)
  else:
    liz.setProperty("fanart_image", defaultBackground)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',shortname="",zeit="",production_year="",abo=1,search=""):
  debug ("addLink abo " + str(abo))
  debug ("addLink abo " + str(shortname))
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  commands = []
  finaladd = "plugin://plugin.video.youtv/?mode=addit&url="+urllib.quote_plus(url)
  finaldel = "plugin://plugin.video.youtv/?mode=delit&url="+urllib.quote_plus(url)
  
  seriendel = "plugin://plugin.video.youtv/?mode=sdel&url="+urllib.quote_plus(url)
  serienadd = "plugin://plugin.video.youtv/?mode=sadd&url="+urllib.quote_plus(url)
  
  download = "plugin://plugin.video.youtv/?mode=download&url="+urllib.quote_plus(url) 
  search = "plugin://plugin.video.youtv/?mode=Search&wort="+urllib.quote_plus(search)+"&url="
  # Langzeitarchiv/Serien erst ab Pro-Account
  commands.append(( translation(30143), 'ActivateWindow(Videos,'+ search +')'))
  if abo >3 :
    commands.append(( translation(30112), 'XBMC.RunPlugin('+ finaladd +')'))   
    commands.append(( translation(30113), 'XBMC.RunPlugin('+ finaldel +')'))   
    commands.append(( translation(30114), 'XBMC.RunPlugin('+ serienadd +')'))   
    commands.append(( translation(30115), 'XBMC.RunPlugin('+ seriendel +')'))      
  # Download erst ab Basic-Account
  if cd=="4921" or abo>1:
     commands.append(( translation(30116), 'XBMC.RunPlugin('+ download +')'))    
  debug("1.")     
  liz.addContextMenuItems( commands )
  debug("2.")     
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  debug("3.")     
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)  
  debug("4.")     
  return ok

def addLinkarchive(name, url, mode, iconimage, duration="", desc="", genre='',shortname="",zeit="",production_year=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  commands = []
  download = "plugin://plugin.video.youtv/?mode=download&url="+urllib.quote_plus(url)    
  finaldel = "plugin://plugin.video.youtv/?mode=delit&url="+urllib.quote_plus(url)    
  serienadd = "plugin://plugin.video.youtv2/?mode=sadd&url="+urllib.quote_plus(url)
  commands.append(( translation(30113), 'XBMC.RunPlugin('+ finaldel +')'))   
  commands.append(( translation(30114), 'XBMC.RunPlugin('+ serienadd +')'))
  commands.append(( translation(30116), 'XBMC.RunPlugin('+ download +')'))   
  liz.addContextMenuItems( commands )
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok
  
  
def addLinkSeries(name, url, mode, iconimage, duration="", desc="", genre=''):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setProperty("fanart_image", iconimage)
  #liz.setProperty("fanart_image", defaultBackground)
  commands = []
  seriendel = "plugin://plugin.video.youtv/?mode=sdeldirekt&url="+urllib.quote_plus(url)  
  commands.append(( translation(30115), 'XBMC.RunPlugin('+ seriendel +')'))         
  liz.addContextMenuItems( commands )
  xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
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
  
  
def getUrl(url,data="x",token=""):
        https=addon.getSetting("https")
        if https=="true":
           url=url.replace("https","http")
        print("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "YOUTV/1.2.7 CFNetwork/758.2.8 Darwin/15.0.0"
        if token!="":
           mytoken="Token token="+ token
           opener.addheaders = [('User-Agent', userAgent),
                                ('Authorization', mytoken)]
        else:
           opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             struktur = json.loads(cc)  
             error=struktur["errors"][0] 
             error=unicode(error).encode("utf-8")
             debug("ERROR : " + error)
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content
def cachelear():
    if xbmcvfs.exists(temp+"/token")  :
      xbmcvfs.delete(temp+"/token")
      if not xbmcvfs.exists(temp+"/token")  :
         dialog2 = xbmcgui.Dialog()
         ok = xbmcgui.Dialog().ok( translation(30142), translation(30142) )
    
def login():
   global addon   
   if xbmcvfs.exists(temp+"/token")  :
     f=xbmcvfs.File(temp+"/token","r")   
     token=f.read()
   else:
      user=addon.getSetting("user")        
      password=addon.getSetting("pw") 
      debug("User :"+ user)
      values = {
         'auth_token[password]' : password,
         'auth_token[email]' : user
      }
      data = urllib.urlencode(values)
      content=getUrl("https://www.youtv.de/api/v2/auth_token.json?platform=ios",data=data)
      struktur = json.loads(content)   
      token=struktur['token']
      f = open(temp+"token", 'w')           
      f.write(token)        
      f.close()    
   
   return token
   
def Genres():
   url="https://www.youtv.de/api/v2/genres.json?platform=ios"
   token=login()  
   content=getUrl(url,token=token)        
   struktur = json.loads(content)
   themen=struktur["genres"]   
   for name in themen:
      namen=unicode(name["name"]).encode("utf-8")
      id=name["id"]   
      addDir(namen, namen, "Subgeneres","",ids=str(id))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   
def subgenres(ids):
  debug("IDS: "+ ids)
  url="https://www.youtv.de/api/v2/genres.json?platform=ios"  
  token=login()  
  content=getUrl(url,token=token)        
  struktur = json.loads(content)
  themen=struktur["genres"]   
  for name in themen:
      id=name["id"]  
      debug("ID: "+ str(id))
      if str(id)==str(ids) :         
         subgen=name["genres"] 
         addDir("Alle", "Alle", "listgenres","",ids=str(id))         
         for subname in subgen:
            namen=unicode(subname["name"]).encode("utf-8")
            id=subname["id"]    
            addDir(namen, namen, "listgenres","",ids=str(id))
         break
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
  
def abodauer(token="")  :
   if token=="":
       token=login()   
   content=getUrl("https://www.youtv.de/api/v2/subscription.json?platform=ios",token=token)
   debug("Subcription: ")
   debug(content)
   struktur = json.loads(content)       
   tage=struktur["subscription"]["history_days"]         
   return tage
   
def getThemen(url,filter):   
   token=login()   
   tage=abodauer(token)
   if filter=="channels" :
     datuma=[translation(30121),translation(30122)]    
     sprache=xbmc.getLanguage(xbmc.ISO_639_1)
     # ---------------------------------------
     # locale bei OPENELEC nicht installiert !
     # ---------------------------------------
     #if sprache=="de":
        #try:           
        #   locale.setlocale(locale.LC_ALL, 'de_DE')
        #except:
        #   locale.setlocale(locale.LC_ALL, 'deu_deu')       
     for i in xrange(2, tage):        
       if sprache=="de":
         Tag=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(i),'%w')
         datuma.append(translation(30130 + int(Tag)))
       else:
         Tag=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(i),'%A')
         datuma.append(Tag)
     dialog = xbmcgui.Dialog()
     nr=dialog.select("Datum", datuma)
     if nr==-1:
        return 1
     tagit=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(nr),'%Y-%m-%d')
     datum="&date="+tagit
     
   else:
     datum=""
   content=getUrl(url,token=token)     
   debug("+X:"+ content)
   struktur = json.loads(content)
   themen=struktur[filter]   
   namenliste=[]
   idliste=[]
   logoliste=[]
   sortnamen=[]
   for name in themen:
      namen=unicode(name["name"]).encode("utf-8")
      sortnamen.append(namen.lower())
      namenliste.append(namen)
      idliste.append(name["id"])       
      if filter=="filters" :
         mode="listtop"
         logo=""
      if filter=="channels" :
         mode="listtv"       
         logo=name["logo"][0]["url"]   
      logoliste.append(logo)  
   sortnamen,namenliste, idliste,logoliste = ( list(x) for x in zip(*sorted(zip(sortnamen,namenliste, idliste,logoliste))))
   for i in range(len(namenliste)):
      addDir(namenliste[i], namenliste[i], mode+datum,logoliste[i],ids=str(idliste[i]))
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def liste(url,filter):
   datums = urllib.unquote_plus(params.get('date', ''))
   if  datums!="":
     url=url+"&date="+ datums    
   debug("+++- :"+ url)
   token=login()
   tage=abodauer(token)
      
   content=getUrl(url,token=token) 
   debug("+X:"+ content)
   struktur = json.loads(content)   
   themen=struktur[filter]    
   zeigedate=addon.getSetting("zeigedate")
   for name in themen:
     #2016-02-26T21:15:00.000+01:00
     
     endtime=unicode(name["ends_at"]).encode("utf-8")     
     match=re.compile('(.+?)\..+', re.DOTALL).findall(endtime)
     endtime=match[0]     
     timeString  = time.strptime(endtime,"%Y-%m-%dT%H:%M:%S")
     enttime=time.mktime(timeString)
     
     st=unicode(name["starts_at"]).encode("utf-8")
     starttime=st
     match=re.compile('(.+?)\..+', re.DOTALL).findall(starttime)
     starttime=match[0]  
     timeString  = time.strptime(starttime,"%Y-%m-%dT%H:%M:%S")     
     starttime=time.mktime(timeString)
     
     nowtime=time.mktime(datetime.datetime.now().timetuple())
     diftime=nowtime-starttime
     diftime2=int(diftime/  86400)       
     match=re.compile('(.+?)-(.+?)-(.+?)T(.+?):(.+?):', re.DOTALL).findall(st)
     if zeigedate!="false": 
       times=match[0][2] +"."+ match[0][1] +"."+ match[0][0] +" "+ match[0][3] +":"+match[0][4]
     else:
       times=match[0][3] +":"+match[0][4]
     start=match[0][0] +"."+ match[0][1] +"."+ match[0][2] +" "+ match[0][3] +":"+match[0][4] +":00"
     title=unicode(name["title"]).encode("utf-8")
     search=unicode(name["title"]).encode("utf-8")
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "None":
       title=title+" ( "+subtitle +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     production_year=unicode(name["production_year"]).encode("utf-8")      
     if enttime < nowtime:
       if filter!="archived_broadcasts":
         if diftime2 < tage:
	   # Mediathek begrenzt durch Abodauer (Free = 1 Tag, Basic-Abo = 3 Tage, Pro-Abo = 7 Tage)
           addLink(times + " - " + title, id, "playvideo", bild, duration=duration, desc="", genre=genres,shortname=title,zeit=start,production_year=production_year,abo=tage,search=search)
       else:
	 # Langzeitarchiv ohne Begrenzung durch Abodauer
         addLinkarchive(times + " - " + title, id, "playvideo", bild, duration=duration, desc="", genre=genres, shortname=title, zeit=start, production_year=production_year)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

   
   
def download(id):  
  download_dir=addon.getSetting("download_dir")    
  if download_dir=="":
       dialog = xbmcgui.Dialog()
       dialog.select(translation(30117), translation(30118)  )
       return 0
  quaname=[]
  qalfile=[]
  qname=[]
  bitrate=addon.getSetting("bitrate")
  debug("ID :::"+ id)
  token=login()
  content=getUrl("https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios",token=token)
  debug("+X+ :"+ content)
  struktur = json.loads(content) 
  qulitaet=struktur["files"]
  nq=""
  hq=""
  hd=""

  for name in qulitaet:  
     quaname.append(name["quality_description"])
     qalfile.append(name["file"])  

     # Normal 
     if name["quality"]=="nq" :        
        nq=name["file"]        

     # High Quality 
     if name["quality"]=="hq" :
        hq=name["file"]     

     # HD
     if name["quality"]=="hd" :
        hd=name["file"]

  #MAX      
  if hd!="":
      max=hd
  elif hq!="":
      max=hq
  else :
      max=nq  
  #MIN
  if nq!="":
    min=nq
  elif hq!="":
    min=hq
  else:
    min=hd
  if bitrate=="Min":
    file=min      
  if bitrate=="Max":
     file=max
  if bitrate=="Select":
     dialog = xbmcgui.Dialog()
     nr=dialog.select("Bitrate", quaname)      
     file=qalfile[nr]  
     
  file_name = file.split('/')[-1]     
  progress = xbmcgui.DialogProgress()
  progress.create("Youtv",translation(30119),file_name)
  u = urllib2.urlopen(file)
  f = open(os.path.join(download_dir, file_name), 'wb')
  meta = u.info()
  file_size = int(meta.getheaders("Content-Length")[0])
  #print "Downloading: %s Bytes: %s" % (file_name, file_size)

  file_size_dl = 0
  block_sz = 16384
  while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    process= int( file_size_dl * 100. / file_size)
    progress.update(process)
    if progress.iscanceled():         
        progress.close()
        f.close()
        break
  f.close()
  
  
  
  #progress.create('Progress', 'This is a progress bar.')     
  #urllib.urlretrieve (file, temp+"/mp3.mp3")
  #print("####"+   content)

# - Bereits definiert -
#params = parameters_string_to_dict(sys.argv[2])
#mode = urllib.unquote_plus(params.get('mode', ''))
#url = urllib.unquote_plus(params.get('url', ''))
#ids = urllib.unquote_plus(params.get('ids', ''))
#genid = urllib.unquote_plus(params.get('genid', ''))

   
   
#List Serien Einträge   
def Series(url,filter):
   
   token=login()
   content=getUrl(url,token=token) 
   debug("+X:"+ content)
   struktur = json.loads(content)   
   themen=struktur[filter]   
   for name in themen:
     #2016-02-26T21:15:00.000+01:00       
     title=unicode(name["title"]).encode("utf-8")
     id=str(name["id"])     
     addLinkSeries(title, id, "", "", duration="", desc="", genre="")
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
   

def playvideo(id):  
  quaname=[]
  qalfile=[]
  qname=[]
  bitrate=addon.getSetting("bitrate")
  debug("ID :::"+ id)
  url="https://www.youtv.de/api/v2/broadcast_files/"+ str(id) +".json?platform=ios"
  struktur=holejson(url)  
  debug(struktur)
  if len(struktur)==0:
     return 1   
  qulitaet=struktur["files"]
  nq=""
  hq=""
  hd=""

  for name in qulitaet:  
     quaname.append(name["quality_description"])
     qalfile.append(name["file"])  

     # Normal 
     if name["quality"]=="nq" :        
        nq=name["file"]        

     # High Quality 
     if name["quality"]=="hq" :
        hq=name["file"]     

     # HD
     if name["quality"]=="hd" :
        hd=name["file"]

  #MAX      
  if hd!="":
      max=hd
  elif hq!="":
      max=hq
  else :
      max=nq  
  #MIN
  if nq!="":
    min=nq
  elif hq!="":
    min=hq
  else:
    min=hd
  if bitrate=="Min":
    file=min      
  if bitrate=="Max":
     file=max
  if bitrate=="Select":
     dialog = xbmcgui.Dialog()
     nr=dialog.select("Bitrate", quaname)      
     file=qalfile[nr]  
  listitem = xbmcgui.ListItem(path=file)  
  xbmcplugin.setResolvedUrl(addon_handle,True, listitem)  
   
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
ids = urllib.unquote_plus(params.get('ids', ''))
genid = urllib.unquote_plus(params.get('genid', ''))
wort=""
wort = urllib.unquote_plus(params.get('wort', ''))
def search(url="",wort=""):
   debug("SEARCH URL :"+url)
   filter="broadcasts"
   if wort=="":
     dialog = xbmcgui.Dialog()
     d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
     d=urllib.quote(d, safe='')
   else:
     d=urllib.quote(wort, safe='')
   token=login()
   tage=abodauer(token)
   content=getUrl("https://www.youtv.de/api/v2/broadcasts/search.json?q="+ d +"&platform=ios",token=token)
   debug("Content")
   struktur = json.loads(content)   
   themen=struktur[filter]      
   zeigedate=addon.getSetting("zeigedate")
   for name in themen:
     title=unicode(name["title"]).encode("utf-8")
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "None":
       title=title+" ( "+subtitle +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     production_year=unicode(name["production_year"]).encode("utf-8") 
     
     endtime=unicode(name["ends_at"]).encode("utf-8")     
     match=re.compile('(.+?)\..+', re.DOTALL).findall(endtime)
     endtime=match[0]     
     timeString  = time.strptime(endtime,"%Y-%m-%dT%H:%M:%S")
     enttime=time.mktime(timeString)
     
     st=unicode(name["starts_at"]).encode("utf-8")
     starttime=st
     match=re.compile('(.+?)\..+', re.DOTALL).findall(starttime)
     starttime=match[0]  
     timeString  = time.strptime(starttime,"%Y-%m-%dT%H:%M:%S")     
     starttime=time.mktime(timeString)
     
     nowtime=time.mktime(datetime.datetime.now().timetuple())
     diftime=nowtime-starttime
     diftime2=int(diftime/  84400)       
          
     match=re.compile('(.+?)-(.+?)-(.+?)T(.+?):(.+?):', re.DOTALL).findall(st)
     if zeigedate!="false": 
       times=match[0][2] +"."+ match[0][1] +"."+ match[0][0] +" "+ match[0][3] +":"+match[0][4] +" "
     else:
       times=match[0][3] +":"+match[0][4] +" "
     start=match[0][0] +"."+ match[0][1] +"."+ match[0][2] +" "+ match[0][3] +":"+match[0][4] +":00"
     title=unicode(name["title"]).encode("utf-8")
     search=unicode(name["title"]).encode("utf-8")
     subtitle=unicode(name["subtitle"]).encode("utf-8")
     if subtitle!= "None":
       title=title+" ( "+subtitle +" )"
     id=str(name["id"])
     bild=unicode(name["image"][0]["url"]).encode("utf-8")
     duration=str(name["duration"])
     genres=unicode(name["genre"]["name"]).encode("utf-8") 
     production_year=unicode(name["production_year"]).encode("utf-8")      
     if enttime < nowtime and diftime2<tage:             
       debug("Adde Link")
       addLink(times + " - " + title, id, "playvideo", bild, duration=duration, desc="", genre=genres,shortname=title,zeit=start,production_year=production_year,abo=tage,search=search)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
# Haupt Menu Anzeigen      

def addit(id):
  token=login()                  
#  content=getUrl("https://www.youtv.de/api/v2/broadcasts/"+ str(id) +".json?platform=ios",token=token)
#  debug(content)  
#  struktur = json.loads(content) 
#  sendung=struktur["broadcast"]  
#https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios      archived_broadcast[id]:  299501
  values = {
         'archived_broadcast[id]' : id         
  }
  data = urllib.urlencode(values)
  content=getUrl("https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios",token=token,data=data)

def delit(id=0,url=""):
  debug("----- id :" +str(id))
  debug("---- URL ;"+str(url))
  token=login() 
  mytoken="Token token="+ token
  userAgent = "YOUTV/1.2.7 CFNetwork/758.2.8 Darwin/15.0.0"  
  if id>0:
    query_url = "https://www.youtv.de/api/v2/archived_broadcasts/"+ str(id)+".json?platform=ios"
  else:
     query_url ="https://www.youtv.de/api/v2/search_texts/"+str(url)+".json?locale=de&platform=android&version_code=9&platform_version=21"    
  debug("---- query_url :"+query_url)
  headers = {
      'User-Agent': userAgent,
      'Authorization': mytoken
  }        
  debug(headers)  
  opener = urllib2.build_opener(urllib2.HTTPHandler)
  req = urllib2.Request(query_url, None, headers)
  req.get_method = lambda: 'DELETE' 
  url = urllib2.urlopen(req) 
  xbmc.executebuiltin("Container.Refresh")


def serienadd(ids):
    token=login()   
    content=getUrl("https://www.youtv.de/api/v2/broadcasts/"+ str(ids) +".json?platform=ios",token=token)
    debug("content :"+content)
    struktur = json.loads(content)   
    serien=struktur["broadcast"]   
    serie=serien["series_id"]
    if serie==None:
       dialog = xbmcgui.Dialog()
       dialog.ok(translation(30117), translation(30120))    
    else:
       serienadd_direkt(serie)    
    
def serienadd_direkt(serie)    :    
      token=login()
      values = {
         'archived_series[id]' : serie
      } 
      data = urllib.urlencode(values)
      content=getUrl("https://www.youtv.de/api/v2/archived_series.json?platform=ios",token=token,data=data)

      
def seriendel(ids):
    token=login()                
    content=getUrl("https://www.youtv.de/api/v2/broadcasts/"+ str(ids) +".json?platform=ios",token=token)
    debug("content :"+content)
    struktur = json.loads(content)   
    serien=struktur["broadcast"]   
    serie=serien["series_id"]
    seriendel_direkt(serie)
    
def seriendel_direkt(serie):
    token=login()
    query_url = "https://www.youtv.de/api/v2/archived_series.json?id="+ str(serie)  +"&platform=ios"
    userAgent = "YOUTV/1.2.7 CFNetwork/758.2.8 Darwin/15.0.0"  
    mytoken="Token token="+ token
    headers = {
        'User-Agent': userAgent,
        'Authorization': mytoken
    }     
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(query_url, None, headers)
    req.get_method = lambda: 'DELETE' 
    url = urllib2.urlopen(req) 
    xbmc.executebuiltin("Container.Refresh")

def Favoritenfiner():
   token=login()
   content=getUrl("https://www.youtv.de/api/v2/search_texts.json?locale=de&platform=android&version_code=9&platform_version=21",token=token)
   addDir(translation(30138), translation(30138), 'AddFav', "")
   struktur = json.loads(content)    
   for element in struktur["search_texts"]:
       debug("-------")
       debug(element)
       debug("-------")
       text=element["text"]
       url=element["broadcasts_url"]
       id=element["id"]
       debug(element)
       addDir_fav(text, url, 'ListFav', "",ids=id)               
   #Text=struktur{"search_texts"}["Text"]
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def AddFav():
   dialog = xbmcgui.Dialog()
   d = dialog.input(translation(30010), type=xbmcgui.INPUT_ALPHANUM)
   d=urllib.quote(d, safe='')
   token=login()
   values = {
         'search_text[text]' : d,
   }
   data = urllib.urlencode(values)
   content=getUrl("https://www.youtv.de/api/v2/search_texts.json?locale=de&platform=android&version_code=9&platform_version=21",token=token,data=data)
   xbmc.executebuiltin("Container.Refresh")

def favdel(ids):
   debug("2. IDS"+ str(ids))  
   delit(url=ids)
   
if mode is '':
    tage=abodauer()
    addDir(translation(30103), translation(30001), 'TOP', "")
    addDir(translation(30104), translation(30005), 'Genres',"")
    addDir(translation(30105), translation(30006), 'Sender', "")   
    addDir(translation(30107), translation(30107), 'Search', "")  
    addDir(translation(30137), translation(30137), 'Favoritenfiner', "")  
    # Langzeitarchiv / Serienaufnahme erst ab Pro-Abo
    if tage > 3:
       addDir(translation(30108), translation(30108), 'Archive',"")  
       addDir(translation(30123), translation(30123), 'Series',"")  
    addDir(translation(30106), translation(30106), 'Settings', "")        
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'TOP':
          getThemen("https://www.youtv.de/api/v2/filters.json?platform=ios","filters")
  if mode == 'Genres':
          Genres()  
  if mode == 'Sender':
          getThemen("https://www.youtv.de/api/v2/channels.json?platform=ios ","channels")             
  if mode == 'listtv':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/channels/"+ ids +"/broadcasts.json?platform=ios","broadcasts")                 
  if mode == 'listgenres':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/genres/"+ ids +"/broadcasts.json?platform=ios","broadcasts")                 
  if mode == 'listtop':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/filters/"+ ids +"/broadcasts.json?platform=ios","broadcasts")                           
  if mode == 'Archive':
          #date=2016-02-26&
          liste("https://www.youtv.de/api/v2/archived_broadcasts.json?platform=ios","archived_broadcasts")                      
  if mode == 'Series':
          #date=2016-02-26&
          Series("https://www.youtv.de/api/v2/archived_series.json?platform=ios","archived_series")                                
  if mode == 'playvideo':  
          playvideo(url)  
  if mode == 'Search':  
          search(url,wort=wort)           
  if mode == 'addit':  
          addit(url)
  if mode == 'delit':  
          delit(id=url)          
  if mode == 'Subgeneres':  
          subgenres(ids)
  if mode == 'sadd':  
          serienadd(url)    
  if mode == 'sdel':  
          seriendel(url)
  if mode == 'sadddirekt':  
          serienadd_direkt(url) 
  if mode == 'sdeldirekt':              
          seriendel_direkt(url)
  if mode == 'Favoritenfiner':              
          Favoritenfiner()        
  if mode == 'ListFav':              
          liste(url,"broadcasts")
  if mode == 'AddFav':              
          AddFav()
  if mode == 'favdel': 
          debug("1. IDS" + str(ids)) 
          favdel(ids)          
  if mode == 'download':              
          download(url)
  if mode == 'cachelear':              
          cachelear()
          
