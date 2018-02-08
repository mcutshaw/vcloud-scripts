#!/usr/bin/python3
import requests
import base64
from xml.etree import ElementTree

fileconfig = open('defsecrenew.conf','r')
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

def renew():
    end = True
    counter = 1
    while end:
        resp = requests.get(url=api+'/vAppTemplates/query?page='+str(counter),headers=headers)
        if('BAD_REQUEST' in resp.text):
            end = False
        xml_content = resp.text
        root = ElementTree.fromstring(xml_content)
        for child in root:
            if('name' in child.attrib):
                if 'Def' in child.attrib['name']:
                    print(child.attrib['name'],end=': ')
                    child_id = child.attrib['href'].replace('https://vcloud.ialab.us/api/vAppTemplate/','')
                    resp = requests.get(url=api+'/vAppTemplate/'+child_id+'/leaseSettingsSection',headers=headers)
                    resp = requests.put(url=api+'/vAppTemplate/'+child_id+'/leaseSettingsSection',headers=headers,data=resp.text)
                    print("Renewed")
        counter = counter +1

if __name__ == '__main__':
    set_auth_token()
    renew()
    print("End")
