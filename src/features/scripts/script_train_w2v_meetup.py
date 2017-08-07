import pandas as pd
import re
import nltk
import sys
sys.path.append('src/features')
from tsne_transformer import *

# Text is processed in a different here to keep the tokens intact.

def column2list(dataframe, column):
	"""Transform a dataframe column to a list.
	
	Args:
		dataframe: Name of a dataframe
		column (str): Name of the selected column.
	
	Return:
		Column as a list.
		
	"""
	return list(dataframe[column])

def preprocess_document(text):
	"""Wrapper of the above."""
	return create_tokens(lowercase_text(text))

def lowercase_text(text):
	"""Lowercase a string.
	
	Args:
		text (str): String to lowercase.
		
	Return:
		Lowercased text.
		
	"""
	return text.lower()

def create_tokens(text):
	"""Split a string into tokens. The tokens will be created by identifying
	HTML tags, @, #, emoticons, words and numbers.

	Args:
		text (str): Raw text data

	Return:
		tokens (list, str): The pieces of the string.

	"""
	regex_str = [r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs, 
				 r'\'(.+?)\'']

	# Create the tokenizer which will be case insensitive and will ignore space.
	tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)

	tokens = tokens_re.findall(text) # Find all patterns and tokenize them
	return tokens

def train_word2vec(sentences, size, window, min_count, iterations):
	"""Train a word2vec model. Training is optimised with Negative Sampling.
	
	Args:
		sentences (list, str): The tokenized sentences.
		size (int): The number of neurons in the hidden layer. It corresponds to the length of the vector representation of words.
		window (int): The number of words before and after the target word to consider as context.
		min_count (int): Ignore all words with total frequency lower than this.
		iterations (int): Number of iterations (epochs) over the corpus.
		
	Return:
		Word2Vec model.
		
	"""
	return gensim.models.word2vec.Word2Vec(sentences=sentences, size=size, window=window, 
										   min_count=min_count, iter=iterations)

if __name__ == '__main__':

	# Read dataframe
	df_groups = pd.read_csv('data/interim/df_groups_lad_and_topics.csv')

	# List with the tags.
	tags = column2list(df_groups, 'topic_name')

	print('PREPROCESSING TAGS')
	preprocessed_tags = [preprocess_document(tag) for tag in tags]

	# Small hack to process the text
	texts = []
	for preprocessed_tag in preprocessed_tags:
		tokens = []
		for tup in preprocessed_tag:
			tokens.append(tup[1])
		texts.append(tokens)

	# Clean documents that will be used for training the word2vec model.
	documents = [[re.sub('\s', '_', txt) for txt in text] for text in texts]

	print('TRAINING WORD2VEC')
	# Train model
	w2v = train_word2vec(documents, 300, 5, 2, 20)

	# # Save model

	# w2v.save('models/w2v.word2vec')

	# Instantiate TSNE class
	ts = TransformerTSNE(w2v)
	dict_keys, dict_values = ts.unravel_dictionary(ts.word_vectors())
	# Calculate cosine distance
	cos_dist = ts.calculate_cosine_distance(ts.calculate_cosine_similarity(ts.vectors2sparse_matrix(dict_values)))
	print('SHAPE OF COSINE DISTANCE MATRIX: {}'.format(cos_dist.shape))
	print('CALCULATING TSNE...')
	# Train TSNE
	tsne_space = ts.tsne_transformation(cos_dist, 500, 90)

	# Save 2D space
	with open('data/models/tsne_space.pickle', 'wb') as h:
		pickle.dump(tsne_space, h)

	# Save used tokens
	with open('data/models/tokens.pickle', 'wb') as h:
		pickle.dump(dict_keys, h)

	# Visualise TSNE
	ts.word_vectors_in_space(dict_keys, tsne_space)