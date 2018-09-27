# charset=utf-8
#!/usr/bin/python2.7
#
# Small script to show PostgreSQL and Pyscopg together
#

import psycopg2
import numpy as np



def get_arrays(cur):
    M = np.zeros(5,dtype=object)

    cur.execute("SELECT count(*) FROM public.exhibitors_cataloguebenefit")
    number_of_benefits = cur.fetchall()[0][0]
    benefit_array = np.zeros(number_of_benefits, dtype=int)
    M[0] = benefit_array

    cur.execute("SELECT count(*) FROM public.exhibitors_catalogueemployment")
    number_of_employments = cur.fetchall()[0][0]
    employment_array = np.zeros(number_of_employments, dtype=int)
    M[1] = employment_array

    cur.execute("SELECT count(*) FROM public.exhibitors_catalogueindustry")
    number_of_industries = cur.fetchall()[0][0]
    industries_array = np.zeros(number_of_industries, dtype=int)
    M[2] = industries_array

    cur.execute("SELECT count(*) FROM public.exhibitors_cataloguevalue")
    number_of_values = cur.fetchall()[0][0]
    values_array = np.zeros(number_of_values, dtype=int)
    M[3] = values_array

    cur.execute("SELECT count(*) FROM public.exhibitors_cataloguelocation")
    number_of_locations = cur.fetchall()[0][0]
    locations_array = np.zeros(number_of_locations, dtype=int)
    M[4] = locations_array

    return M





def get_data(cur, M):
    cur.execute("SELECT * FROM exhibitors_exhibitor WHERE fair_id = 3")
    rows = cur.fetchall()

    for row in rows:
        print("Company: " + str(row[0]))






def main():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    M = get_arrays(cur)
    get_data(cur, M)


main()