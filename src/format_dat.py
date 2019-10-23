import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import argparse
import sys
import csv
import random
import numpy as np
import string
import pickle
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
nltk.download('punkt')

def parseArg():
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-i', '--InpFil', required=True, type=str,
	                    help='Txt file contains search results from Pubmed')
	parser.add_argument('-o', '--outname', default="train.npy", type=str,
	                    help='Txt file contains search results from Pubmed')
	args = parser.parse_args()
	return args 

class GetPubmed(object):
	"""docstring for GetPubmed"""
	def __init__(self, args, trainP=0.7):
		self.InpFil = args.InpFil
		self.outname = args.outname
		self.trainFil = "%s_train.npy"%self.outname
		self.testFil = "%s_test.npy"%self.outname
		self.trainLabel = "%s_train.labels"%self.outname
		self.testLabel = "%s_test.labels"%self.outname
		self.DictFil = "%s_dict.pkl"%self.outname
		self.pkl = {}
		self.trainP = trainP
		self.key_level = 0
		self.word2key = {"cold":1, " ":0}
		self.key2word = {1:"cold", 0:" "}
		self.TrainArray = []
		self.TestArray = []
		self.TrainLabels = []
		self.TestLabels = [] 

	def run(self):
		InpFil = open(self.InpFil, "rt")
		SaveFil = open(self.DictFil, "wt")
		Counter = 0
		reader = csv.reader(InpFil)
		for row in reader:
			if len(row) < 3 or row[0].startswith("@"):
				#print(row)
				continue
			self.processAbstract(row[1].lower(), row[2])

			#break
		#print(Counter)
		output = open(self.DictFil, 'wb')
		pickle.dump(self.word2key, output)
		output.close()
		
		tmp = np.empty(len(self.TrainArray),object)
		tmp[:] = self.TrainArray
		np.save(self.trainFil, tmp)
		tmp = np.empty(len(self.TestArray),object)
		tmp[:] = self.TestArray
		np.save(self.testFil, tmp)
		#np.save(self.trainFil, np.array(self.TrainArray, dtype='object'))
		#np.save(self.testFil, np.array(self.TestArray, dtype='object'))

		output = open(self.trainLabel, 'wt')
		output.write("\n".join(self.TrainLabels))
		output.close()
		output = open(self.testLabel, 'wt')
		output.write("\n".join(self.TestLabels))
		output.close()



	def processAbstract(self, abstract, label):
		abstract = abstract.replace("-", " ")
		abstract = abstract.translate(str.maketrans('', '', string.punctuation))
		abstract = abstract.replace("colds", "cold")
		#abstract = abstract.split()
		#print(abstract)
		#abstract = re.split('-;, ',abstract)
		#print(abstract)

		stop_words = set(stopwords.words('english')) 
		  
		word_tokens = word_tokenize(abstract) 
		  
		filtered_sentence = [w for w in word_tokens if not w in stop_words] 
		  
		filtered_sentence = [] 
		  
		for w in word_tokens: 
		    if w not in stop_words: 
		        filtered_sentence.append(w) 
		  
		#print(word_tokens) 
		#print(filtered_sentence) 
		abstract = filtered_sentence

		try:
			#idx = abstract.index("<e>cold</e>")
			idx = abstract.index("ecolde")
		except:
			print("Error", abstract)
			#exit()
			return
		#print(idx)
		words = abstract#.split()
		word_array = []
		test_words = []
		for i in range(idx-10,idx+10):
			if i < 0 or i > len(words)-1:
				word_array.append(0)
				continue
			#print(i, len(words))
			try:
				word = words[i]
			except:
				print(words, i)
			if word == "ecolde":
				word = 'cold'
			elif word == "ecoldse":
				word = 'colds'
			else:
				word = word.translate(str.maketrans('', '', string.punctuation))
			if word not in self.word2key:
				self.key_level += 1
				self.word2key[word] = self.key_level
				self.key2word[self.key_level] = word
			key = self.word2key[word]
			word_array.append(key)
			test_words.append(word)
		print(test_words)
		word_array = np.array(word_array, dtype='float64')
		if random.random() < self.trainP:
			#outfil = self.testFil
			self.TrainArray.append(word_array)
			self.TrainLabels.append(label)
		else:
			#outfil = self.trainFil
			self.TestArray.append(word_array)
			self.TestLabels.append(label)		

	#def generatewordvector(self)
 
def main():
	args = parseArg()
	ins = GetPubmed(args) 
	ins.run()

if __name__ == '__main__':
	main()