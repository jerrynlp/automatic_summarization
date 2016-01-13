from operator import add
from pyspark import  SparkContext
sc = SparkContext( 'local', 'pyspark')
def tokenize(text):
    terms = text.split('\t')
    summary = []
    if len(terms) == 2:
        summary = terms[1].split()
    return summary

text = sc.textFile("/media/jerry/SSD1/AM/TopStory/wattpad_summary")
words = text.flatMap(tokenize)
wc = words.map(lambda x: (x,1))
counts = wc.reduceByKey(add)
counts.saveAsTextFile("/media/jerry/SSD1/AM/TopStory/wc")
