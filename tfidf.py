import argparse
import logging
import os
import time

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


def init_log(log_path, log_level=logging.WARNING):
    logfolder = os.path.dirname(log_path)
    if os.path.exists(logfolder) is False:
        try:
            os.makedirs(logfolder)
        except:
            # create folder failed, replace with current folder
            log_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.basename(log_path))
    logging.basicConfig(filename=log_path, level=log_level)


def get_process_time(start):
    sec = time.time() - start
    mins, sec = divmod(sec, 60)
    hours, mins = divmod(mins, 60)
    return '{} hours, {} minutes, {} seconds'.format(int(hours), int(mins), sec)


def get_tfidf(contents):
    start = time.time()
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    word_counts = vectorizer.fit_transform(contents)
    logging.debug('The word count shape {}'.format(word_counts.get_shape()))
    word = vectorizer.get_feature_names()
    logging.debug('Total has {} words'.format(len(word)))
    tfidf = transformer.fit_transform(word_counts)
    logging.debug('Takes {} to gen TF-IDF'.format(get_process_time(start)))
    return tfidf.toarray()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TF-IDF')
    parser.add_argument('-i', '--input', type=str, help='The Tokenized File Path', default='output_1.txt')
    parser.add_argument('-o', '--output', type=str, help='The TFIDF Result File Path', default='output.txt')
    parser.add_argument('-l', '--log', type=str, help='Log Level', default='WARNING')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        parser.print_help()
        exit(0)
    input_file = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)

    if os.path.exists(input_file) is False:
        print('{} not exists'.format(input_file))
        logging.error('{} not exists'.format(input_file))
        exit(0)

    logging.info("Start to load tokenized data from {}".format(input_file))
    with open(input_file, 'r') as fn:
        # contents = [l.strip().split(' ') for l in fn]
        contents = [l.strip() for l in fn]
    # import pdb; pdb.set_trace()
    content_len = len(contents)

    logging.info("Start to compute TF-IDF")
    tfidf = get_tfidf(contents)

    tfidf_len = len(tfidf)

    if content_len != tfidf_len:
        logging.error("Something wrong, {} contents, {} TF-IDF".format(content_len, tfidf_len))
        exit(0)

    logging.info("Start to write TF-IDF to output file")
    with open(output_file, 'w') as fn:
        for i in range(content_len):
            fn.write('{}, {}\n'.format(contents[i], str([v for v in tfidf[i]])))
