import math
from bs4 import BeautifulSoup
import requests
from nltk.tokenize import word_tokenize
import simplemma

# nltk.download('punkt')


"""
   Scrapping from Wikipedia
"""

page = requests.get("https://ro.wikipedia.org/wiki/O_mie_nouă_sute_optzeci_și_patru_(roman)")
soup = BeautifulSoup(page.content, 'html.parser')
list(soup.children)


"""
   Writing the text into a file
"""

# f = open("corpus.txt", "ab")
# for item in soup.find_all('p'):
#     f.write(item.get_text().encode("UTF-8"))
# f.close()


"""
   Extracting the words from the text
"""

text = open("corpus.txt", "r", encoding="utf-8").read()
words_list = word_tokenize(text)

words = []
for item in words_list:
    if item.startswith("„"):
        words.append(item[1:])
    elif item not in ",.:;!?()„”-'[]–’… ''``" and item != '':
        words.append(item)

# print("All the words from the corpus: ")
# print(len(words), words, "\n")


"""
   Lemmatization
"""

langdata = simplemma.load_data('ro')
lemmatized_words = []
for word in words:
    if word == '':
        continue
    lemmatized_words.append(simplemma.lemmatize(word, langdata))
    # print(word, simplemma.lemmatize(word, langdata))

# print("The lemmatized words from the corpus: ")
# print(len(lemmatized_words), lemmatized_words)


"""
   Creating the list of bi-grams, a dictionary with bi-grams frequency and
a dictionary with the distances between each bi-gram
"""

# words = lemmatized_words
list_of_bigrams = []
bigram_counts = {}
bigram_distances = {}
window = 5
for i in range(len(words) - 1):
    if i < len(words) - window:
        for j in range(i + 1, i + window + 1):
            list_of_bigrams.append((words[i], words[j]))

            # frequency
            if (words[i], words[j]) in bigram_counts:
                bigram_counts[(words[i], words[j])] += 1
            else:
                bigram_counts[(words[i], words[j])] = 1

            # distances
            if (words[i], words[j]) in bigram_distances:
                bigram_distances[(words[i], words[j])] += [j - i]
            else:
                bigram_distances[(words[i], words[j])] = [j - i]

    elif i < len(words) - 1:
        for j in range(i + 1, len(words)):
            list_of_bigrams.append((words[i], words[j]))

            # frequency
            if (words[i], words[j]) in bigram_counts:
                bigram_counts[(words[i], words[j])] += 1
            else:
                bigram_counts[(words[i], words[j])] = 1

            # distances
            if (words[i], words[j]) in bigram_distances:
                bigram_distances[(words[i], words[j])] += [j - i]
            else:
                bigram_distances[(words[i], words[j])] = [j - i]

# print("\n All the possible Bigrams are: ")
# print(len(list_of_bigrams), list_of_bigrams)

print("\n Bigrams along with their frequency: ")
print(len(bigram_counts), bigram_counts)

print("\n Bigrams along with their distances: ")
print(len(bigram_distances), bigram_distances)


"""
   Computing the mean and variance for each bi-gram
"""

mean_and_variance = {}
threshold = 5
for bigram in bigram_counts.keys():
    if bigram_counts[bigram] >= threshold:
        mean = sum(bigram_distances[bigram]) / bigram_counts[bigram]
        s = 0
        for d in bigram_distances[bigram]:
            s += (d - mean) ** 2
        variance = math.sqrt(s / (bigram_counts[bigram] - 1))
        mean_and_variance[bigram] = [mean, variance]

print("\n Bigrams along with their mean and variance: ")
print(len(mean_and_variance), mean_and_variance)

# --- If the variance is 0, it means that all the distances between those
# two words are equal.
# --- A low standard deviation means that the 2 words usually occur at about
# the same distance.
# --- If the distances between those two words are randomly distributed
# (which is the case for 2 words that are not in a particular relationship),
# then the variance will be high.


"""
   Selecting the bi-grams that have a variance smaller then 1
"""

variance_smaller_then_1 = {}
for bigram in mean_and_variance.keys():
    if mean_and_variance[bigram][1] < 1:
        variance_smaller_then_1[bigram] = mean_and_variance[bigram]

print("\n The bigrams with variance smaller than 1: ")
print(len(variance_smaller_then_1), variance_smaller_then_1)
