import argparse
import logging
import jieba
import os
import requests
import time
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

target_tag = 'description'
stop_words = ['__', '，']


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


def is_valid_word(w):
    valid_word = False
    if len(w) == 1:
        # keep a-z, A-Z, 0-9, and multi-bytes characters
        if 'a' <= w <= 'z' or \
           'A' <= w <= 'Z' or \
           '0' <= w <= '9' or \
           ord(w) > 127:
            valid_word = True
    elif len(w) > 1:
        if w not in stop_words:
            valid_word = True
    return valid_word


def download_rss(url, output):
    logging.debug("Start to download from {} to {}".format(url, output))
    start = time.time()
    r = requests.get(url)
    logging.debug("Takes {} to download RSS".format(get_process_time(start)))
    success = False
    if r.status_code == 200:
        logging.debug("Download success".format(url, output))
        try:
            with open(output, 'w') as fn:
                fn.write(r.text)
            success = True
        except Exception as e:
            # print("Write RSS to {} failed with {}".format(output, e))
            logging.error("Write RSS to {} failed with {}".format(output, e))
    else:
        # print("Download RSS failed with status code {} from {}".format(r.status_code, url))
        logging.error("Download RSS failed with status code {} from {}".format(r.status_code, url))
    try:
        r.close()
    except:
        pass
    return success


def download_url(url):
    logging.debug("Start to download url content from {}".format(url))
    r = requests.get(url)
    msg = ''
    logging.debug("response status code {}".format(r.status_code))
    if r.status_code == 200:
        msg = r.text
    else:
        logging.debug("download error message {}".format(r.text))
    try:
        r.close()
    except:
        pass
    return msg


def extract_tag(rss, download=False):
    logging.debug("Extract tag \"{}\" from {}, download: {}".format(target_tag, rss, download))
    start = time.time()
    tree = ET.parse(rss)
    root = tree.getroot()
    stack = [root]
    node_content = []
    # search all nodes children for target tag
    url_count = 0
    while len(stack) > 0:
        node = stack.pop(0)
        if node.tag == target_tag:
            nodetext = node.text.replace('\n', '')
            if download:
                # extract link from node text, if not append the node text
                links = get_link_from_anchor(nodetext)
                if len(links) == 0:
                    logging.debug("No anchor in {}".format(nodetext))
                    node_content.append(nodetext)
                else:
                    url_count += len(links)
                    for url in links:
                        msg = download_url(url)
                        # only keep with non-empty data, ignore if all urls are empty
                        if len(msg) > 0:
                            node_content.append(msg.replace('\n', ''))
                        else:
                            logging.debug("Empty content from {}".format(url))
            else:
                node_content.append(nodetext)
            continue
        ch = node.getchildren()
        if len(ch) > 0:
            stack.extend(ch)
    logging.debug("Takes {} to extract tag, download url count: {}".format(get_process_time(start), url_count))
    return node_content


def get_link_from_anchor(msg):
    try:
        soup = BeautifulSoup(msg, 'html.parser')
        links = [link.get("href") for link in soup.findAll("a")]
        logging.debug("Extract {} links from {}".format(len(links), msg))
    except Exception as e:
        logging.error("Falied to parse anchor from msg with {}".format(e))
        logging.error("msg: {}".format(msg))
        links = []
    return links


def tokenize_content(contents, filter=False):
    start = time.time()
    try:
        t_content = [jieba.lcut(c) for c in contents]
        if filter is True:
            f_content = []
            for content in t_content:
                f_content.append([c for c in content if is_valid_word(c) is True])
            # replace t_content by f_content
            t_content = f_content
    except Exception as e:
        logging.error("Tokenize by jieba failed with {}".format(e))
        t_content = []
    logging.debug("Takes {} to tokenize result".format(get_process_time(start)))
    return t_content


if __name__ == '__main__':
    """
    Process Folw:
    1) Download new RSS if set
    2) Parse RSS file to extract description tag field
    3) Replace description field if set the download parameter
    4) Write each description content to the description file
    5) Tokenize each content with jieba, filter with valid word if needed
    6) Write tokenized data into output file
    """

    parser = argparse.ArgumentParser(description='Tokenizer Parser')
    parser.add_argument('-i', '--input', type=str, help='The RSS File Path', default='news.rss')
    parser.add_argument('-o', '--output', type=str, help='The Tokenized Result File Path', default='output.txt')
    parser.add_argument('-d', '--description', type=str, help='The Description File Path', default='description.txt')
    parser.add_argument('-r', '--renew', action='store_true', help='Renew the RSS File')
    parser.add_argument('-u', '--url', type=str, help='The RSS Link', default='https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant')
    parser.add_argument('-D', '--Download', action='store_true', help='Download News from Description Link as Data Instead of Description Field')
    parser.add_argument('-f', '--filter', action='store_true', help='Filter the Invalid Words')
    parser.add_argument('-l', '--log', type=str, help='Log Level', default='WARNING')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        parser.print_help()
        exit(0)

    # log level: {'CRITICAL': 50, 'FATAL': 50, 'ERROR': 40, 'WARN': 30, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10, 'NOTSET': 0}
    log_level = logging._nameToLevel.get(args.log.upper(), 30)
    jieba.setLogLevel(log_level)
    init_log(os.path.abspath('log'), log_level)

    rss = os.path.abspath(args.input)
    descr = os.path.abspath(args.description)
    output = os.path.abspath(args.output)

    if args.renew is True:
        logging.info("Set to renew RSS")
        download_rss(args.url, rss)

    if os.path.exists(rss) is False:
        # print("{} not exists, please check or renew the RSS file".format(rss))
        logging.error("{} not exists, please check or renew the RSS file".format(rss))
        exit(0)

    logging.info("Start to extract tag contents from RSS")
    contents = extract_tag(rss, args.Download is True)
    logging.info("Get {} tag content result".format(len(contents)))
    try:
        logging.info("Write description file to {}".format(descr))
        with open(descr, 'w') as fn:
            for c in contents:
                fn.write('{}\n'.format(c))
    except Exception as e:
        # print("Write description file to {} failed with {}".format(descr, e))
        logging.error("Write description file to {} failed with {}".format(descr, e))

    logging.info("Start to tokenize contents, filter: {}".format(args.filter))
    t_content = tokenize_content(contents, args.filter is True)
    logging.info("Get {} tokenized content result".format(len(t_content)))
    try:
        logging.info("Write tokenize file to {}".format(output))
        with open(output, 'w') as fn:
            for t in t_content:
                fn.write('{}\n'.format(' '.join(t)))
    except Exception as e:
        # print("Write output file to {} failed with {}".format(output, e))
        logging.error("Write output file to {} failed with {}".format(output, e))
