#charset=utf-8
import json
import numpy as np
import psycopg2

# File where data is fetched from the database
import data_fetch

def enable_connection():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("I am unable to connect to the database")
    return conn.cursor()


def similarity_func(student_answers, company_answers, company_data, number_similar_companies):
    distances = {}
    for i,company in enumerate(company_answers):
        distances[i] = np.sqrt(sum(pow(a-b,2) for a, b in zip(student_answers, company)))
    distances_sorted = []
    for key, value in sorted(distances.iteritems(), key=lambda kv: kv[1]):
        distances_sorted.append((key, value))
    k = 0
    most_similar_companies = {}
    for i in range(number_similar_companies):
        company_id = distances_sorted[i]
        most_similar_companies[i] = {
            "exhibitor_id": company_data[company_id[0]][0],
            "distance": company_id[1]
        }
    with open('data.json', 'w') as outfile:
        json.dump(most_similar_companies, outfile)
    #print most_similar_companies
    return most_similar_companies

def matching(file_path):
    cur = enable_connection()
    student_data_from_file = {}
    with open(file_path, 'r') as infile:
        student_data_from_file = json.load(infile)
    student_data = format_student_data(cur, student_data_from_file)
    company_answers = data_fetch.get_company_data(cur)
    company_data = data_fetch.get_names_and_ids(cur)
    most_similar_companies = similarity_func(student_data, company_answers, company_data, 5)
    return most_similar_companies


def format_student_data(cur, data):
    student_data = []

    # Get the number of answers for each question
    number_of_answers = data_fetch.get_number_of_answers(cur)

    benefit_answer_indexes = np.zeros(number_of_answers[0], dtype=int)
    for answer in data.get("benefits"):
        # Note that the indexes in the database are not zero indexed.
        benefit_answer_indexes[answer - 1] = 1
    student_data = np.append(student_data, benefit_answer_indexes)

    employment_answer_indexes = np.zeros(number_of_answers[1], dtype=int)
    for answer in data.get("employments"):
        employment_answer_indexes[answer - 1] = 1
    student_data = np.append(student_data,employment_answer_indexes)

    industry_answer_indexes = np.zeros(number_of_answers[2], dtype=int)
    for answer in data.get("industries"):
        industry_answer_indexes[answer - 1] = 1
    student_data = np.append(student_data, industry_answer_indexes)

    value_answer_indexes = np.zeros(number_of_answers[3], dtype=int)
    for answer in data.get("values"):
        value_answer_indexes[answer - 1] = 1
    student_data = np.append(student_data, value_answer_indexes)

    location_answer_indexes = np.zeros(number_of_answers[4], dtype=int)
    for answer in data.get("locations"):
        location_answer_indexes[answer - 1] = 1
    student_data = np.append(student_data, location_answer_indexes)
    return student_data


matching('test.json')