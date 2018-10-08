# charset=utf-8
#!/usr/bin/python2.7
#
# Small script to show PostgreSQL and Pyscopg together
#

import psycopg2
import numpy as np


fair_id = "3"



def get_arrays(cur):
    # Create the matrix M in which all questions by all companies will be stored.
    # M will consist of (number of companies * number of answers per question)
    # M is really a list of lists since all questions have different number of answers.
    M = np.zeros(5,dtype=object)


    #Get the number of answers on the question about company benefits
    cur.execute("SELECT count(*) FROM exhibitors_cataloguebenefit")
    number_of_benefits = cur.fetchall()[0][0]
    benefit_array = np.zeros(number_of_benefits, dtype=int)
    M[0] = benefit_array

    #Get the number of answers on the question about employments
    cur.execute("SELECT count(*) FROM exhibitors_catalogueemployment")
    number_of_employments = cur.fetchall()[0][0]
    employment_array = np.zeros(number_of_employments, dtype=int)
    M[1] = employment_array

    #Get the number of answers on the question about industries
    cur.execute("SELECT count(*) FROM exhibitors_catalogueindustry")
    number_of_industries = cur.fetchall()[0][0]
    industries_array = np.zeros(number_of_industries, dtype=int)
    M[2] = industries_array

    #Get the number of answers on the question about company values
    cur.execute("SELECT count(*) FROM exhibitors_cataloguevalue")
    number_of_values = cur.fetchall()[0][0]
    values_array = np.zeros(number_of_values, dtype=int)
    M[3] = values_array

    #Get the number of answers on the question about company location
    cur.execute("SELECT count(*) FROM exhibitors_cataloguelocation")
    number_of_locations = cur.fetchall()[0][0]
    locations_array = np.zeros(number_of_locations, dtype=int)
    M[4] = locations_array

    return M






def get_data(cur):

    # Get all the exhibitor ids of this years fair
    cur.execute("SELECT * FROM exhibitors_exhibitor WHERE fair_id = " + fair_id)
    exhibitor_ids = cur.fetchall()
    M = get_arrays(cur)

    # Get the number of exhibitors
    number_of_companies = len(exhibitor_ids)

    # Get the total number of possible answers for one company
    number_of_answers = 0
    for answer_list in M:
        number_of_answers += len(answer_list)


    # Initialize the final matrix (number of companies * number of possible answers)
    companies_data = np.zeros((number_of_companies, number_of_answers), dtype=int)

    # Iterate through all companies an mark their answers in their row in the final matrix.
    for i,id in enumerate(exhibitor_ids):
        all_answers = []

        # Get the answers on the question about the company benefits
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguebenefit_id  \
                     FROM exhibitors_exhibitor_catalogue_benefits, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_benefits.exhibitor_id = "  + str(id[0]) +  " \
                     ORDER BY exhibitor_id, cataloguebenefit_id")
        benefit_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        benefit_answer_indexes = np.zeros(len(M[0]), dtype=int)
        for answer in benefit_answers:
            # Note that the indexes in the database are not zero indexed.
            benefit_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers,benefit_answer_indexes)


        # Get the answers on the question about employment
        cur.execute("SELECT DISTINCT exhibitor_id, catalogueemployment_id  \
                     FROM exhibitors_exhibitor_catalogue_employments, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_employments.exhibitor_id = "  + str(id[0]) +  " \
                     ORDER BY exhibitor_id, catalogueemployment_id")
        employment_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        employment_answer_indexes = np.zeros(len(M[1]), dtype=int)
        for checkbox in employment_answers:
            employment_answer_indexes[checkbox[1] - 1] = 1
        all_answers = np.append(all_answers,employment_answer_indexes)


        # Get the answers on the question about industries
        cur.execute("SELECT DISTINCT exhibitor_id, catalogueindustry_id  \
                     FROM exhibitors_exhibitor_catalogue_industries, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_industries.exhibitor_id = "  + str(id[0]) +  " \
                     ORDER BY exhibitor_id, catalogueindustry_id")
        industry_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        industry_answer_indexes = np.zeros(len(M[2]), dtype=int)
        for answer in industry_answers:
            industry_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers,industry_answer_indexes)




        # Get the answers on the question about company values
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguevalue_id  \
                     FROM exhibitors_exhibitor_catalogue_values, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_values.exhibitor_id = "  + str(id[0]) +  " \
                     ORDER BY exhibitor_id, cataloguevalue_id")
        value_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        value_answer_indexes = np.zeros(len(M[3]), dtype=int)
        for answer in value_answers:
            value_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers,value_answer_indexes)



        # Get the answers on the question about company locations
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguelocation_id  \
                     FROM exhibitors_exhibitor_catalogue_locations, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_locations.exhibitor_id = "  + str(id[0]) +  " \
                     ORDER BY exhibitor_id, cataloguelocation_id")
        location_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        location_answer_indexes = np.zeros(len(M[4]), dtype=int)
        for answer in location_answers:
            location_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers,location_answer_indexes)

        # All answers contains all the answers for this company (represented as an array of 0 and 1).
        # Add this answer array to the final matrix.
        companies_data[i] = all_answers


        # To check what companies has not responded yet, run this below and replace X with ex id
        # SELECT companies_company.name, exhibitors_exhibitor.id
        # FROM companies_company,  exhibitors_exhibitor
        # WHERE exhibitors_exhibitor.company_id = companies_company.id and exhibitors_exhibitor.id = X
        # ORDER BY exhibitors_exhibitor.id desc
        #if np.all(all_answers==0):
        #    print "Company with exhibitor id: " + str(id[0]) + " has not responded yet"

        #print (companies_data[i])


        # MAYBE REMOVE THIS? Too many without answers on these two
        # Get the average age and year founded
        # cur.execute("SELECT catalogue_average_age, catalogue_founded
        #              FROM exhibitors_exhibitor
        #              WHERE id = "  + str(id[0]))
        # average_age_and_year = cur.fetchall()
        # print average_age_and_year







def test_data_fetch():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    get_data(cur)


#test_data_fetch()