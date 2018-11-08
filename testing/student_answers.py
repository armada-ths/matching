import psycopg2
import numpy as np


number_of_questions = 5


# Method for extracting the number of answers for each question
def get_number_of_answers(cur):
    # Create a list consisting of all the different number of answers
    M = np.zeros(number_of_questions,dtype=int)

    #Get the number of answers on the question about company benefits
    cur.execute("SELECT count(*) FROM exhibitors_cataloguebenefit")
    number_of_benefits = cur.fetchall()[0][0]
    M[0] = number_of_benefits

    #Get the number of answers on the question about employments
    cur.execute("SELECT count(*) FROM exhibitors_catalogueemployment")
    number_of_employments = cur.fetchall()[0][0]
    M[1] = number_of_employments

    #Get the number of answers on the question about industries
    cur.execute("SELECT count(*) FROM exhibitors_catalogueindustry")
    number_of_industries = cur.fetchall()[0][0]
    M[2] = number_of_industries

    #Get the number of answers on the question about company values
    cur.execute("SELECT count(*) FROM exhibitors_cataloguevalue")
    number_of_values = cur.fetchall()[0][0]
    M[3] = number_of_values

    #Get the number of answers on the question about company location
    cur.execute("SELECT count(*) FROM exhibitors_cataloguelocation")
    number_of_locations = cur.fetchall()[0][0]
    M[4] = number_of_locations
    return M


# Method for extracting the answers for one student
def get_student_answers(cur):
    #Get the list of number of answers per questions
    M = get_number_of_answers(cur)

    all_answers = []

    # Get the answers on the question about the company benefits
    cur.execute("")
    benefit_answers = cur.fetchall()

    # Create an array of zeros and for each answer the student has answered, fill in 1 on that index.
    benefit_answer_indexes = np.zeros(M[0], dtype=int)
    for answer in benefit_answers:
        # Note that the indexes in the database are not zero indexed.
        benefit_answer_indexes[answer[1] - 1] = 1
    all_answers = np.append(all_answers,benefit_answer_indexes)


    # Get the answers on the question about employment
    cur.execute("")
    employment_answers = cur.fetchall()

    # Create an array of zeros and for each answer the student has answered, fill in 1 on that index.
    employment_answer_indexes = np.zeros(M[1], dtype=int)
    for checkbox in employment_answers:
        employment_answer_indexes[checkbox[1] - 1] = 1
    all_answers = np.append(all_answers,employment_answer_indexes)


    # Get the answers on the question about industries
    cur.execute("")
    industry_answers = cur.fetchall()

    # Create an array of zeros and for each answer the student has answered, fill in 1 on that index.
    industry_answer_indexes = np.zeros(M[2], dtype=int)
    for answer in industry_answers:
        industry_answer_indexes[answer[1] - 1] = 1
    all_answers = np.append(all_answers,industry_answer_indexes)


    # Get the answers on the question about company values
    cur.execute("")
    value_answers = cur.fetchall()

    # Create an array of zeros and for each answer the student has answered, fill in 1 on that index.
    value_answer_indexes = np.zeros(M[3], dtype=int)
    for answer in value_answers:
        value_answer_indexes[answer[1] - 1] = 1
    all_answers = np.append(all_answers,value_answer_indexes)


    # Get the answers on the question about company locations
    cur.execute("")
    location_answers = cur.fetchall()

    # Create an array of zeros and for each answer the student has answered, fill in 1 on that index.
    location_answer_indexes = np.zeros(M[4], dtype=int)
    for answer in location_answers:
        location_answer_indexes[answer[1] - 1] = 1
    all_answers = np.append(all_answers,location_answer_indexes)
    print all_answers



def test():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("Unable to connect to the database")

    cur = conn.cursor()
    get_student_answers(cur)


test()
