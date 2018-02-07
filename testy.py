#!/usr/bin/python3
import requests
import base64
from xml.etree import ElementTree
import urllib
import subprocess

fileconfig = open('testy.conf','r')
user = fileconfig.readline().replace('\n','')
passwd = fileconfig.readline().replace('\n','')
host = fileconfig.readline().replace('\n','')
org = fileconfig.readline().replace('\n','')

api='https://%s/api' % host
session_url='%s/sessions' % api
query_url='%s/query' % api

headers={'Accept': 'application/*+xml;version=1.5'}

def set_auth_token():
    auth_str = '%s@%s:%s' % (user, org, passwd)
    auth=base64.b64encode(auth_str.encode()).decode('utf-8')
    headers['Authorization'] = 'Basic %s' % auth
    resp = requests.post(url=session_url, headers=headers)
    del headers['Authorization']
    headers['x-vcloud-authorization'] = resp.headers['x-vcloud-authorization']

def get_org():
    resp = requests.get(url=api+'/catalogs/query', headers=headers)
#    print(resp.text)
    resp = requests.get(url=api+'/vApps/query', headers=headers)
    xml_content = resp.text
#    print(resp.text)

    root = ElementTree.fromstring(xml_content)
    vapps = {}
''' 
    for child in root:
        if 'name' in child.attrib:
            print(child.attrib)
            vmid = child.attrib['href'].replace('https://vcloud.ialab.us/api/vApp/','')
            print(vmid)
            print(requests.delete(url=api+'/vApp/'+vmid, headers=headers))
        if 'VMRecord' in child.tag:
            attrs = child.attrib
            cont = attrs['containerName']
            if cont not in vapps:
                vapps[cont] = {}
            vapps[cont][attrs['name']] = attrs['href']
            '''
 


def get_vapps():
    query_str = 'type=vm&filter=status==POWERED_ON' #&fields=name,containerName'
    print(query_str)
    url = '%s?%s' % (query_url, query_str)
    resp = requests.get(url=url, headers=headers)
    xml_content = resp.text
    print(xml_content)
    root = ElementTree.fromstring(xml_content)
    vapps = {}
    for child in root:
        if 'VMRecord' in child.tag:
            attrs = child.attrib
            cont = attrs['containerName']
            if cont not in vapps:
                vapps[cont] = {}
            vapps[cont][attrs['name']] = attrs['href']
    return vapps

def get_ticket(vm_url):
    url = '%s/screen/action/acquireTicket' % vm_url
    resp = requests.post(url=url, headers=headers)
    root = ElementTree.fromstring(resp.text)
    mks_url = urllib.parse.unquote(root.text)
    return mks_url

if __name__ == '__main__':
    set_auth_token()
    get_org()
#    vapps = get_vapps()
#    print(vapps)
