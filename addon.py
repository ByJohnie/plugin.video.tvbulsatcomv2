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
print logged
#Меню с директории в приставката
def CATEGORIES():
        #Категории
        if logged=='true':
                addDir('ТЕЛЕВИЗИЯ','https://'+app+'/tv/','',4,md+'DefaultFolder.png')
                addDir('Радио','https://'+app+'/tv/','',5,md+'DefaultFolder.png')
                addDir('Видеотека','https://'+app+videoteka,'',1,md+'DefaultFolder.png')
                addDir('Генерирай плейлиста','https://'+app+'/tv/','',7,md+'DefaultFolder.png')
        if logged=='false':
                xbmcgui.Dialog().ok('Грешка 107','Внимание! Приложението може да се използва спрямо активните Ви абонаменти. Вече използвате приложението с максимално допустимите устройства. Телефон 0700 319 19 - Булсатком')

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
        if __Addon.getSetting('ext_epg') == 'true':
         template = '#EXTINF:-1 radio="%s" tvg-id="%s" tvg-logo="%s" tvg-name="%s" group-title="%s",%s\n%s\n'
         data = '#EXTM3U\n'
         for video in jsonrsp:
          name = video['title'].encode('utf-8', 'ignore')
          genre = video['genre'].encode('utf-8', 'ignore')
          epg = video['epg_name'].encode('utf-8', 'ignore')
          epg = epg.replace("24_kitchen","24kitchen")
          epg = epg.replace("axn","AXN")
          epg = epg.replace("axn_black","AXNBlack")
          epg = epg.replace("AXN_black","AXNBlack")
          epg = epg.replace("axn_white","AXNWhite")
          epg = epg.replace("AXN_white","AXNWhite")
          epg = epg.replace("agro_tv_hd","agroTV")
          epg = epg.replace("alfa","Alfa")
          epg = epg.replace("animal_planet","AnimalPlanet")
          epg = epg.replace("ams_hd","AutoMotorSport")
          epg = epg.replace("actionplus_hd","ActionPlus")
          epg = epg.replace("bntworld","BNTWorld")
          epg = epg.replace("bnt1_hd","BNT1")
          epg = epg.replace("bnt2","BNT2")
          epg = epg.replace("bnt_hd","BNTHD")
          epg = epg.replace("bulgaria_on_air","BulgariaOnAir")
          epg = epg.replace("bloomberg_tv","Bloomberg")
          epg = epg.replace("box_tv_hd","BoxTV")
          epg = epg.replace("bTV","bTV")
          epg = epg.replace("bTV_action","bTVAction")
          epg = epg.replace("bTV_comedy","bTVComedy")
          epg = epg.replace("bTV_cinema","bTVCinema")
          epg = epg.replace("bTV_lady","bTVLady")
          epg = epg.replace("boomerang","Boomerang")
          epg = epg.replace("bg_music_channel_hd","BGMusicChannel")
          epg = epg.replace("babytv","BabyTV")
          epg = epg.replace("bit","BiT")
          epg = epg.replace("balkanica_hd","Balkanika")
          epg = epg.replace("bul_hist_hd","BulHistory")
          epg = epg.replace("bulgaria24","Bulgaria24")
          epg = epg.replace("hristobotev","BNRHristoBotev")
          epg = epg.replace("horizont","BNRHorizont")
          epg = epg.replace("bgradio","BGRadio")
          epg = epg.replace("cn","CartoonNetwork")
          epg = epg.replace("city_tv","City")
          epg = epg.replace("cinemax_hd","Cinemax")
          epg = epg.replace("cinemax_2_hd","Cinemax2")
          epg = epg.replace("cnn","CNN")
          epg = epg.replace("CartoonNetworkn","CNN")
          epg = epg.replace("cherno_more","ChernoMore")
          epg = epg.replace("cbs_reality","CBSReality")
          epg = epg.replace("crime_invest_network","CI")
          epg = epg.replace("comedy_central","ComedyCentral")
          epg = epg.replace("comedyplus_hd","ComedyPlus")
          epg = epg.replace("cinemaplus_hd","CinemaPlus")
          epg = epg.replace("diema","Diema")
          epg = epg.replace("diema_family","DiemaFamily")
          epg = epg.replace("Diema_family","DiemaFamily")
          epg = epg.replace("diemasporthd","DiemaSport")
          epg = epg.replace("Diemasporthd","DiemaSport")
          epg = epg.replace("diemasport2hd","DiemaSport2")
          epg = epg.replace("Diemasport2hd","DiemaSport2")
          epg = epg.replace("discovery_hd","DiscoveryHDShowcase")
          epg = epg.replace("Discovery_hd","DiscoveryHDShowcase")
          epg = epg.replace("discovery","Discovery")
          epg = epg.replace("discovery_science","DiscoveryScience")
          epg = epg.replace("Discovery_science","DiscoveryScience")
          epg = epg.replace("disney_channel","Disney")
          epg = epg.replace("disney_junior","DisneyJunior")
          epg = epg.replace("docubox","DocuBox")
          epg = epg.replace("da_vinci_learning","DaVinciLearning")
          epg = epg.replace("dstv","DSTV")
          epg = epg.replace("dm_sat","DMSat")
          epg = epg.replace("destination_bg_hd","DestinationBG")
          epg = epg.replace("darik","DarikRadioTV")
          epg = epg.replace("evrokom","Eurocom")
          epg = epg.replace("tvevropa","tveurope")
          epg = epg.replace("ekids","Ekids")
          epg = epg.replace("eurosport","Eurosport1")
          epg = epg.replace("eurosport2","Eurosport2")
          epg = epg.replace('Eurosport12','Eurosport2')
          epg = epg.replace("folklor_tv_hd","FolklorTV")
          epg = epg.replace("fan_tv_hd","FENTV")
          epg = epg.replace("fen_folk_tv","FenFolk")
          epg = epg.replace("fox","FOX")
          epg = epg.replace("fox_life","FOXLife")
          epg = epg.replace("FOX_life","FOXLife")
          epg = epg.replace("fox_crime","FOXCrime")
          epg = epg.replace("FOX_crime","FOXCrime")
          epg = epg.replace("fine_living","FineLiving")
          epg = epg.replace("filmplus_hd","FilmPlus")
          epg = epg.replace("filmplus","FPlus")
          epg = epg.replace("fashion_tv","FashionTV")
          epg = epg.replace("food_network_hd","FoodNetworkHD")
          epg = epg.replace("filmbox_hd","FilmBoXtraHD")
          epg = epg.replace("fightbox","FightBox")
          epg = epg.replace("fm_plus","FMPlus")
          epg = epg.replace("fresh","RadioFresh")
          epg = epg.replace("history_channel_hd","History")
          epg = epg.replace("history2","H2")
          epg = epg.replace("hobbytv","HobbyTV")
          epg = epg.replace("hobby_tv_hd","HobbyTVHD")
          epg = epg.replace("hobby_lov_hd","HobbyLovHD")
          epg = epg.replace("hbo","HBOHD")
          epg = epg.replace("hbo_comedy","HBOComedy")
          epg = epg.replace("HBOHD_comedy","HBOComedy")
          epg = epg.replace("hbo3_hd","HBO3")
          epg = epg.replace("HBOHD3_hd","HBO3")
          epg = epg.replace("hustler","HustlerTV")
          epg = epg.replace("hit_tv","HitMix")
          epg = epg.replace("hmtv_hd","HMTV")
          epg = epg.replace("id_xtra","IDXtra")
          epg = epg.replace("in_life_hd","InLife")
          epg = epg.replace("jim_jam","JimJam")
          epg = epg.replace("kanal_3","Kanal3")
          epg = epg.replace("kinonova","KinoNova")
          epg = epg.replace("magic_tv","MagicTV")
          epg = epg.replace("mtv_rock","MTVRocks")
          epg = epg.replace("mtv_hits","MTVHits")
          epg = epg.replace("avto_moto_bg_hd","MotoSportHD")
          epg = epg.replace("mtvlivehd","MTVLiveHD")
          epg = epg.replace("mmtv","MMTV")
          epg = epg.replace("mtel_sport_1","MtelSport1")
          epg = epg.replace("mtel_sport_2","MtelSport2")
          epg = epg.replace("magic_fm","MagicFM")
          epg = epg.replace("novatv","Nova")
          epg = epg.replace("novasporthd","NovaSport")
          epg = epg.replace("nat_geo_hd","NatGeo")
          epg = epg.replace("nat_geo_wild","NatGeoWild")
          epg = epg.replace("nick_jr","NickJr")
          epg = epg.replace("nickelodeon","Nickelodeon")
          epg = epg.replace("outdor_hd","Outdoor")
          epg = epg.replace("ot_blizo__hd","OtBlizoHD")
          epg = epg.replace("perviy_kanal","PerviyKanal")
          epg = epg.replace("planeta_folk","PlanetaFolk")
          epg = epg.replace("planetatv","Planeta")
          epg = epg.replace("planetahd","PlanetaHD")
          epg = epg.replace("po_tv_trakia","Trakiq")
          epg = epg.replace("ringbg","RING")
          epg = epg.replace("ohota_riba","Ribalka")
          epg = epg.replace("skat","Skat")
          epg = epg.replace("filmplushd","SportPlusHD")
          epg = epg.replace("sportaltv","SportalBG")
          epg = epg.replace("stara_zagora_tv","TVSTZ")
          epg = epg.replace("the_voice","TheVoice")
          epg = epg.replace("tv1_hd","TV1")
          epg = epg.replace("travel_tv","Travel")
          epg = epg.replace("travel_tv_hd","thisisbg")
          epg = epg.replace("Travel_tv_hd","thisisbg")
          epg = epg.replace("tvt","TVT")
          epg = epg.replace("tiankov_folk_hd","TiankovFolk")
          epg = epg.replace("trace_sport_stars_hd","TraceSportStars")
          epg = epg.replace("tvplus","TVPlus")
          epg = epg.replace("travel_channel","TravelChannel")
          epg = epg.replace("tv1000","TV1000")
          epg = epg.replace("viasat_explorer","ViasatExplorer")
          epg = epg.replace("viasat_history","ViasatHistory")
          epg = epg.replace("viasat_nature","ViasatNature")
          epg = epg.replace("vh1","VH1")
          epg = epg.replace("vh1_classic","VH1Classic")
          epg = epg.replace("VH1_classic","VH1Classic")
          epg = epg.replace("wness_tv","wness")
          epg = epg.replace("zrock","ZRock")
          epg = epg.replace("dw","DeutscheWelle")
          epg = epg.replace("russia_today","RussiaToday")
          epg = epg.replace("360tunebox","360TuneBoxHD")
          radio = str(video['radio'])
          source = video['sources'].encode('utf-8', 'ignore')+'|User-Agent='+urllib.quote_plus(UA)
          logo = video['logo'].encode('utf-8', 'ignore')
          data += template % (radio, epg, logo, epg, genre, name, source)
         f.write(data)
         f.close()
        else:
         __Addon.getSetting('ext_epg') == 'false'
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
