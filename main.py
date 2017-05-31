'''
* @What Data Mining Final Project : Using Tweeter sentiment analysis to predict change in stock price.
* @Author Sabastian Mugazambi & Simon Orlovsky
* @Date 05/27/2017
* @Purpose : Analyses a tweet and predicts the effect of the tweet on the mentioned company stock price.
* @ test : python main.py 2 F realDonaldTrump 'North Korea has shown great disrespect for their neighbor, China, by shooting off yet another ballistic missile...but China is trying hard!' 05/27/2017
'''
#import libraries
import tweepy #https://github.com/tweepy/tweepy
import csv
import random
import numpy as np
import heapq
import math
import collections
import time
import copy
import sys
import scipy.stats
import nltk
import matplotlib.pyplot as plt
import pylab

import quandl
quandl.ApiConfig.api_key = "mwbHy7C9x4U5HWdxhM9i"
import pandas
import datetime

#importing our files
from tweet_dumper import *
# from sentiment_analysis import *
word_features = 0

def load_training(filename):
    """
    @Function :  load_training(filename)
    @Args: <filename>
    @Purpose: Takes a training file name csv
    """
    pos = []
    neg = []
    with open(filename, 'rU') as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    for pair in content:
        pair = pair.split(",\\t")

        if(pair[1] == 'positive'):
        	pos.append((pair[0],pair[1]))
        else:
            neg.append((pair[0],pair[1]))

    return (pos,neg)


    # all_tweets = np.loadtxt(filename,dtype=str,delimiter=",")
    # print all_tweets

def tokenize(pos_tweets, neg_tweets):
    """
    @Function :  tokenize(pos_tweets, neg_tweets)
    @Args: <positive tweets> <negative tweets>
    @Purpose: takes positive and negative tweets and tokenizes them
    """
    tweets = []
    for (words, sentiment) in pos_tweets + neg_tweets:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
        tweets.append((words_filtered, sentiment))
    return tweets

def get_words_in_tweets(tweets):
    """
    @Function :  get_words_in_tweets(tweets)
    @Args: <tweets>
    @Purpose: Takes tweets and gets word features
    """
    all_words = []
    for (words, sentiment) in tweets:
      all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    """
    @Function :  get_word_features(wordlist)
    @Args: <wordlist>
    @Purpose: Takes a list of words and converts it into feature list
    """
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features


def extract_features(document):
    """
    @Function :  extract_features(document)
    @Args: <document>
    @Purpose: Takes an entire documents of words and returns frequency distribution
    """
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains: %s' % word] = (word in document_words)
    return features


def three_day(ticker, date):
    try:
        after = date
        before = date
        after += datetime.timedelta(days=1)
        before -= datetime.timedelta(days=1)
        data = quandl.get('WIKI/'+ticker, start_date=before, end_date=after)
        old = data["Close"][0]
        new = data["Close"][1]

        percent_change = (old - new)/old
        return percent_change

    except:
        print "Data not available in WIKI stock data or incorrect ticker: ", ticker

# three_day(ticker)


def main():
    """
    @Function :  Main
    @Args: None <uses sys.argv>
    @Purpose: function and user interface of this program
    """
    global word_features
    #getting the argments
    pred_k = int(sys.argv[1])
    c_symbol = sys.argv[2]
    person = sys.argv[3]
    tweet = sys.argv[4]
    date = sys.argv[5]

    # STEP 1 : Get and dumb tweets
    #get_all_tweets(person)

    # STEP 2 : Create training sets
    train_data = load_training("training_tweets.csv")

    # STEP 3 : torkenize training data set tweets
    tweets = tokenize(train_data[0], train_data[1])

    # STEP 4 : Feature extraction from the training set
    word_features = get_word_features(get_words_in_tweets(tweets))
    training_set = nltk.classify.apply_features(extract_features, tweets)

    #STEP 5 : classify the given tweet as positive or negative sentiment
    classifier = nltk.NaiveBayesClassifier.train(training_set)
    pred_directional_change =  classifier.classify(extract_features(tweet.split()))

    #print out the sentiment
    print "\n------------------------"
    print "\nThe tweet is:\n"," '",tweet,"'"
    print "\n------------------------"
    print "\nSentiment Classification :", pred_directional_change
    print "\n------------------------"

    stock_tweets = {}
    with open('stock_tweets.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        counter = 0
        for row in spamreader:
            date_split = row[0].split('-')
            d = datetime.date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
            tweet = row[1]
            ticker = row[2]
            pred_directional_change =  classifier.classify(extract_features(tweet.split()))

            print three_day(row[2], d), row[2], classifier.prob_classify(extract_features(tweet.split())).prob('positive'), classifier.prob_classify(extract_features(tweet.split())).prob('negative')



if __name__ == '__main__':
	main()
