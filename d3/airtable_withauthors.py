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

for threshold in range(6,9):
	nodes=[]

	links=[]

	for id in texts:
		text=texts[id]['fields']
		if 'Referenced' in text.keys():
			refs=text['Referenced']
			if len(refs)>=threshold:
				try:
					year=text['Year']
				except:
					year=0
				author=text['Author']
				nodes.append({"node":id,"name":text['Title'],"year":year,"author":author})
		
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
		
		elif 'Reference' in text.keys():
			try:
				year=text['Year']
			except:
				year=None
			nodes.append({"node":id,"name":text['Title'],"year":year,"author":"Michel Foucault"})


	#now interject authors
	authors = list(set([i['author'] for i in nodes if i['author']!='Michel Foucault']))
	#print(authors)
	authorlinks={i:{"sources":{},"targets":{}} for i in authors}

	for node in nodes:
		author=node['author']
		id=node['node']
		if author!='Michel Foucault':
			for link in links:
				#print(author)
				source=link['source']
				target=link['target']
				value=link['value']
				if target==id:
					if source in authorlinks[author]['sources']:
						authorlinks[author]['sources'][source]+=value
					else:
						authorlinks[author]['sources'][source]=value
					if target in authorlinks[author]['targets']:
						authorlinks[author]['targets'][target]+=value
					else:
						authorlinks[author]['targets'][target]=value


	for author in authors:
		nodes.append({"node":author,"name":author,"author":author,"year":0})


	links=[]

	for author in authorlinks:
		for source in authorlinks[author]['sources']:
			links.append({"source":source,"target":author,"value":authorlinks[author]['sources'][source]})
		for target in authorlinks[author]['targets']:
			links.append({"target":target,"source":author,"value":authorlinks[author]['targets'][target]})

	#remove orphan nodes

	linkednodes=[]
	for link in links:
		linkednodes.append(link['source'])
		linkednodes.append(link['target'])
	linkednodes=list(set(linkednodes))

	nodes=[i for i in nodes if i['node'] in linkednodes]


	nodes=sorted(nodes,key=lambda x: (x['author'],x['year']))
	
	nodeslist=[i["node"] for i in nodes]
	
	for node in nodes:
		id=node["node"]
		newid=nodeslist.index(id)
		node["node"]=newid
		node["id"]=newid

	for link in links:
		source_id=link["source"]
		link["source"]=nodeslist.index(source_id)
		target_id=link["target"]
		link["target"]=nodeslist.index(target_id)
		link["id"]=nodeslist.index(source_id)

	print("nodes count",len(nodes))
	print("links count",len(links))

	d=open('threshold_%d.json' %threshold,'w')
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
	
