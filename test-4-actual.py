import numpy
import re, collections
import requests
import lxml
import base64
import nltk
import getpass
import urllib2
import cgitb
import time
import sys
import MySQLdb

dbc = MySQLdb.connect(host="localhost",user="root",passwd="shagunakarsh",db="gsf")
cursor = dbc.cursor()

DICTIONARY = "/home/shagun/Desktop/gsfhack/ramakant-mnew/products.txt";
TARGET = ""
MAX_COST = 1
 
# Keep some interesting statistics
NodeCount = 0
WordCount = 0

# The Trie data structure keeps a set of words, organized with one node for
# each letter. Each node has a branch for each letter that may follow it in the
# set of words.
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

        global NodeCount
        NodeCount += 1

    def insert( self, word ):
        node = self
        for letter in word:
            if letter not in node.children: 
                node.children[letter] = TrieNode()

            node = node.children[letter]

        node.word = word

# read dictionary file into a trie
trie = TrieNode()
for word in open(DICTIONARY, "rt").read().split():
    WordCount += 1
    trie.insert( word )

print "Read %d words into %d nodes" % (WordCount, NodeCount)

# The search function returns a list of all words that are less than the given
# maximum distance from the target word
def search( word, maxCost ):

    # build first row
    currentRow = range( len(word) + 1 )

    results = []

    # recursively search each branch of the trie
    for letter in trie.children:
        searchRecursive( trie.children[letter], letter, word, currentRow, 
            results, maxCost )
    as_strings = []  
    for i in results:
        as_strings.append(i[0])
    return as_strings

# This recursive helper is used by the search function above. It assumes that
# the previousRow has been filled in already.
def searchRecursive( node, letter, word, previousRow, results, maxCost ):

    columns = len(word) + 1
    currentRow = [previousRow[0] + 1 ]

    # Build one row for the letter, with a column for each letter in the target
    # word, plus one for the empty string at column 0
    for column in xrange( 1, columns ):

        insertCost = currentRow[column - 1] + 1
        deleteCost = previousRow[column] + 1

        if word[column - 1] != letter:
            replaceCost = previousRow[ column - 1 ] + 1
        else:                
            replaceCost = previousRow[ column - 1 ]

        currentRow.append( min( insertCost, deleteCost, replaceCost ) )

    # if the last entry in the row indicates the optimal cost is less than the
    # maximum cost, and there is a word in this trie node, then add it.
    if currentRow[-1] <= maxCost and node.word != None:
        results.append( (node.word, currentRow[-1] ) )

    # if any entries in the row are less than the maximum cost, then 
    # recursively search each branch of the trie
    if min( currentRow ) <= maxCost:
        for letter in node.children:
            searchRecursive( node.children[letter], letter, word, currentRow, 
                results, maxCost )

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(file('big.txt').read()))
print len(NWORDS)
alphabet = 'abcdefghijklmnopqrstuvwxyz'

def spelltest2(tests):
    var = nltk.word_tokenize(tests)
    tmp = nltk.pos_tag(var)
   # print tmp
    return tmp


def SpellCheck(data,nlp_output):
    input_string = data
    new_str = ""
    line = input_string.split(' ')
    print line
    combinations = []
    dct = {}
    speech = {}
    for tuples in nlp_output:
        dct[tuples[0]] = tuples[1]    
    l = len(line)
    a = []
    for w in range(l):
        if(dct[line[w]] == 'ADJ' or dct[line[w]] == 'NNP' or dct[line[w]] == 'NN' or dct[line[w]] == 'N'or dct[line[w]] == 'NP' or dct[line[w]] == 'NUM'): 
            a.append(line[w])
    print a
    for w in range(len(a)):
        print w
        if(dct[a[w]] == 'NN' or dct[a[w]] == 'NNP' or dct[a[w]] == 'N'or dct[a[w]] == 'NP' or dct[a[w]] == 'NUM'or dct[a[w]] =='ADJ'):
            poss =  search(a[w], MAX_COST) 
            print poss 
            t = dct[a[w]]
            for pos_i in poss:
                speech[pos_i] = t
#           if(w == l-2 and tuples[line[w]] == 'NN' and tuples[line[w+1]] == 'ADJ'):
#           else if(w == l-1 and tuples[line[w]] == 'ADJ'):
#           else :
            tot_comb = []
            for pos_i in poss:
                new_comb = combinations
                if new_comb == []:       
                    new_comb = poss
                else:
                    for stng in new_comb:
                         stng += pos_i
                tot_comb += new_comb    
                combinations = tot_comb

#    if(tuples[line[l-2]] == 'NN' and tuples[line[l-1]] == 'AJ'):
        #  spell check of the word line[l-1]
#         spellchecker.  
        #  all the possible nearest words poss[n]        
#         tot_comb = []
#            for pos_i in poss:
#                new_comb = combinations
#            for stng in new_comb:
#                stng.append(pos_i)
#           tot_comb += new_comb    
#         combinations = tot_comb
        #  spell check of the word line[l-2]
        #  all the possible nearest words poss[n]
#         tot_comb = []
#            for pos_i in poss:
#               new_comb = combinations
#            for stng in new_comb:
#                stng.append(pos_i)
#            tot_comb += new_comb    
#         combinations = tot_comb
    return combinations
                      
# Rank the combinations of the key results using the hash table generated.

def PrintSuggestions(combinations):                 
    print combinations
    for result in combinations:
        words = result.split(' ')
        print words
        valid_keys = 1
    for i in range(len(words)-1):
        if(speech[words[i]] == 'ADJ'):
            cursor.execute("SELECT * FROM indiamart WHERE (adj,noun) values (%s,%s)",(words[i],words[i+1]))
            numrows = (int)(cursor.rowcount)
            if(numrows == 0):
                 valid_keys = 0
        else:
            for j in range(i+1,len(words)):
                cursor.execute("SELECT * FROM indiamart WHERE (adj,noun) values (%s,%s)",(words[i],words[j]))
                numrows = (int)(cursor.rowcount)
                if(numrows == 0):
                    valid_keys = 0
    if(valid_keys):                  
        print(words)

with open ("mydata.txt", "r") as myfile:
    data = myfile.read()

sr = data.lower()
nstr=""
for i in range(len(sr)):
    if not(sr[i] == ',' or sr[i] == '.' or sr[i] == '!' or sr[i] == '?' or sr[i] == '//'  or sr[i] == '&' or  sr[i] == '*' or sr[i] == '\'' or sr[i] == '(' or sr[i] == ')' or sr[i] == '-' or sr[i] == '_' or  sr[i] == '/' or sr[i] == ':' or sr[i] == '#' or sr[i] == '%' or sr[i] == '^' or sr[i] == '=' or sr[i] == '[' or sr[i] == ']' or sr[i] == '|' or sr[i] == '~' or sr[i] == '{' or sr[i] == '}' or sr[i] == '\"' or sr[i] == '$' or sr[i] == ';' or sr[i] == '@' or sr[i] == '\n'):
        nstr += str(sr[i])
MAX_COST = 1
lst = spelltest2(nstr)
print nstr
comb = SpellCheck(nstr,lst)
PrintSuggestions(comb)
                      
# NLP of query input


       
        
    
    
    
    




