#charset=utf-8
import matplotlib
# Vagrant has no GUI
matplotlib.use('Agg')
import somoclu

import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# In order to read in swedeish alphabet 
import psycopg2

# File where data is fetched from the database
import data_fetch

def enable_connection():
	try:
		conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
	except:
		print("I am unable to connect to the database")
	return conn.cursor()

def similarity_func(new_company_data, companies_data, companies_names, number_similar_companies):
	distances = {}
	for i,company in enumerate(companies_data):
		distances[i] = np.sqrt(sum(pow(a-b,2) for a, b in zip(new_company_data, company)))
	most_similar_companies = {}
	k = 0
	for key, value in sorted(distances.items(), key=lambda kv: kv[1]):
		if( k > number_similar_companies):
			break
		else:
			most_similar_companies[key] = value
		k += 1

	return most_similar_companies

def test_som():

	cur = enable_connection()

	companies_data = data_fetch.get_data(cur)
	companies_names = data_fetch.get_names(cur)
	#print(companies_data.shape)
	#print(companies_data)
	most_similar_companies = similarity_func(companies_data[13], companies_data, companies_names, 5)
	#print(most_similar_companies)
	print(list(most_similar_companies.values()))
	for company_id, company_distance in most_similar_companies.items():
		#print(company_id)
		print(companies_names[int(company_id)])
		print(company_distance)
	#print(companies_names[list(most_similar_companies.keys())])
	# c1 = np.random.rand(50, 3)/5
	# c2 = (0.6, 0.1, 0.05) + np.random.rand(50, 3)/5
	# c3 = (0.4, 0.1, 0.7) + np.random.rand(50, 3)/5
	# data = np.float32(np.concatenate((c1, c2, c3)))
	
	# fig = plt.figure()
	# ax = Axes3D(fig)
	# ax.scatter(data[:, 0], data[:, 1], data[:, 2], c=colors)
	# labels = range(150)

	dim_multiplier = 2
	n_rows, n_columns = companies_data.shape[0] * dim_multiplier, \
					    companies_data.shape[1] * dim_multiplier
	som = somoclu.Somoclu(n_columns, n_rows, maptype="toroid",
                       compactsupport=False)
	colors = ["red"] * 60
	colors.extend(["green"] * 60)
	colors.extend(["blue"] * 61)
	unit_labels = range(181)
	som.train(companies_data, epochs=1)
	som.view_umatrix(bestmatches=True, labels=companies_names)
	activation_map = som.get_surface_state()
	# bestmatchs = som.get_bmus(activation_map)
	# print(activation_map)
	# print(bestmatchs)
	# #print(som.activation_map)
	# som.view_component_planes()
	plt.savefig('pic8.png')
	# plt.close()
	# som.view_similarity_matrix()
	# plt.savefig('pic9.png')
	# plt.close('all')
test_som()