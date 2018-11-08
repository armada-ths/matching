# charset=utf-8
#!/usr/bin/python2.7
#
# Small script to show PostgreSQL and Pyscopg together
#

import psycopg2
import numpy as np
import matplotlib.pyplot as plt

try:
	conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
except:
	print("I am unable to connect to the database")

cur = conn.cursor()

cur.execute("""SELECT * from exhibitors_exhibitor WHERE fair_id = 3""")

rows = cur.fetchall()

count_checks = 0
checks_per_company = []
for i, row in enumerate(rows):
	#print(i)
	#print(row)

	cur.execute("SELECT exhibitors_catalogueindustry.industry FROM exhibitors_catalogueindustry, exhibitors_exhibitor_catalogue_industries WHERE exhibitors_exhibitor_catalogue_industries.exhibitor_id = " + str(row[0]) + " AND exhibitors_exhibitor_catalogue_industries.catalogueindustry_id = exhibitors_catalogueindustry.id")

	industries = cur.fetchall()
	
	
	if(len(industries) == 0):
		checks_per_company.append(0)
	else:
		checks_per_company.append(len(industries))
		count_checks = count_checks + 1

#	for industry in industries:
#		
#		print('\t' + industry[0])

	

print(" First length ", len(np.arange(i+1)), "Second length", len(checks_per_company) )
mean_checks = np.mean(checks_per_company[np.where(np.array(checks_per_company) > 0)[0][0]])
print(mean_checks)
plt.plot([0, len(checks_per_company)], [mean_checks, mean_checks], 'k-', lw=2)
plt.plot(np.arange(i+1),checks_per_company, 'bo')
plt.xlabel("Company id")
plt.ylabel("Number of checked boxes")
plt.title(" ")
plt.savefig("new_figure.png")
print(" Percent of companies that inquired data", float(count_checks / i) * 100)