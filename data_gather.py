# charset=utf-8
#!/usr/bin/python2.7
#
# Small script to show PostgreSQL and Pyscopg together
#

import psycopg2

try:
	conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
except:
	print("I am unable to connect to the database")

cur = conn.cursor()

cur.execute("""SELECT * from exhibitors_exhibitor WHERE fair_id = 3""")

rows = cur.fetchall()

for row in rows:
	print(row)

	cur.execute("SELECT exhibitors_catalogueindustry.industry FROM exhibitors_catalogueindustry, exhibitors_exhibitor_catalogue_industries WHERE exhibitors_exhibitor_catalogue_industries.exhibitor_id = " + str(row[0]) + " AND exhibitors_exhibitor_catalogue_industries.catalogueindustry_id = exhibitors_catalogueindustry.id")

	industries = cur.fetchall()

	for industry in industries:
		print('\t' + industry[0])
