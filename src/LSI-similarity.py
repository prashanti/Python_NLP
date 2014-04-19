import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
import math
import gensim
from collections import Counter
from stemming.porter2 import stem
import logging
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import numpy as np
from gensim import corpora, models, similarities
import sys
import scipy.stats
from random import choice
session1=[]
allsessions=[]
################### Creating a set of stopwords
stoplist=set()
for line in open('../TestData/stopwords.txt'):
	line=line.strip()
	stoplist.add(line.lower())
###################



def getkeywords():
	#See here for more info: http://radimrehurek.com/gensim/tut2.html
	count=1

	# to get topics list for all 100 topics 
	#lsi.print_topics(100)

	writetopic=open("TopicWords_"+str(notopics)+".txt",'w')
	for doc in corpus_lsi: 
		
		keywords=set()
		doc.sort(key=lambda tup: tup[1], reverse=True)
		#print "top1",doc[0][0] # this is the top topic for this document
		#print "top2",doc[1][0] # this is the next best topic for this document
		i=0
		
		count+=1
		while (i<4): #4 top topics
			topicscore=lsi.show_topic(doc[i][0], topn=4)
			# top two words from each topic

			keywords.add(stem2word[topicscore[0][1].strip()])
			keywords.add(stem2word[topicscore[1][1].strip()])
			keywords.add(stem2word[topicscore[2][1].strip()])
			keywords.add(stem2word[topicscore[3][1].strip()])
			i+=1

		for word in keywords:
			writetopic.write(word+",")
		writetopic.write("\n")
	

inputfile=str(sys.argv[1])
corpussize = sum(1 for line in open(inputfile))
notopics=str(sys.argv[2])

Scorematrix = [[0 for x in xrange(corpussize)] for x in xrange(corpussize)]




################### 
stem2word={}
for line in open(inputfile):
	for word in line.lower().split():
		stemmed=stem(word).strip()
		stem2word[stemmed]=word

dictionary = corpora.Dictionary([[stem(word) for word in line.lower().split()] for line in open(inputfile)])
stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
dictionary.filter_tokens(stop_ids + once_ids) 
dictionary.compactify() 
dictionary.save('./storeddictionary.dict') 


###################




###################### Corpus from a file

class MyCorpus(object):
	def __iter__(self):
		freq=Counter()
		for line in open(inputfile):
			words=line.lower().split()
			tmp=Counter()
			for word in words:
				word=stem(word).strip()
				if (tmp[word]!=1):
					freq[word] +=1
				tmp[word]=1


		for line in open(inputfile):
			# assume there's one document per line, tokens separated by whitespace
			newline=list()
			newline=[stem(word) for word in line.lower().split()]
			for word in newline:
				word=word.strip()
				if word in stoplist:
					newline = filter(lambda a: a != word, newline)
				if ((freq[word]==1) & (word not in stoplist)):
					newline = filter(lambda a: a != word, newline)
			yield dictionary.doc2bow(newline)

corpus_memory_friendly = MyCorpus() 
corpora.MmCorpus.serialize('./storedcorpus.mm', corpus_memory_friendly) 


	###################


	################### Load the stored dictionary and corpus

dictionary = corpora.Dictionary.load('./storeddictionary.dict')
corpus = corpora.MmCorpus('./storedcorpus.mm')

	###################


# Creating Models here
tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
corpus_tfidf = tfidf[corpus]

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=notopics)
corpus_lsi = lsi[corpus_tfidf]

#lsi.print_debug(num_topics=5, num_words=10)
################## LSI 
lsisimlist=[]
index = similarities.MatrixSimilarity(corpus_lsi)
row=0
for doc in corpus_lsi:
	col=0
	sims = index[doc]
	lsisimlist.append(list(sims))
	scorelist= list(enumerate(sims))
	# for each document, scorelist holds the similarities between that document to all other documents in the corpus (including itself)
	for score in scorelist:
		Scorematrix[row][col]=score[1]
		col=col+1
	row=row+1	

row=0
col=0
scores=""
for row in range(0,corpussize):
 	for col in range (0,corpussize):
		scores=scores+"\t"+str(Scorematrix[row][col]).strip()
	print scores.strip()
	scores=""	
# NOTE: Scores are in the 2D array Scorematrix. To get the similarity score between document x and document y, access Scorematrix[x-1][y-1]


getkeywords()	














