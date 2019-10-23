import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import argparse
import sys

pubmedID = re.compile("PMID:\s(\d+).")
#HTMLabstract = re.compile('<h3>Abstract</h3><div class=""><p>([\w\d\s.,;<="-:>]+)</p>')
#HTMLabstract = re.compile('<h3>Abstract</h3><div class="">(.+)</div><div class="keywords">')
HTMLabstract = re.compile('<h3>Abstract</h3><div class="">(.+)</p><p class="copyright">Copyright')
#HTMLtitle = re.compile('</div><h1>([\w\d\s.,;<="-:>]+)</h1>')
HTMLtitle = re.compile('</div><h1>(.+)</h1>')

def parseArg():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-i', '--InpFil', required=True, type=str,
	                    help='Txt file contains search results from Pubmed')
	parser.add_argument('-o', '--OutFil', required=True, type=str,
	                    help='Txt file contains search results from Pubmed')
	args = parser.parse_args()
	return args 

class GetPubmed(object):
	"""docstring for GetPubmed"""
	def __init__(self, args):
		self.InpFil = args.InpFil
		self.OutFil = args.OutFil
		
	def run(self):
		SearchResFil = open(self.InpFil, "rt")
		SaveFil = open(self.OutFil, "wt")
		Counter = 0
		for l in SearchResFil:
			pubmed_id = pubmedID.search(l)
			if pubmed_id != None:
				#print(pubmed_id.group(1))
				Counter += 1
				Title, Abstract = self.GrabAbstract(pubmed_id.group(1))
				if Title != None:
					SaveFil.write("<PubMedID>%s<Title>%s\n"%(pubmed_id.group(1), Title))
					SaveFil.write("<Abstract>%s\n"%(Abstract))

			#break
		#print(Counter)

	def GrabAbstract(self, pubmed_id):
		url = "https://www.ncbi.nlm.nih.gov/pubmed/%s"%(pubmed_id)
		print(pubmed_id)
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


def main():
	args = parseArg()
	ins = GetPubmed(args) 
	ins.run()

if __name__ == '__main__':
	main()