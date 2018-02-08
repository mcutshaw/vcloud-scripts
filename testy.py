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
    resp = requests.get(url=api+'/api/query', headers=headers)
    xml_content = resp.text
    root = ElementTree.fromstring(xml_content)
    for child in root:
        if('name' in child.attrib):
            catid = child.attrib['href'].replace(api+'/catalog/','')
            resp = requests.get(url=api+'/catalog/'+catid,headers=headers)
            xml_content = resp.text
            cat_root = ElementTree.fromstring(xml_content)
            for cat_child in cat_root:
                if cat_child.tag.split('}')[1] == 'CatalogItems':
                    for vapp_child in cat_child:
                        vapp_name = vapp_child.attrib['name']
                        if 'DefSec' in vapp_name:
                            print(vapp_child.tag)
                            vapp_id = vapp_child.attrib['id']
                            resp = requests.get(url=api+'/catalogItem/'+vapp_id,headers=headers)
                            print(resp.text)
                            
def renew():
    for x in range(1,5):
        resp = requests.get(url=api+'/vAppTemplates/query?page='+str(x),headers=headers)
        xml_content = resp.text
        root = ElementTree.fromstring(xml_content)
        for child in root:
            if('name' in child.attrib):
                if 'Def' in child.attrib['name']:
                    print(child.attrib['name'])
                    child_id = child.attrib['href'].replace('https://vcloud.ialab.us/api/vAppTemplate/','')
                    #print(child_id)
                    resp = requests.get(url=api+'/vAppTemplate/'+child_id+'/leaseSettingsSection',headers=headers)
                    print(resp.text)
                    resp = requests.put(url=api+'/vAppTemplate/'+child_id+'/leaseSettingsSection',headers=headers,data=resp.text.replace('7776000','77776000'))
                    print(resp.text)
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
    renew()
#    vapps = get_vapps()
#    print(vapps)
