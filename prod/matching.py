#charset=utf-8
import json
import numpy as np
import psycopg2
from math import*

# File where data is fetched from the database
import data_fetch

def enable_connection():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("I am unable to connect to the database")
    return conn.cursor()

def euclidean(student_answers, company):
    return np.sqrt(sum(pow(a-b,2) for a, b in zip(student_answers, company)))

def manhattan_distance(student_answers,company):
    return sum(abs(a-b) for a,b in zip(student_answers,company))
    
def square_rooted(x, rounded):
    return round(sqrt(sum([a*a for a in x])),rounded)
 
def cosine_similarity(student_answers,company):
    rounded= 15
    numerator = sum(a*b for a,b in zip(student_answers,company))
    denominator = square_rooted(student_answers,rounded)*square_rooted(company, rounded)
    return round(numerator/float(denominator),rounded)

def similarity_func(student_answers, company_answers, company_data, number_similar_companies):
    
    distances = {}
    distance_cosine=np.zeros(len(company_answers), dtype=float)
    distance_euclidean=np.zeros(len(company_answers), dtype=float)

    # Eps is needed in case the max value is == 0 
    #   which implies invalid division and that 
    #   may happen in case of a exact match between
    #   company and the student
    eps = 0.0000000001
    for i,company in enumerate(company_answers):
        distance_cosine[i] = cosine_similarity(student_answers + eps, company + eps)
        distance_euclidean[i] = euclidean(student_answers + eps, company + eps)
    
    # Normalize the vectors in order to be able
    #   to sum them and get the final distance measure
    normalized_distance_cosine = distance_cosine/ max(distance_cosine)
    normalized_distance_euclidean = distance_euclidean/ max(distance_euclidean)
    for i,company in enumerate(company_answers):
        distances[i] = normalized_distance_cosine[i] + normalized_distance_euclidean[i]

    distances_sorted = []
    for key, value in sorted(distances.iteritems(), key=lambda kv: kv[1]):
        distances_sorted.append((key, value))

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