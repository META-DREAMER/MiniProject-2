"""
November 22th, 2015
Phase 3 Program
Authors: Hammad Jutt, J Maxwell Douglas

This program interprets queries from the user and retrieves reviews matching the queries from the index
files created in phase 2.
"""

import re
import sys
from bsddb3 import db
import csv
import time
import datetime

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

RT_IDX = "indexes/rt.idx"
PT_IDX = "indexes/pt.idx"
RW_IDX = "indexes/rw.idx"
SC_IDX = "indexes/sc.idx"
REVIEW_FIELDS = ["Product ID", "Title", "Price", "User ID", "Name", "Helpfulness", "Rating", "Date", "Summary", "Review"]



def getTerms(input):
    """
    Parses input from the user, removes any whitespace around '<', '>' and ':' characters and returns a list of terms.
    Used to prepare user input for the getReviews() function.
    :param input: String to extract terms from.
    :return List of terms after parsing.
    """
    input = re.sub("\\s*>\\s*", ">", input)
    input = re.sub("\\s*<\\s*", "<", input)
    input = re.sub("\\s*:\\s*", ":", input)
    return input.split()



def getExact(terms, index):
    """
    Matches review numbers with the given textual query. Partial match allowed with '%' wildcard at
    end of term.

    :param terms: List of terms to search for
    :param index: path to index file to search in
    :return Set of review numbers matching the given terms
    """
    database = db.DB()
    database.open(index)
    cur = database.cursor()
    result = []

    for term in terms:
        exact = not term[-1] == '%'
        if not exact:
            term = term[:-1]
        itr = cur.get(term, db.DB_SET_RANGE)
        while itr:
            if (not exact and not itr[0].startswith(term)):
                break
            if exact and itr[0] != term:
                break
            result.append(itr[1])
            itr=cur.get(term, db.DB_NEXT)

    cur.close()
    database.close()

    return set(result)

def getRange(terms, index):
    """
    Searches a given index file for matches on terms given.

    :param terms: List of terms in the format [>/<]NUMBER
    :param index: Path to the index file to search
    :return: subset of the given reviews that match the given terms
    """
    database = db.DB()
    database.open(index)
    cur = database.cursor()
    result = []

    for term in terms:
        value = float(term[1:])
        itr = cur.first()
        while itr:
            if (term[0] == '>' and float(itr[0]) > value):
                result.append(itr[1])
            elif (term[0] == '<' and float(itr[0]) < value):
                result.append(itr[1])
            itr=cur.next()

    cur.close()
    database.close()
    return set(result)

def filterPrices(reviews, terms):
    """
    Filters a list of reviews by price.

    :param reviews: List of reviews to filter
    :param terms: List of prices in the format [>/<]NUMBER
    :return: subset of the given reviews that match the given terms
    """
    result = []

    for review in reviews:
        try:
            price = float(review["Price"])
        except ValueError:
            continue
        valid = False
        for term in terms:
            filter = float(term[1:])
            if (term[0] == '>' and price > filter):
                valid = True
            elif (term[0] == '<' and price < filter):
                valid = True
            else:
                valid = False

        if valid:
            result.append(review)

    return result

def filterDates(reviews, terms):
    """
    Filters a list of reviews by date.
    :param reviews: List of reviews to filter
    :param terms: List of terms in the format [>/<]YYYY/MM/DD
    :return: subset of the given reviews that match the given terms
    """
    result = []
    for review in reviews:
        date = float(review["Date"])
        valid = False
        for term in terms:
            filter = time.mktime(datetime.datetime.strptime(term[1:], "%Y/%m/%d").timetuple())
            if (term[0] == '>' and date > filter):
                valid = True
            elif (term[0] == '<' and date < filter):
                valid = True
            else:
                valid = False

        if valid:
            result.append(review)

    return result


def getReviews(terms):
    """
    Retrieves all reviews that matches all the given terms.
    Terms can in any of the following formats:
        - p:word
        - r:word
        - word
        - rscore >/< number
        - rdate >/< YYYY/MM/DD
        - pprice >/< number
    :param terms: list of terms
    :return list of reviews as dictionaries matching all the given terms
    """

    pTerms, rTerms, rscoreTerms, ppriceTerms, rdateTerms, otherTerms = ([] for i in range(6))

    for term in terms:
        if term.startswith("p:"):
            pTerms.append(term[2:])
        elif term.startswith("r:"):
            rTerms.append(term[2:])
        elif term.startswith("rscore"):
            rscoreTerms.append(term[6:])
        elif term.startswith("pprice"):
            ppriceTerms.append(term[6:])
        elif term.startswith("rdate"):
            rdateTerms.append(term[5:])
        else:
            otherTerms.append(term)

    results = []

    if otherTerms:
        results.append(getExact(otherTerms, PT_IDX).union(getExact(otherTerms, RT_IDX)))
    if pTerms:
        results.append(getExact(pTerms, PT_IDX))
    if rTerms:
        results.append(getExact(rTerms, RT_IDX))
    if rscoreTerms:
        try:
            results.append(getRange(rscoreTerms, SC_IDX))
        except ValueError:
            print("Invalid value specified for range operator.")
            return None

    if not results:
        print("Invalid query. Please specify a term to search for.")
        return None

    reviews = getReviewData(set.intersection(*results))

    if ppriceTerms:
        reviews = filterPrices(reviews, ppriceTerms)
    if rdateTerms:
        try:
            reviews = filterDates(reviews, rdateTerms)
        except ValueError:
            print("Invalid date format specified. Should be YYYY/MM/DD.")
            return None

    if not reviews:
        print("No reviews found")
    return reviews


def getReviewData(reviewNums):
    """
    Takes a list of review numbers and retrieves their data.

    Returns a list of the reviews as dictionaries with the fields
    in the REVIEW_FIELDS variable at the top of the file.

    :param reviewNums list of review numbers to retrieve data for
    :return list of review dictionaries
    """
    database = db.DB()
    database.open(RW_IDX)


    reviews = csv.DictReader([database.get(r) for r in reviewNums],
                          fieldnames=REVIEW_FIELDS,
                          skipinitialspace=True)
    database.close()
    return [review for review in reviews]


def printReviews(reviews):
    """
    Takes in a list of reviews and formats and prints them in a readable format.
    ANSI color codes are used and each line is capped at 15 words to make the reviews easier to read .

    :param reviews: List of review dictionaries with the fieldnames:
    Product ID, Title, Price, User ID, Name, Helpfulness, Rating, Date, Summary, and Review
    """

    quoteChar = "&quot;"
    fieldnames=REVIEW_FIELDS
    outputFormat = color.HEADER+'%s: '+color.ENDC+'%s'

    for review in reviews:
        print(color.OKBLUE + "\n----------REVIEW----------" + color.ENDC)

        review["Date"] = datetime.datetime.fromtimestamp(int(review["Date"])).strftime('%Y/%m/%d')
        for field in [outputFormat % (f, re.sub(quoteChar, '"', review[f])) for f in fieldnames]:
            print re.sub("((\S+\\s+){15})", "\\1\n", field, 0, re.DOTALL)



if __name__ == '__main__':


    print(color.OKBLUE + "\n----------Amazon Review Database----------" + color.ENDC)
    while True:
        input = raw_input(color.WARNING+"\nPlease enter a query or 'exit()' to quit: " + color.ENDC).lower()
        if input == "exit()":
            sys.exit()

        terms = getTerms(input)

        reviews = getReviews(terms)

        if reviews:
            printReviews(reviews)
