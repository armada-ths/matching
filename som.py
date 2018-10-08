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

	c1 = np.random.rand(50, 3)/5
	c2 = (0.6, 0.1, 0.05) + np.random.rand(50, 3)/5
	c3 = (0.4, 0.1, 0.7) + np.random.rand(50, 3)/5
	data = np.float32(np.concatenate((c1, c2, c3)))
	colors = ["red"] * 50
	colors.extend(["green"] * 50)
	colors.extend(["blue"] * 50)
	fig = plt.figure()
	ax = Axes3D(fig)
	ax.scatter(data[:, 0], data[:, 1], data[:, 2], c=colors)
	labels = range(150)
	n_rows, n_columns = 100, 160
	som = somoclu.Somoclu(n_columns, n_rows, maptype="toroid",
                      compactsupport=False)
	som.train(data)
	som.view_component_planes()
	plt.savefig('foo.png')
	#som.view_component_planes()

test_som()