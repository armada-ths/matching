#charset=utf-8
import json
import numpy as np
import psycopg2
import sys

# File where data is fetched from the database
import data_fetch

def enable_connection():
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("I am unable to connect to the database")
    return conn.cursor()


def similarity_func(student_data, company_data, number_similar_companies, doc_id):
    student_yes_indexes = []

    # Get all the answers the student marked
    student_answers = student_data["answers"]
    for i in range(len(student_answers)):
        if student_answers[i] == 1:
            student_yes_indexes.append(i)
    new_student_answers = np.ones(len(student_yes_indexes))

    # Only keep the answer options that the student answered
    new_company_answers = company_data["answers"][:, student_yes_indexes]
    
    # The maximum similarity obtainable is the number of 
    # questions answered + the number of cities entered.
    # The minimum is -1*the number of questions answered
    # minus 1 if the student has picked any cities
    max_points = len(student_yes_indexes)
    min_points = -1*max_points
    # Compare student and companies based on their selected answers
    similarities = {}
    for i,company in enumerate(new_company_answers):
        # Don't measure distance, measure similarity
        # If the student answered yes, the company gets +1 similarity
        # if they also picked yes, and -1 similarity if they didn't
        # We may then normalize it, taking into account the worst
        # possible similarity, and the best possible similarity.
        # The best possible is if the company has answered yes
        # for everything the student checked.
        similarities[i] = sum((1 if a == b else -1 for a, b in zip(new_student_answers, company)))

    # Compare student and companies based on the cities they entered
    # Split the student choices at comma and remove whitespace
    student_cities = [x.strip().lower() for x in student_data["cities"].split(',')]
    student_cities = [x for x in student_cities if x] # We do not accept empty strings    

    if len(student_cities) > 0: # The student actually wrote something
        max_points += len(student_cities)
        min_points -= 1

        for i, company_cities in enumerate(company_data["cities"]):
            # If the company has not answered, they get -1, 
            # since the student clearly has a preference, 
            # and we can't know if the company lives up to it
            if company_cities is None or not company_cities: # None or empty string
                similarities[i] -= 1
            else:
                # Get the number of citites in common
                number_of_matching_cities = sum([1 if city in company_cities.lower() else 0 for city in student_cities])
                if number_of_matching_cities == 0:
                    # The company didn't match a single city, so they get -1
                    similarities[i] -= 1
                else:
                    similarities[i] += number_of_matching_cities
    
    # Sort the similarity scores so we can get the highest ones
    similarities_sorted = []
    for key, value in sorted(similarities.items(), key=lambda kv: kv[1], reverse=True):
        similarities_sorted.append((key, value))
    most_similar_companies = {}
    # Now get the companies with the highest similarities
    # Here we normalize the scores to values between 0 and 1.
    # Currently, the values are between max_points and min_points.
    # The normalization formula is thus:
    # (x - min_points) / (2*max_points + 1)
    for i in range(number_similar_companies):
        company = similarities_sorted[i]
        company_index = company[0]
        exhibitor_id = company_data["info"][company_index][0]

        normalized_similarity = (company[1] - min_points) / (max_points - min_points) 

        most_similar_companies[i] = {
            "exhibitor_id": exhibitor_id,
            "similarity": normalized_similarity
        }
    # Dump the data to file
    with open("/tmp/" + doc_id + "_output.json", "w") as outfile:
        json.dump(most_similar_companies, outfile)
    return most_similar_companies

def matching(doc_id, file_path, fair_id):
    cur = enable_connection()
    with open(file_path, 'r') as infile:
        student_data_from_file = json.load(infile)

    student_data = format_student_data(cur, student_data_from_file)
    company_data = data_fetch.get_company_data(cur, fair_id)

    most_similar_companies = similarity_func(student_data, company_data, 5, doc_id)
    return most_similar_companies


def format_student_data(cur, data):
    answers = []
    # Get the number of answers for each question
    number_of_answers = data_fetch.get_number_of_answers(cur)

    competence_answer_indexes = np.zeros(number_of_answers[0], dtype=int)
    for answer in data.get("competences"):
        competence_answer_indexes[answer - 1] = 1
    answers = np.append(answers, competence_answer_indexes)

    employment_answer_indexes = np.zeros(number_of_answers[1], dtype=int)
    for answer in data.get("employments"):
        employment_answer_indexes[answer - 1] = 1
    answers = np.append(answers,employment_answer_indexes)

    industry_answer_indexes = np.zeros(number_of_answers[2], dtype=int)
    for answer in data.get("industries"):
        industry_answer_indexes[answer - 1] = 1
    answers = np.append(answers, industry_answer_indexes)

    value_answer_indexes = np.zeros(number_of_answers[3], dtype=int)
    for answer in data.get("values"):
        value_answer_indexes[answer - 1] = 1
    answers = np.append(answers, value_answer_indexes)

    location_answer_indexes = np.zeros(number_of_answers[4], dtype=int)
    for answer in data.get("locations"):
        location_answer_indexes[answer - 1] = 1
    answers = np.append(answers, location_answer_indexes)

    student_data = {"answers": answers,
                    "cities": data.get("cities")}

    return student_data

matching(sys.argv[1],sys.argv[2], sys.argv[3])
