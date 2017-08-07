import numpy as np
import sklearn
from sklearn import mixture
import matplotlib.pyplot as plt
from sklearn import metrics
import itertools
import pickle

class GaussianMixtureEvaluation():
	def __init__(self, data):
		self.data = data

	def bic_gmm(self):
		"""Evaluate GMM through BIC and keep the best model.
		
		Args:
			data (array): 2D space produced by t-SNE.
			
		Return:
			best_gmm: GMM with the lowest BIC.
			bic (array): The BIC values for the various GMMs that were produced.
			
		"""
		lowest_bic = np.infty
		bic = []
		n_components_range = range(1, 50)
		cv_types = ['spherical', 'tied', 'diag', 'full']
		for cv_type in cv_types:
			for n_components in n_components_range:
				# Fit a Gaussian mixture model
				gmm = mixture.GaussianMixture(n_components=n_components,
											  covariance_type=cv_type)
				gmm.fit(self.data)
				bic.append(gmm.bic(self.data))
				if bic[-1] < lowest_bic:
					lowest_bic = bic[-1]
					best_gmm = gmm
					
		bic = np.array(bic)
		return best_gmm, bic

	def calculate_silhouette_scores(self, covariance_type):
		"""Calculate the silhouette score for the different number of components used in GMM.
		
		Args:
			data (array): 2D space produced by t-SNE.      
		
		Return:
			scores (list, float): Silhouette scores for the different number of components.

		TODO:
			* Add covariance type in the custom grid search.
			
		"""
		scores = [0]
		for i in range(10, 90):
			gaussian = sklearn.mixture.GaussianMixture(n_components=i, covariance_type=covariance_type)
			gmm = gaussian.fit(self.data)
			label = gmm.predict(self.data)
			sil_score = metrics.silhouette_score(self.data, label)
			
			# print(sil_score)
			# print(sil_score, scores[0])
			if np.max(scores) < sil_score:
				best_gmm = gmm
			scores.append(sil_score)

		return best_gmm, scores

class VisualiseEvaluationGMM():
	def __init__(self, gmm):
		self.gmm = gmm

	def bic_plot(self, scores):
		"""Create a BIC plot for the GMM.
		
		Args:
			clf: The fitted GMM model.
		"""
		n_components_range = range(1, 50)
		cv_types = ['spherical', 'tied', 'diag', 'full']

		color_iter = itertools.cycle(['navy', 'turquoise', 'cornflowerblue',
									  'darkorange'])
		bars = []

		# Plot the scores scores
		plt.figure(figsize=(15,8))
		for i, (cv_type, color) in enumerate(zip(cv_types, color_iter)):
			xpos = np.array(n_components_range) + .2 * (i - 2)
			bars.append(plt.bar(xpos, scores[i * len(n_components_range):
										  (i + 1) * len(n_components_range)],
								width=.2, color=color))

		plt.xticks(n_components_range)
		plt.ylim([scores.min() * 1.01 - .01 * scores.max(), scores.max()])
		plt.title('scores per model')
		xpos = np.mod(scores.argmin(), len(n_components_range)) + .65 +\
			.2 * np.floor(scores.argmin() / len(n_components_range))
		plt.text(xpos, scores.min() * 0.97 + .05 * scores.max(), '*', fontsize=14)
		plt.xlabel('Number of components')
		plt.legend([b[0] for b in bars], cv_types)
		plt.show()

	def silhouette_plot(self, scores):
		"""Plot the silhouette scores.
		
		Args:
			silhouette_scores (list, float): The silhouette scores for the different number of components used in GMM.
		
		"""
		plt.plot(scores)
		plt.xlabel('Model number')
		plt.ylabel('Silhouette score')
		plt.title('Silhouette score for GMM on t-SNE 2D space')
		plt.show()

if __name__ == '__main__':
	with open('data/word2vec/tsne_space.pickle', 'rb') as h:
		tsne_space = pickle.load(h)

	with open('data/word2vec/tokens.pickle', 'rb') as h:
		tokens = pickle.load(h)    

	gmm_eval = GaussianMixtureEvaluation(tsne_space)
	best_gmm, bic = gmm_eval.bic_gmm()

	print('BEST GMM MODEL: {}'.format(best_gmm))
	gmm_vis = VisualiseEvaluationGMM(best_gmm)

	# Do the same for silhouette scores
	# m, scores = gmm_eval.calculate_silhouette_scores('diag')

	# gmm_vis = VisualiseEvaluationGMM(m)
	gmm_vis.bic_plot(bic)

	token_labels = best_gmm.predict(tsne_space)
	clustered_tokens = [tuple((tokens[i], token_labels[i])) for i in range(len(tokens))]

	with open('data/word2vec/clustered_tokens.pickle', 'wb') as h:
		pickle.dump(clustered_tokens, h)

	with open('data/word2vec/gmm_clf.pickle', 'wb') as h:
		pickle.dump(best_gmm, h)
