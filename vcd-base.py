#!/bin/python3
import sys
from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
import requests
from lxml import etree, objectify

# Collect arguments.
if len(sys.argv) != 6:
        print("Usage: python3 {0} host org user password vdc".format(sys.argv[0]))
        sys.exit(1)
host = sys.argv[1]
org = sys.argv[2]
user = sys.argv[3]
password = sys.argv[4]
vdc = sys.argv[5]

# Disable warnings from self-signed certificates.
requests.packages.urllib3.disable_warnings()

# Login. SSL certificate verification is turned off to allow self-signed
# certificates.  You should only do this in trusted environments.
print("Logging in: host={0}, org={1}, user={2}".format(
        host, org, user))
client = Client(host,
                api_version='29.0',
                verify_ssl_certs=False,
                log_file='pyvcloud.log',
                log_requests=True,
                log_headers=True,
                log_bodies=True)
client.set_credentials(BasicLoginCredentials(user, org, password))

print("Fetching Org...")
org_resource = client.get_org()
org = Org(client, resource=org_resource)

print("Fetching VDC...")
vdc_resource = org.get_vdc(vdc)
vdc = VDC(client, resource=vdc_resource)
print("Fetching vApps....")
vapps = vdc.list_resources(EntityType.VAPP)
for vapp in vapps:
        vapp_resource = vdc.get_vapp(vapp['name'])
        tarvapp = VApp(client, resource=vapp_resource)
        sets = tarvapp.get_access_settings()
        sets = etree.tostring(sets, pretty_print=True)
        print(sets)
# Log out.
print("Logging out")
client.logout()
