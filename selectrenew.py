#!/usr/bin/python3
import requests
import base64
import threading
import datetime
from xml.etree import ElementTree

fileconfig = open('defsecrenew.conf','r')
user = fileconfig.readline().replace('\n','')
passwd = fileconfig.readline().replace('\n','')
host = fileconfig.readline().replace('\n','')
org = fileconfig.readline().replace('\n','')
log_ip = fileconfig.readline().replace('\n','')

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
        resp = requests.get(url=api+'/vApps/query?page='+str(counter),headers=headers)
        if('BAD_REQUEST' in resp.text):
            end = False
            break
        t = threading.Thread(target=grab_renew, args = (resp,))
        t.start()
        counter = counter +1
def grab_renew(resp):
    xml_content = resp.text                                                                                                                                                                                
    root = ElementTree.fromstring(xml_content)
    for child in root:
        if('name' in child.attrib):
            if 'CCDC_Practice' in child.attrib['name']:
                t = threading.Thread(target=request_renew, args = (child,))
                t.start()

def request_renew(child):
    try:
        child_id = child.attrib['href'].replace('https://vcloud.ialab.us/api/vApp/','')
        resp = requests.get(url=api+'/vApp/'+child_id+'/leaseSettingsSection',headers=headers)
        resp = requests.put(url=api+'/vApp/'+child_id+'/leaseSettingsSection',headers=headers,data=resp.text)
        print(child.attrib['name'],"Renewed")
        requests.post(url=log_ip,verify=False,data={'defsecpractice':str(child.attrib['name'])+" renewed at "+str(datetime.datetime.now())})
    except:
        requests.post(url=log_ip,verify=False,data={'defsecpractice':str(child.attrib['name'])+" renewed at "+str(datetime.datetime.now())})

if __name__ == '__main__':
    set_auth_token()
    renew()
