__author__ = 'jerry'
import os, sys
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string, math
import xml.dom.minidom
from xml.dom.minidom import Document

stoplist = set(stopwords.words('english'))
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

def keyword(sentence):
    '''
    extract keywords from sentences
    :param sentence:
    :return:
    '''
    keywords = {}
    sent = sentence
    tokens = word_tokenize(sent)
    wordnet_lemmatizer = WordNetLemmatizer()
    lem_tokens = [wordnet_lemmatizer.lemmatize(t) for t in tokens] #lemmatization
    sel_tokens = [word for word in lem_tokens if word not in punctuation and word not in stoplist] #ignoring stopwords
    for token in sel_tokens:
        keywords[token] = 0
    return keywords.keys()

def read_summary(in_file):
    '''
    read one summary
    :param in_file: handle of summary file
    :return: summary_id, unigram, bigram
    '''
    summary_id = 0
    src_sents = []
    sent_keywords = []
    summary_type = ''
    #read one summary
    line = in_file.readline().rstrip()
    if line:
        terms = line.split('\t')
        if len(terms) == 4:
            summary_type = terms[1]
            summary_id = int(terms[2])
            article = terms[3]
            sents = sent_tokenize(onlyascii(article)) #sentence segmentation
            for sent in sents:
                keywords = keyword(sent)
                if len(keywords):
                    sent_keywords.append(keywords)
                    src_sents.append(sent)
    return summary_id, summary_type, src_sents, sent_keywords


class story:
    def __init__(self):
        self.src_sentences = []
        self.sent_keywords = []
        self.src_part = []
    def add_part(self, part_number, part):
        sents = sent_tokenize(onlyascii(part)) #sentence segmentation
        sent_keywords = []
        keywords = []
        for sent in sents:
            keywords = keyword(sent)
            if len(keywords):
                sent_keywords.append(keyword(sent))
                self.src_part.append(part_number)
                self.src_sentences.append(sent)
        self.sent_keywords.extend(sent_keywords)
    def get_relevent_sentence(self, src_keywords):
        keywords = {}
        for term in src_keywords:
            keywords[term] = 0

        rel_sentences_keywords = []
        rel_sentences_scores = []
        rel_sentences_src = []
        rel_sentences_parts = []
        score_dict = {}
        for i in range(len(self.src_sentences)):
            story_keywords = self.sent_keywords[i]
            score = 0.0
            for term in story_keywords:
                if term in keywords:
                    score += 1.0
            #score = score / math.sqrt(len(story_keywords)) / math.sqrt(len(keywords))
            if score > 0:
                score_dict[i] = score
        ranked_sents = sorted(score_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        for i in range(min(5, len(ranked_sents))):
            item = ranked_sents[i]
            rel_sentences_keywords.append(self.sent_keywords[item[0]])
            rel_sentences_scores.append(item[1])
            rel_sentences_src.append(self.src_sentences[item[0]])
            rel_sentences_parts.append(self.src_part[item[0]])
        return rel_sentences_keywords, rel_sentences_scores, rel_sentences_src, rel_sentences_parts


def read_story(in_file, sel_id, first_line):
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
    st = story()
    line = first_line.rstrip()
    while line:
        terms = line.split('\t')
        if len(terms) != 4:
            line = in_file.readline().rstrip()
            continue
        story_id = int(terms[0])
        if story_id == sel_id:
            st.add_part(int(terms[2]), terms[3])
        elif story_id != sel_id:
            break
        line = in_file.readline().rstrip()
    return line, st

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print('USAGE: python summary_ana.py <summary_path> <story_path>')
        exit(1)
    summary_file_path = '/media/jerry/SSD/AM/TopStory/wattpad_summary_sel.sort'
    story_file_path = '/media/jerry/SSD/AM/TopStory/story_file_sel.sort'
    summary_file = open(summary_file_path, 'rb')
    story_file = open(story_file_path, 'rb')
    first_line = 'BEGIN'
    document = Document()
    root = document.createElement('root') #root
    document.appendChild(root)
    while True:
        summary_id, summary_type, src_sents, sent_keywords = read_summary(summary_file) #read one summary
        if summary_id == 0:
            break
        if len(src_sents) == 0 or len(sent_keywords) == 0: #unavailable summary
            continue
        first_line, st = read_story(story_file, summary_id, first_line)
        if not first_line:
            break
        summary_root = document.createElement('summary_root_' + str(summary_id))
        summary_root.setAttribute('summary_type', summary_type)
        summary_root.setAttribute('summary_id', str(summary_id))
        root.appendChild(summary_root)
        print summary_id
        for i in range(len(src_sents)):
            rel_sentences_keywords, rel_sentences_scores, rel_sentences_src, rel_sentences_parts = st.get_relevent_sentence(sent_keywords[i])
            ############Add to xml############
            src_sent = document.createElement('src_sent')
            src_sent.setAttribute('src', src_sents[i])
            summary_root.appendChild(src_sent)
            for j in range(len(rel_sentences_parts)):
                sentence = document.createElement('relevent_sentence_' + str(j))
                sentence.setAttribute('src', rel_sentences_src[j])
                sentence.setAttribute('score', str(rel_sentences_scores[j]))
                sentence.setAttribute('part', str(rel_sentences_parts[j]))
                src_sent.appendChild(sentence)
    ########### write xml
    f = open('/media/jerry/SSD/AM/TopStory/relevent_sentences.xml','w')
    f.write(document.toprettyxml(indent = "\t", newl = "\n", encoding = "utf-8"))
    f.close()
    summary_file.close()
    story_file.close()