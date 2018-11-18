import psycopg2
import numpy as np

# This years fair id
fair_id = "3"
# Number of questions
number_of_questions = 5

# Method for extracting the names of all the exhibitors
def get_names_and_ids(cur):
    # Get all the exhibitor ids of this years fair
    cur.execute("SELECT id FROM public.exhibitors_exhibitor WHERE fair_id = " + fair_id + "ORDER BY id")
    exhibitors_ids = cur.fetchall()

    # Get the names of the exhibitors
    exhibitors = []
    for id in exhibitors_ids:
        cur.execute(" SELECT companies_company.name \
                      FROM companies_company,  exhibitors_exhibitor \
                      WHERE exhibitors_exhibitor.company_id = companies_company.id and exhibitors_exhibitor.id =  "  + str(id[0]))
        exhibitor_name = cur.fetchone()[0]
        exhibitors.append((id[0],exhibitor_name))
    return exhibitors


# Method for extracting the number of answers for each question
def get_number_of_answers(cur):
    # Create a list consisting of all the different number of answers
    number_of_answers_per_question = np.zeros(number_of_questions,dtype=int)

    # Get the number of answers on the question about company benefits
    cur.execute("SELECT count(*) FROM exhibitors_cataloguebenefit")
    number_of_benefits = cur.fetchall()[0][0]
    number_of_answers_per_question[0] = number_of_benefits

    # Get the number of answers on the question about employments
    cur.execute("SELECT count(*) FROM exhibitors_catalogueemployment")
    number_of_employments = cur.fetchall()[0][0]
    number_of_answers_per_question[1] = number_of_employments

    # Get the number of answers on the question about industries
    cur.execute("SELECT count(*) FROM exhibitors_catalogueindustry")
    number_of_industries = cur.fetchall()[0][0]
    number_of_answers_per_question[2] = number_of_industries

    # Get the number of answers on the question about company values
    cur.execute("SELECT count(*) FROM exhibitors_cataloguevalue")
    number_of_values = cur.fetchall()[0][0]
    number_of_answers_per_question[3] = number_of_values

    # Get the number of answers on the question about company location
    cur.execute("SELECT count(*) FROM exhibitors_cataloguelocation")
    number_of_locations = cur.fetchall()[0][0]
    number_of_answers_per_question[4] = number_of_locations

    return number_of_answers_per_question


# Method for extracting all the company answers
def get_company_data(cur):
    # Get all the exhibitor ids of this years fair
    exhibitors = get_names_and_ids(cur)
    exhibitor_ids = []

    for i in range(len(exhibitors)):
        exhibitor_ids.append(exhibitors[i][0])

    # Get the number of exhibitors
    number_of_companies = 182

    # Get the number of answers for each question
    number_of_answers = get_number_of_answers(cur)

    # Get the total number of possible answers for one company
    total_number_of_answers = 0
    for answers in number_of_answers:
        total_number_of_answers += answers

    # Initialize the final matrix (number of companies * number of possible answers)
    company_answers = np.zeros((number_of_companies, total_number_of_answers), dtype=int)

    # Iterate through all companies an mark their answers in their row in the final matrix.
    for i,id in enumerate(exhibitor_ids):
        all_answers = []

        # Get the answers on the question about the company benefits
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguebenefit_id  \
                     FROM exhibitors_exhibitor_catalogue_benefits, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_benefits.exhibitor_id = "  + str(id) +  " \
                     ORDER BY exhibitor_id, cataloguebenefit_id")
        benefit_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        benefit_answer_indexes = np.zeros(number_of_answers[0], dtype=int)
        for answer in benefit_answers:
            # Note that the indexes in the database are not zero indexed.
            benefit_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers, benefit_answer_indexes)

        # Get the answers on the question about employment
        cur.execute("SELECT DISTINCT exhibitor_id, catalogueemployment_id  \
                     FROM exhibitors_exhibitor_catalogue_employments, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_employments.exhibitor_id = "  + str(id) +  " \
                     ORDER BY exhibitor_id, catalogueemployment_id")
        employment_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        employment_answer_indexes = np.zeros(number_of_answers[1], dtype=int)
        for answer in employment_answers:
            employment_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers, employment_answer_indexes)

        # Get the answers on the question about industries
        cur.execute("SELECT DISTINCT exhibitor_id, catalogueindustry_id  \
                     FROM exhibitors_exhibitor_catalogue_industries, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_industries.exhibitor_id = "  + str(id) +  " \
                     ORDER BY exhibitor_id, catalogueindustry_id")
        industry_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        industry_answer_indexes = np.zeros(number_of_answers[2], dtype=int)
        for answer in industry_answers:
            industry_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers, industry_answer_indexes)

        # Get the answers on the question about company values
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguevalue_id  \
                     FROM exhibitors_exhibitor_catalogue_values, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_values.exhibitor_id = "  + str(id) +  " \
                     ORDER BY exhibitor_id, cataloguevalue_id")
        value_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        value_answer_indexes = np.zeros(number_of_answers[3], dtype=int)
        for answer in value_answers:
            value_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers, value_answer_indexes)

        # Get the answers on the question about company locations
        cur.execute("SELECT DISTINCT exhibitor_id, cataloguelocation_id  \
                     FROM exhibitors_exhibitor_catalogue_locations, exhibitors_exhibitor \
                     WHERE exhibitors_exhibitor_catalogue_locations.exhibitor_id = "  + str(id) +  " \
                     ORDER BY exhibitor_id, cataloguelocation_id")
        location_answers = cur.fetchall()

        # Create an array of zeros and for each answer the company has answered, fill in 1 on that index.
        location_answer_indexes = np.zeros(number_of_answers[4], dtype=int)
        for answer in location_answers:
            location_answer_indexes[answer[1] - 1] = 1
        all_answers = np.append(all_answers, location_answer_indexes)

        # All answers contains all the answers for this company (represented as an array of 0 and 1).
        # Add this answer array to the final matrix.
        company_answers[i] = all_answers
    return company_answers


def test_data_fetch(id):
    try:
        conn = psycopg2.connect("dbname='ais_dev' user='ais_dev' host='localhost'")
    except:
        print("Unable to connect to the database")

    cur = conn.cursor()
    comp_data = get_names_and_ids(cur)
    comp_answ = get_company_data(cur)
    for i in range(len(comp_data)):
        if comp_data[i][0] == id:
            print(comp_answ[i])

#test_data_fetch()