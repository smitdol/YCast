# -*- coding: utf-8 -*-
import logging
import xml.etree.ElementTree as ET

XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'


def get_init_token():
    return '<EncryptedToken>0000000000000000</EncryptedToken>'


def strip_https(url):
    if url.startswith('https://'):
        url = 'http://' + url[8:]
    return url


def add_bogus_parameter(url):
    """
    We need this bogus parameter because some (if not all) AVRs blindly append additional request parameters
    with an ampersand. E.g.: '&mac=<REDACTED>&dlang=eng&fver=1.2&startitems=1&enditems=100'.
    The original vTuner API hacks around that by adding a specific parameter or a bogus parameter like '?empty=' to
    the target URL.
    """
    return url +'?empty='


class Page:
    def __init__(self):
        self.items = []
        self.count = -1
        self.dontcache = False

    def add(self, item):
        self.items.append(item)

    def set_count(self, count):
        self.count = count

    def to_xml(self):
        xml = ET.Element('ListOfItems')
        ET.SubElement(xml, 'ItemCount').text = str(self.count)
        if self.dontcache:
            ET.SubElement(xml, 'NoDataCache').text = 'Yes'
        for item in self.items:
            xml.append(item.to_xml())
        return xml

    def to_string(self):
#        s = XML_HEADER + ET.tostring(self.to_xml(),encoding='us-ascii').decode('us-ascii') #.decode('utf-8')
        s = XML_HEADER + ET.tostring(self.to_xml(),encoding='utf-8').decode('utf-8') #.decode('utf-8')
        t = s.replace("><",">\r\n<") #.replace("&amp;","&")
        logging.debug(t)
        return t


class Previous:
    def __init__(self, url):
        self.url = url

    def to_xml(self):
        item = ET.Element('Item')
        ET.SubElement(item, 'ItemType').text = 'Previous'
        ET.SubElement(item, 'UrlPrevious').text = add_bogus_parameter(self.url)
        ET.SubElement(item, 'UrlPreviousBackUp').text = add_bogus_parameter(self.url)
        return item


class Display:
    def __init__(self, text):
        self.text = text

    def to_xml(self):
        item = ET.Element('Item')
        ET.SubElement(item, 'ItemType').text = 'Display'
        ET.SubElement(item, 'Display').text = self.text
        return item


class Search:
    def __init__(self, caption, url):
        self.caption = caption
        self.url = url

    def to_xml(self):
        item = ET.Element('Item')
        ET.SubElement(item, 'ItemType').text = 'Search'
        ET.SubElement(item, 'SearchURL').text = add_bogus_parameter(self.url)
        ET.SubElement(item, 'SearchURLBackUp').text = add_bogus_parameter(self.url)
        ET.SubElement(item, 'SearchCaption').text = self.caption
        ET.SubElement(item, 'SearchTextbox').text = None
        ET.SubElement(item, 'SearchButtonGo').text = "Search"
        ET.SubElement(item, 'SearchButtonCancel').text = "Cancel"
        return item


class Directory:
    def __init__(self, title, destination, item_count=-1):
        self.title = title
        self.destination = destination
        self.item_count = item_count

    def to_xml(self):
        item = ET.Element('Item')
        ET.SubElement(item, 'ItemType').text = 'Dir'
        ET.SubElement(item, 'Title').text = " "+self.title
        ET.SubElement(item, 'UrlDir').text = add_bogus_parameter(self.destination)
        ET.SubElement(item, 'UrlDirBackUp').text = add_bogus_parameter(self.destination)
#        ET.SubElement(item, 'DirCount').text = str(self.item_count)
        return item

    def set_item_count(self, item_count):
        self.item_count = item_count


class Station:
    def __init__(self, id, name, description, url, icon, genre, location, mime, bitrate, bookmark, prefix):
        self.id = id
        self.name = name
        self.description = description
        self.url = strip_https(url)
        self.trackurl = None
        self.icon = icon
        self.genre = genre
        self.location = location
        self.mime = mime
        self.bitrate = bitrate
        self.bookmark = bookmark
        self.prefix = prefix

    def set_trackurl(self, url):
        self.trackurl = url

    def set_bookmark(self, url):
        self.bookmark = url

    def set_mac(self, mac):
        self.mac = mac

    def to_xml(self):
        item = ET.Element('Item')
        ET.SubElement(item, 'ItemType').text = 'Station'
        ET.SubElement(item, 'StationId').text = self.id
        ET.SubElement(item, 'StationName').text = self.name
        params = '?ex45v='+self.mac + '&id=' +self.id + '&p='+self.prefix 
        if self.trackurl:
            ET.SubElement(item, 'StationUrl').text = self.trackurl + params
        elif self.url:
            ET.SubElement(item, 'StationUrl').text = self.url + params
        if self.description:
            ET.SubElement(item, 'StationDesc').text = self.description
        else:
            ET.SubElement(item, 'StationDesc').text = self.name
#        if self.icon:
#            ET.SubElement(item, 'Logo').text = self.icon
#        ET.SubElement(item, 'Logo').text = 'http://logo.vtuner.net/007452/logo/logo-28875.jpg'
        if self.genre:
            ET.SubElement(item, 'StationFormat').text = self.genre
        else:
            ET.SubElement(item, 'StationFormat').text = 'Pop'
        if self.location:
            ET.SubElement(item, 'StationLocation').text = self.location
        else:
            ET.SubElement(item, 'StationLocation').text = 'Netherlands'
        if self.bitrate:
            ET.SubElement(item, 'StationBandWidth').text = str(self.bitrate)
        else:
            ET.SubElement(item, 'StationBandWidth').text = '96'
        if self.mime:
            ET.SubElement(item, 'StationMime').text = self.mime
        else:
            ET.SubElement(item, 'StationMime').text = 'MP3'
        ET.SubElement(item, 'Relia').text = '3'
        if self.bookmark:
            ET.SubElement(item, 'Bookmark').text = self.bookmark
        return item
