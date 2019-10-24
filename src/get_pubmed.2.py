import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import argparse
import sys
import math
from multiprocessing import Process
from Bio import Entrez
import json
import pprint
import time
import sys
pp = pprint.PrettyPrinter(indent=4)

pubmedID = re.compile("PMID:\s(\d+).")
HTMLabstract = re.compile('<h3>Abstract</h3><div class="">(.+)</p><p class="copyright">Copyright')
HTMLtitle = re.compile('</div><h1>(.+)</h1>')
MyEmail = "jw3514@cumc.columbia.edu"

def parseArg():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-i', '--InpFil', required=True, type=str,
	                    help='Txt file contains search results from Pubmed')
	parser.add_argument('-o', '--OutFil', required=True, type=str,
	                    help='Output Name')
	parser.add_argument('-t', '--threads', default=1, type=int,
	                    help='Threads')
	parser.add_argument('-b', '--batch', default=100, type=int,
	                    help='Threads')

	args = parser.parse_args()
	return args 

class GetPubmed(object):
	"""docstring for GetPubmed"""
	def __init__(self, args):
		self.InpFil = args.InpFil
		self.OutName = args.OutFil
		self.threads = args.threads
		self.batch_size = args.batch
		self.pubmedIDs = []
		
	def run(self):
		SearchResFil = open(self.InpFil, "rt")
		#SaveFil = open(self.OutFil, "wt")
		Counter = 0
		for l in SearchResFil:
			pubmed_id = pubmedID.search(l)
			if pubmed_id != None:
				self.pubmedIDs.append(pubmed_id.group(1))
		if self.threads == 1:
			self.process(self.pubmedIDs, "%s.Abs.txt"%(self.OutName))
		else:
			procs = []
			step = math.ceil(len(self.pubmedIDs)/self.threads)
			for i in range(self.threads):
				fname = "%s.%d.Abs.txt"%(self.OutName, i+1)
				if i < self.threads-1 :
					List = self.pubmedIDs[i*step:(i+1)*step]
				else:
					List = self.pubmedIDs[i*step:]
				p = Process(target=self.process, args=(List, fname))
				p.start()
				procs.append(p)
			[p.join() for p in procs]
		stderr.write("Done!")

	def process(self, pubmedIDList, outputFilename):
		OutFil = open(outputFilename, 'wt')
		FLAG_STOP = False
		while 1:
			try:
				if len(pubmedIDList) > self.batch_size:
					IDs = pubmedIDList[0:self.batch_size]
				else:
					IDs = pubmedIDList
					FLAG_STOP = True
				papers = self.fetch_details(IDs)
				for paper in papers["PubmedArticle"]:
					try:
						Title = paper["MedlineCitation"]["Article"]["ArticleTitle"]
						AbstractParts = paper["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]
						AbstractString = " ".join(AbstractParts)
						soup = BeautifulSoup(AbstractString, "lxml")
						AbstractString = soup.getText()
						#print(AbstractString)
						OutString = "%s|%s|%s\n"%(ID, Title, AbstractString)
						OutFil.write("%s|%s|%s\n"%(ID, Title, AbstractString))
						stdout.write(OutString)
					except:
						stderr.write("Cant find title or abstract: %s"%paper["MedlineCitation"]["PMID"])
				if FLAG_STOP:
					break
				pubmedIDList = pubmedIDList[self.batch_size:]
			except urllib.error.HTTPError:
				secs = 5
				stderr.write("waiting %d secs"%secs)
				time.sleep(secs)
			except:
				print("Unexpected error:", sys.exc_info()[0])

	def GrabAbstract(self, pubmed_id):
		url = "https://www.ncbi.nlm.nih.gov/pubmed/%s"%(pubmed_id)
		#print(pubmed_id)
		html = None
		for i in range(5): # try 5 times
			try:
				html = urllib.request.urlopen(url).read()
			except:
				continue
		if html == None:
			#sys.stderr.write("Can't Get article: "%pubmed_id)
			print("Can't Get article: "%pubmed_id)
			return None, None	
		buffer_ = []
		start_buffer = False
		html = str(html)
		html = html.split("\\n")
		for l in html:
			if "messagearea" in l:
				#print(l)
				start_buffer = True
			if start_buffer:
				buffer_.append(l)
			if "messagearea_bottom" in l:
				break
		#print(buffer_)
		buffer_ = "\n".join(buffer_)
		try:
			Title = HTMLtitle.search(buffer_).group(1)
			Abstract = HTMLabstract.search(buffer_).group(1)
			soup = BeautifulSoup(Abstract)
			return Title, soup.getText()
		except:
			print("Cant find Abstract or Title for %s"%pubmed_id)
			return None, None 

	def search(self, query):
		Entrez.email = "jw3514@cumc.columbia.edu"
		handle = Entrez.esearch(db='pubmed', sort='relevance', retmax='20',retmode='xml', term=query)
		results = Entrez.read(handle)
		return results
	
	def fetch_details(self, IDs):
		Entrez.email = MyEmail 
		IDs = ".".join(IDs)
		handle = Entrez.efetch(db='pubmed',retmode='xml',id=IDs)
		results = Entrez.read(handle)
		return results

def main():
	args = parseArg()
	ins = GetPubmed(args) 
	ins.run()

if __name__ == '__main__':
	main()
