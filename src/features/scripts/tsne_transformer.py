import gensim
import numpy as np
import scipy
from scipy import sparse
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
import plotly
import plotly.graph_objs as go
from plotly.offline import plot

class TransformerTSNE():
	def __init__(self, word2vec_model):
		self.word2vec_model = word2vec_model

	def word_vectors(self):
		"""Find the N-dimensional vector of each word.
		
		Args:
			word2vec_model: Trained word2vec model.
		
		Return:
			token_vectors (dict): Dictionary where keys are the tokens and values the N-dim vectors. 
			
		"""
		token_vectors = {}
		for i in self.word2vec_model.vocab:
			token_vectors[i] = self.word2vec_model[i]
		return token_vectors

	def vectors2sparse_matrix(self, vectors):
		"""Transform a vector to a sparse matrix.
		
		Args:
			vectors (array): The set of N-dimensional vectors.
			
		Return:
			A sparse matrix.
			
		"""
		return scipy.sparse.csr_matrix(vectors, dtype = 'double')

	def unravel_dictionary(self, token_vectors):
		"""Extract the values of a dictionary.
		
		Args:
			token_vectors (dict): Dictionary where keys are the tokens and values the N-dim vectors. 
		
		Return:
			dict_keys (list, str): The keys of a dictionary.
			dict_values (array, float): The values of a dictionary in a Numpy array.
			
		"""
		dict_keys = list(token_vectors.keys())
		dict_values = np.array(list(token_vectors.values()))
		
		return dict_keys, dict_values

	def calculate_cosine_similarity(self, sparse_matrix):
		"""Calculate the cosine similarity of a sparse matrix."""
		return cosine_similarity(sparse_matrix)

	def calculate_cosine_distance(self, similarities):
		"""Find the cosine distance of some entities. Cosine distance = 1 - cosine similarity.

		Args:
			similarities (array): The cosine similarity.

		Return:
			cosine_distance (array): The cosine distance.

		"""
		cos_distance = 1 - similarities
		return np.clip(cos_distance,0,1,cos_distance)

	def tsne_transformation(self, data, n_iter, perplexity):
		"""Fit and transform data with t-SNE. In this case, metric is precomputed and the cosine distance should 
		be used instead of the default Euclidean distance.

		Args:
			data (array): The high dimensional array to use.
			n_iter (int): Maximum number of iterations for the optimization.
			perplexity (int): Parameter related to the number of nearest neighbors.

		Return:
			A 2-D representation of data.
			
		TODO:
			* Add more hyperparameters. 

		"""
		tsne = TSNE(n_components=2, random_state=0, verbose=1, n_iter=n_iter, perplexity=perplexity, metric='precomputed')
		return tsne.fit_transform(data)

	def word_vectors_in_space(self, words, t_sne):
	    """Plot t-SNE on a 2-dimensional space.
	    
	    Args:
	        words (list, str): The label of each vector.
	        t_sne (list, float): The transformed space that occured after t-SNE.

	    """
	    
	    # Scatterplot of word vectors
	    trace0= go.Scatter(
	        x= t_sne[:, 0],
	        y= t_sne[:, 1],
	        mode= 'markers',
	        name= 'words',
	        text= words,
	        marker = dict(
	            size = 7,
	            color = 'rgba(20, 150, 180, .8)'))
	    
	    # Graph's layout
	    layout= go.Layout(
	        title= 't-SNE for word vectors',
	        hovermode= 'closest',
	        xaxis= dict(
	            title= 'Component_1',
	            ticklen= 5,
	            zeroline= False,
	            gridwidth= 2,
	        ),
	        yaxis=dict(
	            title= 'Component_2',
	            ticklen= 5,
	            gridwidth= 2,
	        ),
	        width=1000,
	        height=1000,
	        showlegend=True
	    )


	    fig= go.Figure(data=[trace0], layout=layout)
	    plotly.offline.plot(fig)