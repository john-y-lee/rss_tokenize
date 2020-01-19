import argparse
import logging
import os
import time

from sklearn.feature_extraction.text import TfidfVectorizer


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


def get_tfidf(contents, ngram=None, max_df=None, min_df=None):
    start = time.time()

    vectorizer = TfidfVectorizer()
    if ngram is not None:
        # verify format
        # format should be two integer join with ',' such as 1,1 or 1,2
        try:
            sp_n = ngram.split(',')
            if len(sp_n) == 2:
                ngram_range = tuple([int(v) for v in sp_n])
                vectorizer.set_params(ngram_range=ngram_range)
        except Exception as e:
            logging.warning("Wrong format for ngram with {}, {}".format(ngram, e))
    if max_df is not None:
        # verify format
        # should be float of integer
        try:
            if '.' in max_df:
                max_df = float(max_df)
                if max_df > 1.0:
                    max_df = 1.0
                if max_df < 0.0:
                    max_df = 0.0
            else:
                max_df = int(max_df)
            vectorizer.set_params(max_df=max_df)
        except Exception as e:
            logging.warning("Wrong format for max_df with {}, {}".format(max_df, e))
    if min_df is not None:
        # verify format
        # should be float of integer
        try:
            if '.' in min_df:
                min_df = float(min_df)
                if min_df > 1.0:
                    min_df = 1.0
                if min_df < 0.0:
                    min_df = 0.0
            else:
                min_df = int(min_df)
            vectorizer.set_params(min_df=min_df)
        except Exception as e:
            logging.warning("Wrong format for min_df with {}, {}".format(min_df, e))

    tfidf = vectorizer.fit_transform(contents)

    words = vectorizer.get_feature_names()
    logging.debug('Total has {} words. First 5 are {}'.format(len(words), words[:min(5, len(words))]))

    logging.debug('Takes {} to gen TF-IDF'.format(get_process_time(start)))
    return tfidf.toarray()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TF-IDF')
    parser.add_argument('-i', '--input', type=str, help='The Tokenized File Path', default='output_1.txt')
    parser.add_argument('-o', '--output', type=str, help='The TFIDF Result File Path', default='output.txt')
    parser.add_argument('-n', '--ngram', type=str, help='The lower and upper boundary of the range of n-values for different n-grams to be extracted.')
    parser.add_argument('-m', '--min_df', type=str, help='When building the vocabulary ignore terms that have a document frequency strictly lower than the given threshold.')
    parser.add_argument('-M', '--max_df', type=str, help='When building the vocabulary ignore terms that have a document frequency strictly higher than the given threshold.')
    parser.add_argument('-l', '--log', type=str, help='Log Level', default='WARNING')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        parser.print_help()
        exit(0)
    input_file = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)

    log_level = logging._nameToLevel.get(args.log.upper(), logging.WARNING)
    init_log(os.path.abspath('log'), log_level)

    if os.path.exists(input_file) is False:
        print('{} not exists'.format(input_file))
        logging.error('{} not exists'.format(input_file))
        exit(0)

    logging.info("Start to load tokenized data from {}".format(input_file))
    with open(input_file, 'r') as fn:
        contents = [l.strip() for l in fn]
    content_len = len(contents)

    logging.info("Start to calculate TF-IDF")
    tfidf = get_tfidf(contents, ngram=args.ngram,
                      max_df=args.max_df, min_df=args.min_df)

    tfidf_len = len(tfidf)

    if content_len != tfidf_len:
        print("Something wrong, {} contents, {} TF-IDF".format(content_len, tfidf_len))
        logging.error("Something wrong, {} contents, {} TF-IDF".format(content_len, tfidf_len))
        exit(0)

    logging.info("Start to write TF-IDF to output file")
    with open(output_file, 'w') as fn:
        for i in range(content_len):
            fn.write('{}, {}\n'.format(contents[i], str([v for v in tfidf[i]])))
    print("Process completed")
    logging.info("Process completed")
