from time import sleep
from elasticsearch import Elasticsearch
import json


RUN_COUNT = 10
SLEEP_TIME = 600
MAP_FILE = "electoral_map.txt"
NOMINEES = ['trump', 'clinton']
SENTI_THRESHOLD = 0.5
SUPPORT_LEVEL = [0.05, 0.2, 0.55, 0.8, 0.95]
es = Elasticsearch()


def makePrediction(stats):
    total = float(stats[NOMINEES[0]]['total'] + stats[NOMINEES[1]]['total'])
    if total != 0:
        stat = stats[NOMINEES[0]]
        veryPosVotes = stat['veryPos'] / total * SUPPORT_LEVEL[4]
        posVotes = stat['pos'] / total * SUPPORT_LEVEL[3]
        neutralVotes = stat['neutral'] / total * SUPPORT_LEVEL[2]
        negVotes = stat['neg'] / total * SUPPORT_LEVEL[1]
        veryNegVotes = stat['veryNeg'] / total * SUPPORT_LEVEL[0]

        stat = stats[NOMINEES[1]]
        coungter_veryPosVotes = stat['veryPos'] / total * (1 - SUPPORT_LEVEL[4])
        coungter_posVotes = stat['pos'] / total * (1 - SUPPORT_LEVEL[3])
        coungter_neutralVotes = stat['neutral'] / total * (1 - SUPPORT_LEVEL[2])
        coungter_negVotes = stat['neg'] / total * (1 - SUPPORT_LEVEL[1])
        coungter_veryNegVotes = stat['veryNeg'] / total * (1 - SUPPORT_LEVEL[0])

        voteRate0 = veryPosVotes + posVotes + neutralVotes + negVotes + veryNegVotes
        + coungter_veryPosVotes + coungter_posVotes + coungter_neutralVotes + coungter_negVotes +coungter_veryNegVotes

        stat = stats[NOMINEES[1]]
        veryPosVotes = stat['veryPos'] / total * SUPPORT_LEVEL[4]
        posVotes = stat['pos'] / total * SUPPORT_LEVEL[3]
        neutralVotes = stat['neutral'] / total * SUPPORT_LEVEL[2]
        negVotes = stat['neg'] / total * SUPPORT_LEVEL[1]
        veryNegVotes = stat['veryNeg'] / total * SUPPORT_LEVEL[0]

        stat = stats[NOMINEES[0]]
        coungter_veryPosVotes = stat['veryPos'] / total * (1 - SUPPORT_LEVEL[4])
        coungter_posVotes = stat['pos'] / total * (1 - SUPPORT_LEVEL[3])
        coungter_neutralVotes = stat['neutral'] / total * (1 - SUPPORT_LEVEL[2])
        coungter_negVotes = stat['neg'] / total * (1 - SUPPORT_LEVEL[1])
        coungter_veryNegVotes = stat['veryNeg'] / total * (1 - SUPPORT_LEVEL[0])

        voteRate1 = veryPosVotes + posVotes + neutralVotes + negVotes + veryNegVotes
        + coungter_veryPosVotes + coungter_posVotes + coungter_neutralVotes + coungter_negVotes +coungter_veryNegVotes

        rateSum = voteRate0 + voteRate1

        return [voteRate0/rateSum, voteRate1/rateSum]
    else:
        return [0,0]

def makeStats():
    mapFile = open(MAP_FILE, 'r')
    electoralMap = {}
    finalResult = {NOMINEES[0]: 0, NOMINEES[1]: 0}
    for line in mapFile:
        stateName = line.split(' ')[0]
        voteNum = int(line.split(' ')[1])
        electoralMap[stateName] = voteNum

    for state in electoralMap:
        stats = {NOMINEES[0]: {}, NOMINEES[1]:{}}
        for nominee in NOMINEES:
            stat = {'total': 0, 'sentiSum': 0, 'veryPos': 0, 'pos': 0, 'neutral': 0, 'neg': 0, 'veryNeg':0}
            try:
                get_size = es.search(index = nominee)['hits']['total']
                result_raw = es.search(index = nominee + '_' + state.lower(), filter_path = ['hits.hits._*'], size = get_size)
                result_list = result_raw["hits"]["hits"]
            except:
                result_list = []
            
            for tweet in result_list:
                stat['total'] += 1
                senti = tweet['_source']['senti_value']
                if senti > SENTI_THRESHOLD:
                    stat['veryPos'] += 1
                elif senti > 0:
                    stat['pos'] += 1
                elif senti == 0:
                    stat['neutral'] += 1
                elif senti > -SENTI_THRESHOLD:
                    stat['neg'] += 1
                elif senti >= -1:
                    stat['veryNeg'] += 1
            stats[nominee] = stat

        supportRates = makePrediction(stats)
        stats[NOMINEES[0]]['supportRate'] = supportRates[0]
        stats[NOMINEES[1]]['supportRate'] = supportRates[1]
        res = es.index(index = state.lower() + '_' + 'stats', doc_type = "stats", id = 0, body = json.dumps(stats))
        print state
        print res
        print supportRates
        finalResult[NOMINEES[0]] += (supportRates[0] > supportRates[1]) * electoralMap[state]
        finalResult[NOMINEES[1]] += (supportRates[0] < supportRates[1]) * electoralMap[state]
    res = es.index(index = 'finalresult', doc_type = "finalResult", id = 0, body = json.dumps(finalResult))

if __name__ == '__main__':
    count = 0
    while count < RUN_COUNT:
        makeStats()
        sleep(SLEEP_TIME)
