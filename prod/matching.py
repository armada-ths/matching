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
    similarities = {}
    # All the categories except cities, since we treat that differently
    categories = ["competences", "industries", "employments", "values", "locations"]
    weight_sum = 0

    for category in categories:
        # Add the weight for this category to the total weight for later normalization
        weight_sum += student_data["weights"][category]

        student_yes_indexes = []
        # Get all the answers the student marked
        student_answers = student_data[category]
        for i in range(len(student_answers)):
            if student_answers[i] == 1:
                student_yes_indexes.append(i)
        new_student_answers = np.ones(len(student_yes_indexes))
        # The maximum similarity obtainable is the number of 
        # questions answered + the number of cities entered.
        # The minimum is -1*the number of questions answered
        # minus 1 if the student has picked any cities
        max_points = len(student_yes_indexes)
        min_points = -1*max_points
        
        # To check if the student actually answered with something
        answer_given = (len(new_student_answers) != 0)

        similarities[category] = {}
        for i, company_answers in company_data["data"][category].items():
            # If the student answered yes, the company gets +1 similarity
            # if they also picked yes, and -1 similarity if they didn't
            # We may then normalize it, taking into account the worst
            # possible similarity, and the best possible similarity.
            # The best possible is if the company has answered yes
            # for everything the student checked.
          
            if answer_given == 0:
                # No choices made by student, this category will be weighted to 0 
                # either way, so it doesn't really matter but we'll set every company 
                # to a perfect match for this category
                similarities[category][i] = 1
            else:
                # The student did pick something
                # Only keep the answer options that the student answered
                new_company_answers = company_answers[student_yes_indexes]
                value = sum((1 if a == b else -1 for a, b in zip(new_student_answers, new_company_answers)))
                # Normalize
                similarities[category][i] = (value - min_points) / (max_points - min_points)

    # Compare student and companies based on the cities they entered
    # Split the student choices at comma and remove whitespace
    student_cities = [x.strip().lower() for x in student_data["cities"].split(',')]
    student_cities = [x for x in student_cities if x] # We do not accept empty strings    

    city_similarities = {}

    if len(student_cities) > 0: # The student actually wrote something
        max_points = len(student_cities) # The student may get 1 extra point for each city
        min_points = -1 # The student gets at worst -1 if nothing matches

        for i, company_cities in company_data["data"]["cities"].items():
            # If the company has not answered, they get -1, 
            # since the student clearly has a preference, 
            # and we can't know if the company lives up to it
            if company_cities is None or not company_cities: # None or empty string
                city_similarities[i] = -1
            else:
                # Get the number of citites in common
                number_of_matching_cities = sum([1 if city in company_cities.lower() else 0 for city in student_cities])
                if number_of_matching_cities == 0:
                    # The company didn't match a single city, so they get -1
                    city_similarities[i] = -1
                else:
                    city_similarities[i] = number_of_matching_cities
            city_similarities[i] = (city_similarities[i] - min_points) / (max_points - min_points)
    else:
        # If the student provided no answer for cities,
        # it will be weighted to 0 anyways.
        # Since we should return *something*
        # every company is a good match in regards to cities.
        for i in company_data["data"]["cities"].keys():
            city_similarities[i] = 1.0
        
    similarities["cities"] = city_similarities

    # Calculate the total similarity, regardless of category
    # taking into account the normalized weights, we expect
    # the weights to always be present, regardless of user input
    normalized_weights = {}
    for category in categories + ["cities"]:
        normalized_weights[category] = student_data["weights"][category] / weight_sum
    
    similarities["total"] = {}
    for i in company_data["data"][categories[0]].keys(): # All the company indexes
        sum_of_similarities = 0
        for category in categories + ["cities"]:
            # We need to check that we've actually calculated the similarity
            # In the case of cities for instance, we don't calculate the similarity 
            # if the student entered nothing
            if category in similarities: 
                sum_of_similarities += similarities[category][i] * normalized_weights[category]
        
        similarities["total"][i] = sum_of_similarities
    
    # Sort the similarity scores so we can get the highest ones for each category
    # If two values are equal in similarity for a given category,
    # we'll order them after total similarity. The first element of the tuple is 
    # the similarity for the given category, the second is the total similarity.
    sort_key = lambda kv : (kv[1], similarities["total"][kv[0]])

    similarities_sorted = {}
    most_similar_companies = {}
    for category in (categories + ["cities", "total"]):
        similarities_sorted[category] = []
        
        if category in similarities:
            for key, value in sorted(similarities[category].items(), key=sort_key, reverse=True):
                similarities_sorted[category].append((key, value))
            
            # Now get the companies with the highest similarities
            most_similar_companies[category] = []
            for i in range(number_similar_companies):
                company = similarities_sorted[category][i]
                company_index = company[0]
                exhibitor_id = company_data["info"][company_index][0]
 
                similarity = company[1]

                most_similar_companies[category].append(
                    {
                        "exhibitor_id": exhibitor_id,
                        "similarity": similarity
                    }
                )
    # Dump the data to file
    with open("/tmp/" + doc_id + "_output.json", "w") as outfile:
        json.dump(most_similar_companies, outfile)
    return most_similar_companies

def matching(doc_id, file_path, fair_id):
    cur = enable_connection()
    with open(file_path, 'r') as infile:
        student_data_from_file = json.load(infile)

    student_data = format_student_data(cur, student_data_from_file)
    response_size = get_response_size(student_data_from_file)
    company_data = data_fetch.get_company_data(cur, fair_id)

    most_similar_companies = similarity_func(student_data, company_data, response_size, doc_id)
    return most_similar_companies

def get_response_size(data):
    if "response_size" in data:
        return data["response_size"]
    else:
        return 4 # Default


def format_student_data(cur, data):

    # Get the number of answers for each question
    number_of_answers = data_fetch.get_number_of_answers(cur)

    competence_answer_indexes = np.zeros(number_of_answers[0], dtype=int)
    for answer in data["competences"]["answer"]:
        competence_answer_indexes[answer - 1] = 1

    employment_answer_indexes = np.zeros(number_of_answers[1], dtype=int)
    for answer in data["employments"]["answer"]:
        employment_answer_indexes[answer - 1] = 1

    industry_answer_indexes = np.zeros(number_of_answers[2], dtype=int)
    for answer in data["industries"]["answer"]:
        industry_answer_indexes[answer - 1] = 1

    value_answer_indexes = np.zeros(number_of_answers[3], dtype=int)
    for answer in data["values"]["answer"]:
        value_answer_indexes[answer - 1] = 1

    location_answer_indexes = np.zeros(number_of_answers[4], dtype=int)
    for answer in data["locations"]["answer"]:
        location_answer_indexes[answer - 1] = 1

    weights = {}
    for category in ["competences", "employments", "industries", "values", "locations", "cities"]:
        answer = data[category]["answer"]
        if (isinstance(answer, list) and len(answer) > 0) or (isinstance(answer, str) and answer != ""):
            weights[category] = data[category]["weight"]
        else:
            weights[category] = 0

    student_data = {"competences": competence_answer_indexes,
                    "employments": employment_answer_indexes,
                    "industries": industry_answer_indexes,
                    "values": value_answer_indexes,
                    "locations": location_answer_indexes,
                    "cities": data["cities"]["answer"],
                    "weights": weights
    }

    return student_data

matching(sys.argv[1],sys.argv[2], sys.argv[3])
