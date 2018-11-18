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
    student_yes_indexes = []

    # Get all the answers the student marked
    for i in range(len(student_answers)):
        if student_answers[i] == 1:
            student_yes_indexes.append(i)
    new_student_answers = np.ones(len(student_yes_indexes))

    # Only keep the answer options that the student answered
    new_company_answers = company_answers[:, student_yes_indexes]

    distances = {}
    for i,company in enumerate(new_company_answers):
        # If a company has not answered, set the distance to a high value
        if np.all(company == 0):
            distances[i] = 100000
        else:
            distances[i] = np.sqrt(sum(pow(a-b,2) for a, b in zip(new_student_answers, company)))

    distances_sorted = []
    for key, value in sorted(distances.items(), key=lambda kv: kv[1]):
        distances_sorted.append((key, value))
    most_similar_companies = {}
    for i in range(number_similar_companies):
        company = distances_sorted[i]
        company_id = company[0]
        exhibitor_id = company_data[company_id][0]
        #data_fetch.test_data_fetch(exhibitor_id)
        most_similar_companies[i] = {
            "exhibitor_id": exhibitor_id,
            "distance": company[1]
        }
    with open('data.json', 'w') as outfile:
        json.dump(most_similar_companies, outfile)
    return most_similar_companies

def matching(file_path):
    cur = enable_connection()
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