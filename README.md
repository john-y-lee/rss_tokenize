# rss_tokenize
# Programing Language: python 3.6
# Modules Information
* jieba
A tokenizer which supports Chinese.
[URL] https://pypi.org/project/jieba/

* beautifulsoup4
A module which could parse HTML tag
[URL] https://pypi.org/project/beautifulsoup4/

# Install Modules
* installation command
pip3 install -r requirements.txt

# Process Flow
1. Download RSS file if activate renew flag.
2. Parse RSS (XML format) file to extract description tag field.
3. Download News articles and replace description field data
   from the links in description field if set the Download parameter.
4. Write each description content to the description file.
5. Tokenize each content with jieba, filter with valid word if needed.
6. Write tokenized data into output file.

# How to execute
* python3.6 rss_tokenize.py [arguments]
* Arguments
 -i  --input          The file path of RSS. Default: news.rss
 -o  --output         The file path of tokenized result. Default: output.txt
 -d  --description    The file path of description. Default: description.txt
 -r  --renew          A flag to download new RSS file if activated. Default: None
 -u  --url            The RSS url for renew. Default: https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant
 -D  --Download       A flag to download News articles from the link in the description field
                      and replace the description data if activated. Default: None
 -f  --filter         A flag to filter invalid words or stop words after tokenized by jieba. Default: None
 -l  --log            Log level flag. Default: WARNING

# Optional setting
The parameter of "stop_words" could modify manually in code.


# tfidf
# Programing Language: python 3.6
# Modules Information
* scikit-learn
A well known machine learning module
[URL] https://scikit-learn.org/stable/

# Install Modules
* installation command
pip3 install -r requirements.txt

# Process Flow
1. Load description data from file from assignment 1 output file.
2. Compute TF-IDF by scikit-lean.
3. Write description data and TF-IDF to output file.

# How to execute
* python3.6 tfidf.py [arguments]
* Arguments
 -i  --input          The file path of description file. Default: output_1.txt
 -o  --output         The file path of result with TF-IDF. Default: output.txt
 -l  --log            Log level flag. Default: WARNING
