import json
import requests
from optparse import OptionParser, Option, OptionValueError
import time
import re
import os


#Airtable authentication class taken from https://airtable-python-wrapper.readthedocs.io/en/master/authentication.html
class AirtableAuth(requests.auth.AuthBase):
    def __init__(self, api_key=None):
        try:
            self.api_key = api_key or os.environ["AIRTABLE_API_KEY"]
        except KeyError:
            raise KeyError(
                "Api Key not found. Pass api_key as a kwarg \
                            or set an env var AIRTABLE_API_KEY with your key")
    def __call__(self, request):
        auth_token = {"Authorization": "Bearer {}".format(self.api_key)}
        request.headers.update(auth_token)
        return request

def fetch_table_records(base_id,table,auth):
	
	records={}
	offset=''
	while True:
		table = 'Texts'
	
		url = 'https://api.airtable.com/v0/%s/%s' %(base_id,table)
	
		params={'offset':offset}
	
		response = requests.get(url,auth=auth,params=params)
	
		results = json.loads(response.text)
	
		new_records=results['records']
		
		for rec in new_records:
			records[rec['id']]=rec
	
		print(len(records))
	
		try:
			offset=results['offset']
		except:
			break

	return records



d = open('airtablekeys.json','r')
t = d.read()
d.close()
j = json.loads(t)

auth = AirtableAuth(j['api_key'])
base_id=j['base_id']

texts=fetch_table_records(base_id,'Texts',auth)
#print(texts)

id_dict={}

sources={}

#targets={}

for id in texts:
	text=texts[id]['fields']
	#print(text.keys())
	if 'Reference' in text.keys():
		refs=text['Reference']
		for ref in refs:
			sources[ref]=id

		
nodes=[]

links=[]

for id in texts:
	text=texts[id]['fields']
	if 'Referenced' in text.keys():
		refs=text['Referenced']
		
		try:
			year=text['Year']
		except:
			year=None
		
		nodes.append({"node":id,"name":text['Title'],"year":year})
		
		text_sources={}
		for ref in refs:
			source_id=sources[ref]
			print(ref)
			
			try:
				text_sources[source_id]+=1
			except:
				text_sources[source_id]=1
		for source_id in text_sources:
			links.append({"source":source_id,"target":id,"value":text_sources[source_id]})
		
	else:
		nodes.append({"node":id,"name":text['Title'],"year":year})









threshold=8

links = [i for i in links if i['value'] >= threshold]

linkednodes=[]
for link in links:
	linkednodes.append(link['source'])
	linkednodes.append(link['target'])
linkednodes=list(set(linkednodes))

nodes=[i for i in nodes if i['node'] in linkednodes]


nodeslist=[i["node"] for i in nodes]

for node in nodes:
	id=node["node"]
	node["node"]=nodeslist.index(id)

for link in links:
	source_id=link["source"]
	link["source"]=nodeslist.index(source_id)
	target_id=link["target"]
	link["target"]=nodeslist.index(target_id)

print(nodes)
print(links)

d=open('test.json','w')
d.write(json.dumps({"nodes":nodes,"links":links}))
d.close()








'''#work backwards, easier to aggregate this way
#level 3
for text in texts:
	author=text['Author']
	title=text['Title']
	id=text['id']
	if author!='Michel Foucault':
		referenced=text['Referenced']
		#make the node for this cited text
		nodes[id]=title
		#then add the author node if it doesn't already exist
		if author not in nodes.keys():
			nodes[author]=author
		#make author-to-text link
		links[author][title]=len(referenced)
	else:
		for reference in text['Reference']:
			
			nodes[id]=title
			
			linked_author=id_dict[reference]['Author']
			
			try:
				try:
					links[title][linked_author]+=1
				except:
					links[title][author]=1
			except:
				links[title]={author:1}

jnodes=[]
for node in nodes:
	jnodes.append({"node":node,"name":nodes[node]})

jlinks=[]
for source in links:
	for target in source:
		jlinks.append({"source":source,"target":target,"value":links[source][target]})

print(jnodes)
print(jlinks)'''
	