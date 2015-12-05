__author__ = 'jerry'
import os, sys
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
#stoplist = set(stopwords.words('english'))
punctuation = set(string.punctuation)

def onlyascii(source):
    '''
    only keep ascii encoded words (needed by sent_tokenize)
    :param source: string
    :return: target: string after deleting un-ascii characters
    '''
    target = ''
    for a in source:
        if ord(a) >= 32 and ord(a) <= 126:
            target += a
    return target

def article2word(article):
    '''
    extract unigram and bigram from article
    :param article: string
    :return: dict of unigram, bigram
    '''
    unigram = {}
    bigram = {}
    sents = sent_tokenize(onlyascii(article)) #sentence segmentation
    wordnet_lemmatizer = WordNetLemmatizer()
    for sent in sents:
        tokens = word_tokenize(sent)
        lem_tokens = [wordnet_lemmatizer.lemmatize(t) for t in tokens] #lemmatization
        sel_tokens = [word for word in lem_tokens if word not in punctuation] #ignoring stopwords
        pre_token = "BE"
        for token in sel_tokens:
            unigram[token] = 0
            bigram[pre_token + "_" + token] = 0
            pre_token = token
    return unigram, bigram

def read_summary(in_file):
    '''
    read one summary
    :param in_file: handle of summary file
    :return: summary_id, unigram, bigram
    '''
    summary_id = 0
    unigram = {}
    bigram = {}
    #read one summary
    line = in_file.readline().rstrip()
    while line:
        terms = line.split('\t')
        if len(terms) == 2:
            summary_id = int(terms[0])
            unigram, bigram = article2word(terms[1])
            return summary_id, unigram, bigram
    return summary_id, unigram, bigram

def read_story(in_file, sel_id, unigram, bigram, first_line):
    '''
    read one story
    :param in_file: handle of story file
    :param sel_id: selected group id
    :param unigram: unigram of story file
    :param bigram: bigram of story file
    :param first_line: first line of current story (because it was already read)
    :return: first_line of next story
    '''
    #read one story
    line = first_line.rstrip()
    while line:
        terms = line.split('\t')
        if len(terms) != 4:
            line = in_file.readline().rstrip()
            continue
        story_id = int(terms[0])
        if story_id == sel_id:
            p_unigram, p_bigram = article2word(terms[3])
            unigram.update(p_unigram)
            bigram.update(p_bigram)
        elif story_id > sel_id:
            break
        line = in_file.readline().rstrip()
    return line

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('USAGE: python summary_ana.py <summary_path> <story_path>')
        exit(1)
    summary_file_path = sys.argv[1] #'/media/jerry/SSD/AM/wattpad_summary'
    story_file_path = sys.argv[2] #'/media/jerry/F/story_file'
    summary_file = open(summary_file_path, 'rb')
    story_file = open(story_file_path, 'rb')
    first_line = 'BEGIN'
    while True:
        summary_id, summary_unigram, summary_bigram = read_summary(summary_file) #read one summary
        if summary_id == 0:
            break
        if len(summary_unigram) == 0 or len(summary_bigram) == 0: #unavailable summary
            continue
        story_unigram = {}
        story_bigram = {}
        first_line = read_story(story_file, summary_id, story_unigram, story_bigram, first_line)
        if not first_line:
            break
        if len(story_unigram) == 0 or len(story_bigram) == 0: #not find a story
            continue
        same = 0.0
        for term in summary_unigram.keys():
            if term in story_unigram:
                same += 1
        bisame = 0.0
        for term in summary_bigram.keys():
            if term in story_bigram:
                bisame += 1
        print str(summary_id) + "\t" + str(same / len(summary_unigram)) + "\t" + str(bisame / len(summary_bigram))
    summary_file.close()
    story_file.close()