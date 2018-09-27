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

    number_checkboxes = 0
    for answer_list in M:
        number_checkboxes += len(answer_list)

    number_companies = len(rows)

    final_matrix = np.zeros((number_companies, number_checkboxes), dtype=int)

    for i,row in enumerate(rows):
        print()
        print(row[0])
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguebenefit_id  \
                     FROM exhibitors_exhibitor_catalogue_benefits, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_benefits.exhibitor_id = "  + str(row[0]) +  " \
                     ORDER BY exhibitor_id, cataloguebenefit_id")
        benefit_checkboxes = cur.fetchall()
        benefit_checkbox_indexes = np.zeros (len(M[0]), dtype=int)
        for checkbox in benefit_checkboxes:
            print(checkbox[1])
            benefit_checkbox_indexes[checkbox[1] - 1] = 1
        print(benefit_checkbox_indexes)
        final_matrix[i][np.where(benefit_checkbox_indexes > 0)[0]] = 1
        print(final_matrix[i])

        # cur.execute("SELECT DISTINCT exhibitor_id, catalogueemployment_id  \
        #              FROM exhibitors_exhibitor_catalogue_employments, exhibitors_exhibitor \
        #              WHERE exhibitors_exhibitor_catalogue_employments.exhibitor_id = "  + str(row[0]) +  " \
        #              ORDER BY exhibitor_id, catalogueemployment_id")
        # employment_checkboxes = cur.fetchall()
        # employment_checkbox_indexes = np.zeros (len(M[1]), dtype=int)
        # for checkbox in employment_checkboxes:
        #     employment_checkbox_indexes[checkbox[1] - 1] = 1
        # final_matrix[i] = np.concatenate((final_matrix[i],employment_checkbox_indexes))
        # print(employment_checkboxes)
        # print(final_matrix[i])

        

        
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