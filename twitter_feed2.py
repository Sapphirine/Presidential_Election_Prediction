from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
import time
from datetime import datetime
from elasticsearch import Elasticsearch
import json
import alchemyapi as acm
import urllib


Keywords = ['Trump', 'Cruz', 'Kasich', 'Clinton', 'Sanders']

TIME_OUT = 3600*24
access_token = "339694619-zn7vQfCNh0U87SKZs5RRcvSJjT3pahKwkQoM2veF"
access_token_secret = "6dlJawB6eBfy4VTc6wjUT3YVBEHA3cqiL4Ld081eSPJKq"
consumer_key = "lrCLIfpKyDteHdjrgKg42s7GB"
consumer_secret = "VzNW8ChmFCFDBgozDx5XAMVu85m1PXkqMQ9ZkY3gmPsXFTpKSU"



# sqs = boto3.resource('sqs')
# sqs = aws.getResource('sqs','us-east-1')
# queue = sqs.get_queue_by_name(QueueName='TwittMap')

time_start = time.time()
es = Elasticsearch()
#es = Elasticsearch(["https://search-twitter-stream-6xvgrazcnr7svjvka6wycl26hu.us-west-2.es.amazonaws.com"],verify_certs = True)
counter = 0
#for keyword in Keywords:
	#es.index(index = "keyword", doc_type = "tweets", id = 42, body = {"timestamp": datetime.now()})



def maps(lat,lng):

    key='AIzaSyBZT8leFezfMRX-oQE8NEg0kAT3MBdGpho'

    url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(lng)+ '&key=' + key
    
    fh = urllib.urlopen(url)
    data_json = fh.read()
    data = json.loads(data_json)
    address = data["results"][0]["formatted_address"]
    words = address.split(',')
    if words[-1] != ' USA':
        return 'OUT'
    province = ((words[2].strip()).split())[0]
    
    return province

def tweet_analysis(content):
	al = acm.AlchemyAPI()
	try:
	    this_result = al.sentiment('text', content)['docSentiment']
	except:
	    print "AlchemyAPI exception"
	    return -2
	try:
	    result = float(this_result['score'])
	except KeyError:
	    result = 0
	return result

class listener(StreamListener):
	def on_data(self, data):
		global counter
		global TIME_OUT
		if (time.time() - time_start) > TIME_OUT:
			print counter
			return False
		json_data = json.loads(data)
		#print  json_data["coordinates"]
		try:
			if json_data["coordinates"] != None and json_data["lang"] == "en":
				for keyword in Keywords:
					if keyword in json_data["text"]: 
						
						json_data["keyword"] = keyword
						coor = json_data["coordinates"]["coordinates"]
						json_data["state_ID"] = maps(coor[1], coor[0])
						#json_data["state_ID"] = 'NY'
						json_data["senti_value"] = tweet_analysis(json_data['text'])
						to_index = json_data["keyword"].lower() + "_" + json_data["state_ID"].lower()
						to_id = int(time.time() * 100)
						toStore = json.dumps(json_data, ensure_ascii=False)
						if json_data["senti_value"] != -2:
							res0 = es.index(index = json_data["keyword"].lower(), doc_type = "tweets", id = to_id, body = toStore)
							res1 = es.index(index = to_index, doc_type = "tweets", id = to_id, body = toStore)
						# queue.send_message(MessageBody=toSend)
							counter += 1
							if res0['created'] and res1['created']:
							 	print "archive success"
							 	print counter
								print keyword
								print json_data['state_ID']
								print json_data["coordinates"]
								print json_data["senti_value"]
		except KeyError:
			pass
		return True
	def on_error(sefl, status):
		print status


def main():
	id = OAuthHandler(consumer_key, consumer_secret)
	id.set_access_token(access_token,access_token_secret)
	while True:
		try:
			Stream(id, listener()).filter(track=Keywords)
		except KeyboardInterrupt:
			raise

if __name__ == '__main__':
	main()
