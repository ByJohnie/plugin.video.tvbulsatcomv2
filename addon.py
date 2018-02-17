# -*- coding: utf-8 -*-
#Библиотеки, които използват python и Kodi в тази приставка
import re
import sys
import os
import urllib
import urllib2
import cookielib
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
#Encrypt
import aes as aes
import base64
import xml.etree.ElementTree as ET


#Място за дефиниране на константи, които ще се използват няколкократно из отделните модули
__addon_id__= 'plugin.video.tvbulsatcomv2'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.tvbulsatcomv2')
__addondir__    = xbmc.translatePath( __Addon.getAddonInfo('profile') ) 
app = base64.b64decode('YXBpLmlwdHYuYnVsc2F0LmNvbQ==')
videoteka = base64.b64decode('L3ZvZC9zdGIv')
md = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/media/")
UA = 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.3) AppleWebkit/538.1 (KHTML, like Gecko) SamsungBrowser/1.0 TV Safari/538.1'
username = xbmcaddon.Addon().getSetting('settings_username')
password = xbmcaddon.Addon().getSetting('settings_password')
if not username or not password or not __settings__:
        xbmcaddon.Addon().openSettings()
        #xbmcaddon.Addon().setSettings('settings_notification', 'false')


#Инициализация

url = ('https://' + app + '/auth')
print url
req = urllib2.Request(url)
req.add_header('Host', app)
req.add_header('Connection', 'keep-alive')
req.add_header('Origin', app)
req.add_header('User-Agent', UA)
req.add_header('Accept-Language', 'bg-BG,bg;q=0.9')
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
f = opener.open(req)
data = f.read()
info = f.info()
key = info.getheader('CHALLENGE')
enc = aes.AESModeOfOperationECB(key)
password_crypt = enc.encrypt(password + (16 - len(password) % 16) * '\0')
passw = base64.b64encode(password_crypt)
params ={
        'user': username,
        'device_id': 'samsungtv',
        'device_name': 'Samsung Smart TV',
        'os_version':'5.1.2',
        'os_type':'samsungtv',
        'app_version':'0.36',
        'pass': passw
}
url = ('https://' + app + '/?auth')
req = urllib2.Request(url, urllib.urlencode(params))
req.add_header('Host', app)
req.add_header('Connection', 'keep-alive')
req.add_header('Origin', app)
req.add_header('User-Agent', UA)
req.add_header('Accept-Language', 'bg-BG,bg;q=0.9')
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
f = opener.open(req)
jsonrsp = json.loads(f.read())
logged=jsonrsp['Logged']
#Меню с директории в приставката
def CATEGORIES():
        #Категории
        if logged=='true':
                addDir('ТЕЛЕВИЗИЯ','https://'+app+'/tv/','',4,md+'DefaultFolder.png')
                addDir('Радио','https://'+app+'/tv/','',5,md+'DefaultFolder.png')
                addDir('Видеотека','https://'+app+videoteka,'',1,md+'DefaultFolder.png')
                addDir('Генерирай плейлиста','https://'+app+'/tv/','',7,md+'DefaultFolder.png')
        if logged=='false':
                xbmcgui.Dialog().ok('Грешка 199','Внимание! Приложението може да се използва спрямо активните Ви абонаменти. Вече използвате приложението с максимално допустимите устройства. Телефон 0700 319 19')

def VIDEOTEK(url):
        #Жанрове
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        jsonrsp = json.loads(f.read())
                
        for genre in range(0, len(jsonrsp)):
                addDir(jsonrsp[genre]['title'].encode('utf-8', 'ignore'),str(genre),'',2,md+'DefaultFolder.png')
            
#Разлистване на групите
def GROUPS(url):
        try:
            url = int(url) #правим поредния номер на групата Отново число
            req = urllib2.Request('https://'+app+videoteka)
            req.add_header('User-Agent', UA)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            f = opener.open(req)
            jsonrsp = json.loads(f.read())
            #print jsonrsp[0]['childs'][0]['title'].encode('utf-8', 'ignore')  
            for genre in range(0, len(jsonrsp[url]['childs'])):
                addDir(jsonrsp[url]['childs'][genre]['title'].encode('utf-8', 'ignore'),jsonrsp[url]['childs'][genre]['id']+'/1','',3,md+'DefaultFolder.png')
        except:
            addDir('Go back - there are no results','','','',md+'DefaultFolderBack.png')

#Разлистване на заглавията
def INDEX(url):
        try:
            req = urllib2.Request('https://'+app+videoteka+url)
            req.add_header('User-Agent', UA)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            f = opener.open(req)
            jsonrsp = json.loads(f.read())
            for videos in range(0, len(jsonrsp)):
                addLink(jsonrsp[videos]['title'].encode('utf-8', 'ignore'),jsonrsp[videos]['source'][3]['link'],jsonrsp[videos]['description'].replace('\n', ' ').encode('utf-8', 'ignore'),int(jsonrsp[videos]['duration'])*60,6,jsonrsp[videos]['poster'])
             #Ако имаме още страници...
            matchp = re.compile('(.+?)/(\d+)').findall(url)
            for gid, cpage in matchp:
               if len(jsonrsp)==10:
                   addDir('Към страница '+str(int(cpage)+1)+' >>',gid+'/'+str(int(cpage)+1),'',3,md+'DefaultFolder.png')

        except:
            addDir('Go back - there are no results','','','',md+'DefaultFolderBack.png')

def INDEXTV(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        jsonrsp = json.loads(f.read())
        for tv in jsonrsp:
                radio = str(tv['radio'])
                name = tv['title'].encode('utf-8', 'ignore')
                genre = tv['genre'].encode('utf-8', 'ignore')
                source = tv['sources'].encode('utf-8', 'ignore')
                logo = tv['logo'].encode('utf-8', 'ignore')
                
                try:
                        desc = 'Качество: ' + tv['quality'].encode('utf-8', 'ignore').replace('-SMIL','') + ' Категория: ' + genre + ' В момента: ' + tv['program']['title'].encode('utf-8', 'ignore') + ' - ' + tv['program']['desc'].encode('utf-8', 'ignore')
                except:
                        desc = 'Качество: ' + tv['quality'].encode('utf-8', 'ignore').replace('-SMIL','') + ' Категория: ' + genre
                channel = radio + '@' + name + '@' + source + '@' + logo + '@' + desc
                match = re.compile('False@(.+?)@(.+?)@(.+?)@(.*)').findall(channel)
                for title,url,thumbnail,opisanie in match:       
                 addLink2(title,url,6,desc,thumbnail)

def INDEXRADIO(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        jsonrsp = json.loads(f.read())
        for tv in jsonrsp:
                radio = str(tv['radio'])
                name = tv['title'].encode('utf-8', 'ignore')
                genre = tv['genre'].encode('utf-8', 'ignore')
                source = tv['sources'].encode('utf-8', 'ignore')
                logo = tv['logo'].encode('utf-8', 'ignore')
                
                try:
                        desc = 'Качество: ' + tv['quality'].encode('utf-8', 'ignore').replace('-SMIL','') + ' Категория: ' + genre + ' В момента: ' + tv['program']['title'].encode('utf-8', 'ignore') + ' - ' + tv['program']['desc'].encode('utf-8', 'ignore')
                except:
                        desc = 'Качество: ' + tv['quality'].encode('utf-8', 'ignore').replace('-SMIL','') + ' Категория: ' + genre
                channel = radio + '@' + name + '@' + source + '@' + logo + '@' + desc
                match = re.compile('True@(.+?)@(.+?)@(.+?)@(.*)').findall(channel)
                for title,url,thumbnail,opisanie in match:       
                 addLink2(title,url,6,desc,thumbnail)
                
#Зареждане на видео
def PLAY(name,url,iconimage):
        li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=url+'|User-Agent='+urllib.quote_plus(UA)+'&Referer=https://'+app)
        li.setInfo( type="Video", infoLabels={ 'title': name, "plot": "описание" } )
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
        
def indent(elem, level=0):
        i = "\n" + level*"  "
        j = "\n" + (level-1)*"  "
        if len(elem):
         if not elem.text or not elem.text.strip():
          elem.text = i + " "
        if not elem.tail or not elem.tail.strip():
         elem.tail = i
        for subelem in elem:
         indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
         elem.tail = j
        else:
         if level and (not elem.tail or not elem.tail.strip()):
          elem.tail = j
        return elem 
          
def M3U8GENERATOR(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        jsonrsp = json.loads(f.read())
        f = xbmcvfs.File(__addondir__+'bulsat.m3u', 'w')
        template = '#EXTINF:-1 radio="%s" tvg-id="%s" tvg-logo="%s" tvg-name="%s" group-title="%s",%s\n%s\n'
        data = '#EXTM3U\n'
        for video in jsonrsp:
         name = video['title'].encode('utf-8', 'ignore')
         genre = video['genre'].encode('utf-8', 'ignore')
         epg = video['epg_name'].encode('utf-8', 'ignore')
         radio = str(video['radio'])
         source = video['sources'].encode('utf-8', 'ignore')+'|User-Agent='+urllib.quote_plus(UA)
         logo = video['logo'].encode('utf-8', 'ignore')
         data += template % (radio, epg, logo, epg, genre, name, source)
        f.write(data)
        f.close()
        params = {'epg': '3hour'}
        req = urllib2.Request('https://'+app+'//epg/short/', urllib.urlencode(params))
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        #jsonrsp = json.loads(f.read())
        #data = f.read()
        channels = json.load(opener.open(req))
        tv = ET.Element("tv")
        for key, channel in channels.iteritems():
         c = ET.SubElement(tv, "channel", id=key)
         ET.SubElement(c, "display-name").text = channel["name"]
         ET.SubElement(c, "icon", src=channel.get("placeholder").replace("\/", "/"))
         if channel.get("programme"):
            for program in channel["programme"]:
              program_tag = ET.SubElement(tv, "programme", start=program["start"], stop=program["stop"], channel=key)
              ET.SubElement(program_tag, "title").text = program["title"].rstrip()
              ET.SubElement(program_tag, "desc").text = program.get("desc").rstrip()
              tree = ET.ElementTree(tv)
              indent(tv)  
              tree.write(__addondir__+"epg.xml",encoding="UTF-8",xml_declaration=True)


        kodiversion = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
        if kodiversion < 17:
                #връщане в начално положение
                xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
                #заспиване до начално положение
                xbmc.sleep(2000)
                #спиране на пвр
                xbmc.executebuiltin('XBMC.StopPVRManager')
                #пвр старт
                xbmc.executebuiltin('XBMC.StartPVRManager')
                xbmcgui.Dialog().ok('ПВР Рестарт','ПВР е рестартиран, моля натиснете ОК и посетете раздел Телевизия')
                xbmc.executebuiltin('ActivateWindow(home)')
                
        else:
                #връщане в начално положение
                xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
                #заспиване до начално положение
                xbmc.sleep(2000)
                #спиране на пвр
                xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Addons.SetAddonEnabled", "params":{ "addonid": "pvr.iptvsimple", "enabled": false }, "id":1}')
                #пвр старт
                xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Addons.SetAddonEnabled", "params":{ "addonid": "pvr.iptvsimple", "enabled": true }, "id":1}')
                xbmcgui.Dialog().ok('ПВР Рестарт','ПВР е рестартиран, моля натиснете ОК и посетете раздел Телевизия')
                xbmc.executebuiltin('ActivateWindow(home)')

#Модул за добавяне на отделно заглавие и неговите атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addLink(name,url,plot,vd,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': iconimage, 'banner' : iconimage, 'fanart': iconimage })
        liz.setInfo( type="Video", infoLabels={ "duration": vd, "plot": plot } )
        liz.addStreamInfo('video', { 'width': 1280, 'height': 720 })
        liz.addStreamInfo('video', { 'aspect': 1.78, 'codec': 'h264' })
        liz.addStreamInfo('audio', { 'codec': 'aac', 'channels': 2 })
        liz.setProperty("IsPlayable" , "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
def addLink2(name,url,mode,plot,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': iconimage, 'banner' : iconimage, 'fanart': iconimage })
        liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": plot })
        liz.addStreamInfo('video', { 'aspect': 1.78, 'codec': 'h264' })
        liz.addStreamInfo('audio', { 'codec': 'aac', 'channels': 2 })
        liz.setProperty("IsPlayable" , "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

#Модул за добавяне на отделна директория и нейните атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addDir(name,url,plot,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


#НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param



params=get_params()
url=None
name=None
iconimage=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass


#Списък на отделните подпрограми/модули в тази приставка - трябва напълно да отговаря на кода отгоре
if mode==None or url==None or len(url)<1:
        CATEGORIES()

elif mode==1:
        VIDEOTEK(url)
    
elif mode==2:
        GROUPS(url)

elif mode==3:
        INDEX(url)

elif mode==4:
        INDEXTV(url)

elif mode==5:
        INDEXRADIO(url)
                       
elif mode==6:
        PLAY(name,url,iconimage)

elif mode==7:
        M3U8GENERATOR(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
