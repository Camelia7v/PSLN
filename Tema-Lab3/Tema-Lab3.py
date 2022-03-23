# -*- coding: utf-8 -*-
"""PSLN-Lab3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gWX0QEQh_XOmteVGnfadvVlPyRia9E_F

# Imports
"""

from bs4 import BeautifulSoup
import requests
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

"""# Corpus creation"""

# get URL
page = requests.get("https://ro.wikipedia.org/wiki/O_mie_nouă_sute_optzeci_și_patru_(roman)")

# scrape webpage
soup = BeautifulSoup(page.content, 'html.parser')
list(soup.children)

# write text into a file
f = open("corpus.txt", "ab")
for item in soup.find_all('p'):
    f.write(item.get_text().encode("UTF-8"))
f.close()

"""# Words extraction"""

text = open("corpus.txt", "r", encoding="utf-8").read()
words_list = word_tokenize(text)


words = list()
for item in words_list:
  if item.startswith("„"):
    words.append(item[1:]) 
  elif item not in ",.:;!?()„”-'[]–’":
    words.append(item)

print("All the words from the corpus: ")
print(len(words), words, "\n")


unique_words = set(words)
print("All the UNIQUE words from the corpus: ")
print(len(unique_words), unique_words)

"""# 2-gram language model

"""

list_of_bigrams = []
bigram_counts = {}
unigram_counts = {}

for i in range(len(words) - 1):
  if i < len(words) - 1 and words[i+1].islower():
    list_of_bigrams.append((words[i], words[i + 1]))

    if (words[i], words[i+1]) in bigram_counts:
      bigram_counts[(words[i], words[i + 1])] += 1
    else:
      bigram_counts[(words[i], words[i + 1])] = 1

  if words[i] in unigram_counts:
    unigram_counts[words[i]] += 1
  else:
    unigram_counts[words[i]] = 1
  
print("\n All the possible Bigrams are: ")
print(list_of_bigrams)

print("\n Bigrams along with their frequency: ")
print(bigram_counts)

print("\n Unigrams along with their frequency: ")
print(unigram_counts)



list_of_probabilities = {}

for bigram in list_of_bigrams:
    word1 = bigram[0]
    word2 = bigram[1]
    list_of_probabilities[bigram] = (bigram_counts.get(bigram)) / (unigram_counts.get(word1))

print("\n Bigrams along with their probability: ")
print(list_of_probabilities)

"""# Computing the probability for a new text"""

V = len(unique_words)

input = "They buy a big house"
# input = "Acest articol se referă la romanul 1999."
# input = "O mie nouă sute optzeci și patru"

input_words = input.split()

bigrams = []
for i in range(len(input_words) - 1):
    if i < len(input_words) - 1:
        bigrams.append((input_words[i], input_words[i + 1]))

print("\n The bigrams in given sentence are: ")
print(bigrams)


count = 0
for item in input_words:
  if item not in words:
    count += 1


sentence_probability = 1
if count == 0:
  for i in range(len(bigrams)):
    print('0: ', list_of_probabilities[bigrams[i]])
    sentence_probability *= list_of_probabilities[bigrams[i]]
else:
  for i in range(len(bigrams)):
    if bigrams[i] in list_of_bigrams:
      print('1: ', (bigram_counts[bigrams[i]] + 1) / (unigram_counts[bigrams[i][0]] + V))
      sentence_probability *= (bigram_counts[bigrams[i]] + 1) / (unigram_counts[bigrams[i][0]] + V)
    elif bigrams[i][0] in unigram_counts:
      print('2: ', 1 / (unigram_counts[bigrams[i][0]] + V))
      sentence_probability *= 1 / (unigram_counts[bigrams[i][0]] + V)
    else: 
      print('3: ', 1 / V)
      sentence_probability *= 1 / V 


print('\n' + f'The probablility of sentence: "{input}" is ' + str(sentence_probability))

"""# The example from course"""

words = ['<s>', 'there', 'is', 'a', 'big', 'house', '</s>', '<s>', 'i', 'buy', 
         'a', 'house', '</s>', '<s>', 'they', 'buy', 'the', 'new', 'house', '</s>']

list_of_bigrams = []
bigram_counts = {}
unigram_counts = {}

for i in range(len(words) - 1):
  if i < len(words) - 1 and words[i+1].islower():
    list_of_bigrams.append((words[i], words[i + 1]))

    if (words[i], words[i+1]) in bigram_counts:
      bigram_counts[(words[i], words[i + 1])] += 1
    else:
      bigram_counts[(words[i], words[i + 1])] = 1

  if words[i] in unigram_counts:
    unigram_counts[words[i]] += 1
  else:
    unigram_counts[words[i]] = 1

print("\n All the possible Bigrams are: ")
print(list_of_bigrams)

print("\n Bigrams along with their frequency: ")
print(bigram_counts)

print("\n Unigrams along with their frequency: ")
print(unigram_counts)


list_of_probabilities = {}

for bigram in list_of_bigrams:
    word1 = bigram[0]
    word2 = bigram[1]
    list_of_probabilities[bigram] = (bigram_counts.get(bigram)) / (unigram_counts.get(word1))

print("\n Bigrams along with their probability: ")
print(list_of_probabilities)


V = 10

# input = "<s> they buy a big house </s>"
input = "<s> they buy a red house </s>"

input_words = input.split()
sentence_probability = 1
bigrams = []

for i in range(len(input_words) - 1):
    if i < len(input_words) - 1:
        bigrams.append((input_words[i], input_words[i + 1]))

print("\n The bigrams in given sentence are: ")
print(bigrams)


count = 0
for item in input_words:
  if item not in words:
    count += 1

if count == 0:
  for i in range(len(bigrams)):
    print('0', list_of_probabilities[bigrams[i]])
    sentence_probability *= list_of_probabilities[bigrams[i]]
else:
  for i in range(len(bigrams)):
    if bigrams[i] in list_of_bigrams:
      print('1', (bigram_counts[bigrams[i]] + 1) / (unigram_counts[bigrams[i][0]] + V))
      sentence_probability *= (bigram_counts[bigrams[i]] + 1) / (unigram_counts[bigrams[i][0]] + V)
    elif bigrams[i][0] in unigram_counts:
      print('2', 1 / (unigram_counts[bigrams[i][0]] + V))
      sentence_probability *= 1 / (unigram_counts[bigrams[i][0]] + V)
    else: 
      print('3', 1 / V)
      sentence_probability *= 1 / V 

print('\n' + f'The probablility of sentence: "{input}" is ' + str(sentence_probability))