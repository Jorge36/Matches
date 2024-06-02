import pandas as pd
import glob, os, gc
import jellyfish
import cdifflib
from fuzzywuzzy import process, fuzz
import re
import itertools

# process string, this function cleans special characters and whitespaces, and remove substring which are in ingnore_list
def normalize_str(input_str, normalized=False, ignore_list=[]):
    # removes substring in input_str, if the substring is in input_str
    for ignore_str in ignore_list:
        input_str = re.sub(r'{0}'.format(ignore_str), "", input_str, flags=re.IGNORECASE)

    # converts all the characters in lowercase
    # copy of the string with both leadings and trailing characters removed
    if normalized is True:
        input_str = input_str.strip().lower()
        #clean special chars and extra whitespace
        input_str = re.sub("\W", "", input_str).strip()

    return input_str

# calculate ratio between two strings and return a matching ratio between
# 1.0 (most matching) and 0.0 (not matching) using jellyfish or sequencematcher algorithms or neither
# ignore_list contains characters to substitute with ''
def find_string_similarity(first_str, second_str, normalized=False, ignore_list=[]):
    """
    Example: find_string_similarity("Python programmer","Python,programmer!",normalized=True)
    """
    first_str = normalize_str(first_str, normalized=normalized, ignore_list=ignore_list)
    second_str = normalize_str(second_str, normalized=normalized, ignore_list=ignore_list)
    match_ratio = (cdifflib.CSequenceMatcher(None, first_str, second_str).ratio() + jellyfish.jaro_winkler(first_str, second_str))/2.0
    return match_ratio

def match_token_sort_ratio(input_str1, input_str2):
    return fuzz.token_sort_ratio(input_str1, input_str2)

def match_token_sort_ratio_with_List(input_str, input_list):
    return itertools.filterfalse(lambda x: x[1] < 70,process.extract(input_str, input_list, scorer=fuzz.token_sort_ratio))

# change directoy of work
os.chdir('/home/Jorge/Desktop/testing')
# create a dataframe to save the union between files
results = pd.DataFrame([])

for counter, file in enumerate(glob.glob('file*')):
    # read files and assing result to a dataframe
    name = pd.read_csv(file, skiprows = 0)
    # if result is empty, append first dataframe
    if results.empty:
        results = results._append(name, ignore_index = True)
    else: # concatenate dataframes along axis 1
        current_result = pd.DataFrame([])
        current_result = current_result._append(name, ignore_index = True)
        results = pd.concat([results, current_result], axis = 1, ignore_index = False)
        # delete variable and call garbage collector
        del current_result
        gc.collect()

# main logic
# Quantity of row column 2 in results dataframe
quantity_columns1 = results.iloc[:,0].shape[0]
# iterator for column1
iterator1 = itertools.cycle(results.iloc[:,0])
# Quantity of row column 2 in results dataframe
quantity_columns2 = results.iloc[:,1].shape[0]
# iterator for column2
iterator2 = itertools.cycle(results.iloc[:,1])
# list witn value in column 2
list_column2 = []
# dict result with tuples normalized
dict_result_aux = {}
# dict result final
dict_result = {}
# dict column 1
dict_column1 = {}
# dict column 2
dict_column2 = {}

# create dictionary with names and the names normalized
# and a list with the names normalized
for i in range(quantity_columns2):
    name = next(iterator2)
    nameAux = normalize_str(str(name), True, ['$', '-'])
    dict_column2[nameAux] = name
    list_column2.append(nameAux)

# create dictionary with names and the names normalized
# and a list with the names normalized
for i in range(quantity_columns1):
    name= next(iterator1)
    nameAux = normalize_str(str(name), True, ['$', '-'])
    dict_column1[nameAux] = name
    dict_result_aux[nameAux] = []

# calculate ratio using token_sort_ratio from fuzzywuzzy
for name in dict_result_aux:
    dict_result_aux[name] =  list(match_token_sort_ratio_with_List(name, list_column2))

# create dictionary final with the values from files
# using dictionaries created in the first two loops
for key, value in dict_result_aux.items():
        list_result = []
        for v in value:
            list_result.append(dict_column2[v[0]] + ", ratio = " + str(v[1]))
        dict_result[dict_column1[key]] = list_result

del results
gc.collect()
results = pd.DataFrame.from_dict(dict_result, orient='index')
results.to_csv('/home/Jorge/Desktop/testing/results.csv')
# another solution could be using find_string_similarity functino to calculate ratio
# we'd have two loops with this solution,it would be less efficient than the solution implemented becuase
# The solution implemented use itertools to calculate similarities


