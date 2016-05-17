from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core import serializers
from elasticsearch import Elasticsearch
from django.views.decorators.csrf import csrf_exempt
import json
import requests


def stats(request):
    es = Elasticsearch()
    q_dict = request.GET
    state = q_dict['state'].lower()
    try:
        stats_return = es.search(index = state + '_' +  'stats' , filter_path = ['hits.hits._*'])['hits']['hits'][0]['_source']
    except:
        stats_return = {}
    return JsonResponse(stats_return)

def final(request):
    es = Elasticsearch()
    try:
        final_return = es.search(index = 'finalresult', filter_path = ['hits.hits._*'])['hits']['hits'][0]['_source']
    except:
        final_return = {}
    print final_return
    return JsonResponse(final_return)

def byname(request, name):
    print "byname requested: " + name
    es = Elasticsearch()
    #es = Elasticsearch(["https://search-twitter-stream-6xvgrazcnr7svjvka6wycl26hu.us-west-2.es.amazonaws.com"],verify_certs = True)
    try:
        get_size = es.search(index = name)['hits']['total']
        if get_size > 1000:
            get_size = 1000
        result_raw = es.search(index = name, filter_path = ['hits.hits._*'], size = get_size)
        result_list = result_raw["hits"]["hits"]
    except:
        result_list = []
    return_list = []
    #print result_list
    for tweets in result_list:
        #print tweets["_source"]
        try:
            print tweets["_source"]
            if tweets["_source"]["coordinates"] != None:
                to_append_list = tweets["_source"]["coordinates"]["coordinates"]
                to_append_dic ={}
                item = {}
                item['lat'] = to_append_list[1]
                item['lng'] = to_append_list[0]
                try:
                    item['senti_value'] = tweets['_source']['senti_value']
                except:
                    item['senti_value'] = 0
                # try:
                #     to_append_dic['senti_value'] = tweets['_source']['senti_value']
                # except KeyError:
                #     print "senti_value filed exception!"
                #     to_append_dic['senti_value'] = -3
                return_list.append(item)
        except KeyError:
            pass
    print "returned result count: " + str(len(return_list))
    #print "iterated: " + str(iteration_counter)
    #print "list len: " + str(len(result_list))
    return_dict = {}
    return_dict['list'] = return_list
    return JsonResponse(return_dict)


def showstats(request):
    template = loader.get_template('prediction/statspage.html')
    #print "view.index requested"
    return HttpResponse(template.render(request))

@csrf_exempt
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    template = loader.get_template('prediction/index.html')
    #print "view.index requested"
    return HttpResponse(template.render(request))


