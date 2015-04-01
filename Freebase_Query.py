"""
FreeBase_Query.py

Description
-----------
The methods Search_Instance, Topic_Instance and Get_Instance enables users to search for a specific instance of a Freebase
relation in Freebase, obtain the description and Freebase relations of a instance, and perform the previous two methods for
multiple queries with the same relations respectively. Parse replicates lambda calculus of a question and employs
Search_Instance and Topic_Instance to do so.

Usage:

Search_Instance
---------------
Search('San Francisco', 'Warriors', 'sports', 1) # User is allowed to select number of results he wants from the query
Search('Titanic', 'James', 'directed')           # 1 is default

Topic_Instance
--------------
Topic_Instance('San Francisco', 'Warriors', '/en/golden_state_warriors', '/m/0jmj7', 'sports')
Topic_Instance('Titanic', 'James', 'en/titanic', '/m/0dr_4', 'directed')

Get_Instance
------------
Get_Instance([['San Francisco', 'Warriors'], ['Los Angeles', 'Lakers']], 'sports')
Get_Instance([['Titanic', 'James'], ['Dark Knight', 'Nolan']], 'directed')

Parse
-----
Parse('what genre is the hound of the baskervilles', 'hound of the baskervilles', '', 'genre')
Parse('what articles are in the july 1967 issue of frontier times', 'frontier times', 'july 1967', 'articles')

Si Kai Lee 11/03/2015

"""

import json
import re
import urllib


def Search_Instance(Q1, Q2, Relation, Number=1):

    # Get query
    api_key = 'AIzaSyDLAownuEEM-WLsT3MGxFhUKFnaTQh8F4w'
    service_url = 'https://www.googleapis.com/freebase/v1/search'

    params = {
            'query': Q1+'+'+Q2,
            'key': api_key
    }

    url = service_url + '?' + urllib.urlencode(params)
    response = json.loads(urllib.urlopen(url).read())

    required_response = []
    for y in range(Number):
        try:
        # [name, id, mid, confidence, relation]
            z = [response['result'][y]['name'], str(response['result'][y]['id']), str(response['result'][y]['mid']), '('+str(response['result'][y]['score'])+')', Relation]
            required_response.append(z)
        except IndexError:
            return "This search did not yield any valid results. Please check your inputs for errors and try again."

    return required_response


def Topic_Instance(Q1, Q2, ID, MID, Relation):

    api_key = 'AIzaSyDLAownuEEM-WLsT3MGxFhUKFnaTQh8F4w'
    service_url = 'https://www.googleapis.com/freebase/v1/topic'
    params = {
      'key': api_key,
    }
    url = service_url + MID + '?' + urllib.urlencode(params)
    topic = json.loads(urllib.urlopen(url).read())

    print url

    try:
    # Obtains description of topic
        Desc = topic['property']['/common/topic/description']['values'][0]['value']
    except KeyError:
        return "This search did not yield any valid results. This search did not yield any valid results. Please check your inputs for errors and try again."

    # Initiates list collecting possible Freebase relations
    RShip = []

    # Sets default Freebase relation as the relation found under /common/topic/notable_types

    Default = topic['property']['/common/topic/notable_types']['values'][0]['id']
    Default_Count = re.findall('\/', Default)
    Default_1 = Default

    # Collects matches between Relation and Freebase relations, replaces default relation if match is found
    for x in topic['property']:
        try:
            if Relation in x and Relation not in Default:
                Default = x
                RShip.append(x)
        except IndexError:
            pass

    # for x in topic['property']:
    #     for v in range(len(topic['property'][x]['values'])):
    #         try:
    #             y = topic['property'][x]['values'][v]['text']
    #             if Q1 in y or Q2 in y:
    #               if Relation in x and Relation not in Default:
    #                 Default = x
    #                 RShip.append(x)
    #         except IndexError:
    #             pass


    # Ensures that output Freebase relation is most general
    for x in RShip:
        # print x
        if re.findall('\/', x) < Default_Count:
            Default = x
            Default_Count = re.findall('\/', Default)

    # for x in topic['property']:
    #     for v in range(len(topic['property'][x]['values'])):
    #         try:
    #             y = topic['property'][x]['values'][v]['text']
    #             if re.findall('\/common|\/wiki|\/type', x) == [] and re.findall('\/common|\/wiki', y) == []:
    #                 if Q1 in y or Q2 in y:
    #                     RShip.append([x, topic['property'][x]['values'][v]['text']])
    #         except IndexError:
    #             pass


    # Trims output Freebase relation so that the last word is similar to Relation
    Default_p = Default.split('/')
    for x in range(len(Default_p))[::-1]:
        if Relation not in Default_p[x]:
            Default_p.pop(x)
        else:
            break

    Default = '/'.join(Default_p)

    return [Q1, Q2, ID, Desc, Default, Default_1]


def Get_Instance(Instances, Relation):

    Responses_Col = []

    # Iterates through the list
    for x in range(len(Instances)):

        # Checks if more than one instance is required per search
        if len(Instances[x]) == 2:
            Q1, Q2 = Instances[x]
        else:
            Q1, Q2, Number = Instances[x]

        # Search_Instance
        Responses = Search_Instance(Q1, Q2, Relation, Number=1)

        # Initiates list collecting Topic_Instance outputs
        Responses_i = []

        # Iterates through list of responses and run Topic_Instance for each response
        for x in range(len(Responses)):
            try:
                y = Topic_Instance(Q1, Q2, Responses[x][1], Responses[x][2], Responses[x][-1])
                Responses_i.append([Responses[x][0], y[2], y[3], y[4], y[5]])
            except IndexError:
                return "This search did not yield any valid results. Please check your inputs for errors and try again."

        Responses_Col.append(Responses_i)

    return Responses_Col

# (lambda $0 /people/person (/architecture/architectural_style@architects:t /en/bauhaus:/architecture/architectural_style $0))

def Parse(Input, Q1, Q2, Relation):
    Input = Input.split()

    # Sorts the different possible questions asked
    if Input[0].lower() == 'who':
        Parse = ['(lambda $0 /people/person (/', '', ' $0))']
    elif Input[0].lower() == 'how':
        if Input[1].lower() == 'many':
            Parse = ['(count $0 (/', '', ' $0))']
        elif Input[1].lower() == 'long':
            Parse = ['(lambda $0 /type/int (/', '', ' $0))']
    elif Input[0].lower() == 'when':
        Parse = ['(lambda $0 /type/datetime (/', '', ' $0))']
    elif Input[0].lower() == 'where':
        Parse = ['(lambda $0 /location/location (/', '', ' $0))']
    else:
        Parse = ['(lambda $0 /common/topic (/', '', ' $0))']

    Responses = Search_Instance(Q1, Q2, Relation, Number=1)
    Topic = Topic_Instance(Q1, Q2, Responses[0][1], Responses[0][2], Responses[0][-1])

    if Topic == "This search did not yield any valid results. Please check your inputs for errors and try again.":
        return "This search did not yield any valid results. Please check your inputs for errors and try again."

    # Checks if there was a relation mathc
    if Topic[-2] == '':
        Delta_End = Topic[-1].split('/')
        Delta = Delta_End.pop()
        Delta_End.pop(0)
    else:
        # Provides the phrases before and after @
        try:
            Delta = list(set(Topic[-2].split('/')) - set(Topic[-1].split('/')))
            Delta_End = Topic[-2].split('/')
            Delta_End = Delta_End[1:(len(Delta_End)-len(Delta))]
            # If Topic[-2] is exactly identical or completely different from Topic[-1], use the last word of Topic[-2] as
            # the word after @
            if len(Delta) == len(Topic[-2].split('/')) - 1 or len(Delta) == 0:
                Delta_End = Topic[-2].split('/')
                Delta_End.pop(0)
                Delta = Delta_End.pop()
        except ValueError:
            Delta_End = Topic[-2].split('/')
            Delta = Delta_End.pop()
            Delta_End.pop(0)

    # print Delta, Delta_End

    # Concatenates the phrase to be inserted in the lambda calculus
    try:
        if type(Delta) is list:
            Insertion = ('/').join(Delta_End) + '@' + ('@').join(Delta) + ':t ' + Topic[2] + ': '+ ('/').join(Delta_End)
        else:
            Insertion = ('/').join(Delta_End) + '@' + Delta + ':t ' + Topic[2] + ': '+ ('/').join(Delta_End)
        # print Insertion
        Parse[1] = Insertion
    except TypeError:
        return "This search did not yield any valid results. Please check your inputs for errors and try again."

    return ('').join(Parse)

# def Search_Relation(Instance, Relation, Number=10):

#     api_key = 'AIzaSyDLAownuEEM-WLsT3MGxFhUKFnaTQh8F4w'
#     service_url = 'https://www.googleapis.com/freebase/v1/search'

#     params = {
#             'query': Instance,
#             'filter': "(all type:\""+Relation.lower()+"\")",
#             'key': api_key
#     }

#     url = service_url + '?' + urllib.urlencode(params)
#     response = json.loads(urllib.urlopen(url).read())

#     required_response = []

#     for y in range(Number):
#         z = [response['result'][y]['name'], str(response['result'][y]['id']), str(response['result'][y]['mid']), '('+str(response['result'][y]['score'])+')']
#         required_response.append(z)

#     return required_response


# def Topic_Relation(Name, MID, ID='Null'):

#     api_key = 'AIzaSyDLAownuEEM-WLsT3MGxFhUKFnaTQh8F4w'
#     service_url = 'https://www.googleapis.com/freebase/v1/topic'
#     params = {
#       'key': api_key
#     }
#     url = service_url + MID + '?' + urllib.urlencode(params)
#     topic = json.loads(urllib.urlopen(url).read())

#     Desc = topic['property']['/common/topic/description']['values'][0]['value']

#     RShip = []

#     # RShip_1 = []

#     # for property in topic['property']:
#     #     print property + ':'
#     #     for value in topic['property'][property]['values']:
#     #         try:
#     #             RShip.append(value['id'])
#     #         except KeyError:
#     #             continue

#     for property in topic['property']:
#         print property + ':'
#         for value in topic['property'][property]['values']:
#             try:
#                 RShip.append(value['id'])
#             except KeyError:
#                 pass

#     # print 'Is RShip = RShip_1' + str(RShip == RShip_1)

#     RShip_P = [i for i in RShip if not re.findall("\/m.+|\/user.+", i)]

#     # print RShip_P

#     RShip_C = list(set(RShip_P))

#     if ID == 'Null':
#         Result = [Name, Desc, RShip_C]
#     else:
#         Result = [Name, ID, Desc, RShip_C]

#     return Result


# def Get_Relation(Instance, Relation, Number=10):

#     Responses_Col = []

#     for i in Instance:

#         Responses = Search_Relation(i, Relation, Number)

#         Responses_i = []

#         for x in range(len(Responses)):
#             y = Topic_Relation(Responses[x][0], Responses[x][2], Responses[x][1])
#             Responses_i.append(y)

#             Responses_Col.append(Responses_i)

#     return Responses_Col
