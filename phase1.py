'''
November 24th, 2015
Phase 1 Program
Authors: Hammad Jutt, J Maxwell Douglas

This program outputs four different files given an input file.
The titles of the four output files are:
reviews.txt, pterms.txt, rterms.txt, and scores.txt
They are abbreviated as w, x, y, and z respectively as seen a few
lines below.

The global data structure seen below is an array called inputfile. All the
necessary functions in this program make use of this array. It is made by the
open_file function and is simply composed of the separated lines of the input
file.
'''
import sys
import os

inputfile = []
if not os.path.exists("data"):
    os.makedirs("data")

w = open('data/reviews.txt', 'w')
x = open('data/pterms.txt', 'w')
y = open('data/rterms.txt', 'w')
z = open('data/scores.txt', 'w')

'''
Description of Functions:

open_file: This function opens the input files and makes the inputfile array
which contains each line of the input file.

parselines: This function parses the input file appropriately for the function
'print_reviews'.

print_reviews: This function assembles the text for the file reviews.txt.

print_pterms: This function assembles the text for the file pterms.txt.

alphanumeric_iter: This function iterates over individual words as strings
and counts the number of consecutive alphanumeric characters including the
underscore. It then appends them to an array and returns it to the function who
it. The two functions 'print_pterms:' and 'print_rterms:' make use of this tool.

print_rterms: This function assembles the text for the file rterms.txt.

print_scores: This function assembles the text for the file rterms.txt.
'''

def open_file():
    f = open(sys.argv[1])
    for line in f:
        inputfile.append(line)

def parse_lines():
    reviewsarray = []
    for line in inputfile:
        cur_line = ''
        for i in line:
            if i == '\\':
                cur_line += "\\"
            if i == '"':
                cur_line += "&quot;"
            else:
                cur_line += i
        reviewsarray.append(cur_line)

    print_reviews(reviewsarray)

def print_reviews(reviewsarray):
    reviewprint = []
    reviewnum = 1
    q = ""
    a = ["product/title:", "review/profileName:", "review/summary:", "review/text:"]
    for i in reviewsarray:
        if i == '\n':
            q = str(reviewnum)+','+q[:-1] + '\n'
            reviewprint.append(q)
            q = ""
            reviewnum += 1
        else:
            s = i.split()
            if s[0] in a:
                s = s[1:]
                t = ' '
                t = '"' + t.join(s) + '",'
                q += t
            else:
                s = s[1:]
                t = ' '
                t = t.join(s) + ','
                q += t

    for i in reviewprint:
        w.write(i)

def print_pterms():
    reviewnum = 0
    pterms = []
    for i in inputfile:
        s = i.split(' ')
        if len(s) == 0:
            pass
        elif s[0] == "product/title:":
            reviewnum += 1
            s = s[1:]
            for j in s:
                tba = alphanumeric_iter(j, reviewnum, pterms)
    for i in pterms:
        x.write(i)

def print_rterms():
    reviewnum = 0
    rterms = []
    a = ["review/summary:", "review/text:"]
    for i in inputfile:
        s = i.split(' ')
        if len(s) == 0:
            pass
        elif s[0] in a:
            if s[0] == "review/summary:":
                reviewnum += 1
            s = s[1:]
            for j in s:
                tba = alphanumeric_iter(j, reviewnum, rterms)
    for i in rterms:
        y.write(i)

def alphanumeric_iter(word, reviewnum, xterms):
    check = True
    count = 0
    each_word = ''
    for letter in word:
        if letter.isalnum() or letter == '_':
            each_word += letter
            count += 1
        else:
            if count > 2:
                q = ''
                q = each_word+','+str(reviewnum)+'\n'
                q = q.lower()
                xterms.append(q)
                each_word = ''
                count = 0
            else:
                each_word = ''
                count = 0
    if count > 2:
        q = ''
        q = each_word+','+str(reviewnum)+'\n'
        q = q.lower()
        xterms.append(q)

def print_scores():
    reviewnum = 0
    scores = []
    for i in inputfile:
        s = i.split(' ')
        if len(s) == 0:
            pass
        elif s[0] == "review/score:":
            reviewnum += 1
            q = ''
            q += s[1].strip('\n') + ',' + str(reviewnum) + '\n'
            scores.append(q)
    for i in scores:
        z.write(i)

open_file()
parse_lines()
print_pterms()
print_rterms()
print_scores()
