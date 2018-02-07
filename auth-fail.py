#!/usr/bin/python3
# Adapted from: https://www.virtuallyghetto.com/2012/02/how-to-access-vcloud-director-remote.html
import requests
import base64
from xml.etree import ElementTree
import urllib
import subprocess

user=''
passwd=''
host='vcloud.ialab.us'
org='projects'

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

def get_vapps():
    query_str = 'type=vm&filter=status==POWERED_ON'#&fields=name,containerName'
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
    vapps = get_vapps()
    vm_url = vapps['ESXi_Practice']['Ubuntu']
    mks_url = get_ticket(vm_url)
    ticket = mks_url.split('ticket')[1].split('--')[0][1:]
    thumbprint = mks_url.split('--')[1][3:]
    vmrc_host = mks_url.split('/')[2]
    vmrc_host = '138.247.115.251'
    wss = 'wss://vcloud-proxy.ialab.us:443/'
    print(ticket)
    print(thumbprint)
    print(vmrc_host)
    path='/vmfs/volumes/5368517c-b140d954-c94f-2c768a53cb38/Ubuntu (426121de-180b-40cb-8511-5ddeff7859ad)/Ubuntu (426121de-180b-40cb-8511-5ddeff7859ad).vmx'
#    vmrc_url = 'vmrc://%s:443/?mksticket=%s&thumbprint=%s&path=%s&websocket=%s'
#    vmrc_url = vmrc_url % (vmrc_host, ticket, thumbprint, path, wss)
    vmrc_url = 'vmrc://%s/?thumbprint=%s&websocket=%sticket/%s'
    vmrc_url = vmrc_url % (vmrc_host, thumbprint, wss, ticket)
    print(vmrc_url)
    subprocess.call('vmrc "%s"' % vmrc_url, shell=True)
