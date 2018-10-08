import matplotlib
# Vagrant has no GUI
matplotlib.use('Agg')
import somoclu
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import psycopg2


# File where data is fetched from the database
import data_fetch

def enable_connection():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("I am unable to connect to the database")

    return conn.cursor()


def test_som():

	cur = enable_connection()

	companies_data = data_fetch.get_data(cur)
	print(companies_data.shape)

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
	som.train(companies_data, epochs=10, radius0=10, scale0=0.02)
	som.view_umatrix(bestmatches=True, labels=unit_labels)
	# som.view_component_planes()
	plt.savefig('pic3.png')
	#som.view_component_planes()
test_som()