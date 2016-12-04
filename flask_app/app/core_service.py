from flask import Flask, request, Response, jsonify
from itertools import groupby    
from flask_cors import CORS
from pymongo import MongoClient

# MONGODB CONFIGURATION
# MONGODB_HOST = 'localhost'
MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
DB = 'dvproject'
PAGE_NO = 'pageNo'
COLLAB_FILTER = 'dbrelposts0'
COSINE_SIM = 'dbrelcosineposts0'
PERCENTILES = 'dbmetadata0'
TOPICS = 'dbtopics0'
AGGREGATE = 'dbaggregate0'
METADATA = 'dbmetadata0'

# Flask INIT
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

# MONGODB Connection
conn = MongoClient(host=app.config['MONGODB_HOST'], port=app.config['MONGODB_PORT'])
# question score %iles
qsp = []
# support score %iles
ssp = []
# average view count %iles
avp = []
MAPPING = {
    0: "Low",
    1: "Medium",
    2: "High"
}


def get(algo, topic, list_topics=False):
    if algo == 'collabf':
        db_collection = conn[DB][COLLAB_FILTER]
    elif algo == 'cosine':
        db_collection = conn[DB][COSINE_SIM]
    else:
        return {}
    cursor = db_collection.find({"name": topic}, {"related_topics": 1})

    related_topics = [x.get("related_topics") for x in cursor]
    if list_topics:
        related_topics_list = [x.get('name') for x in related_topics[0]]

        return {"topics": related_topics_list
                }
    return related_topics[0]


def getDescription(topic):
    cursor = conn[DB][TOPICS].find({"name": unicode(topic)}, {"desc": 1})
    if cursor.count():
        description = str(cursor[0].get("desc"))
    else:
        description = {}
    return description


def get_topics():
    # TODO : return list of topics from dbtopics table instead of collabf table
    # db_collection = conn[DB][TOPICS]
    # cursor = db_collection.find()
    # topics = [topic.get("name") for topic in cursor]
    db_collection = conn[DB][COLLAB_FILTER]
    cursor = db_collection.find()
    first = cursor[0]
    topics = [x.get("name") for x in first.get("related_topics")]
    return {"topics": topics}


def filter_reco(topic, collabCount, cosineCount, averageViews, averageUpvote, support):
    # 1. COLLAB
    # .. i. Get the collab topics from DB with metric, sort them by value
    cursor = conn[DB][COLLAB_FILTER].find({"name": topic}, {"related_topics": 1})
    
    collabvalues = sorted(cursor[0].get('related_topics'),key=lambda x: x.get('value'), reverse=True)
    collabvalues = map(lambda x: (x.get('name'), x.get('value')), collabvalues)
    collabvalues = filter(lambda x: x[0]!=topic, collabvalues)

    cursor = conn[DB][COSINE_SIM].find({"name": topic}, {"related_topics": 1})
    cosineValues = sorted(cursor[0].get('related_topics'), key=lambda x: x.get('value'), reverse=True)
    cosineValues = map(lambda x: (x.get('name'), x.get('value')), cosineValues)     
    cosineValues = filter(lambda x: x[0]!=topic, cosineValues)

    collabvalues = filterByFilter(averageUpvote, averageViews, collabvalues,support,collabCount)
    cosineValues = filterByFilter(averageUpvote, averageViews, cosineValues,support, cosineCount)
    
    return {"collab": collabvalues, "cosine": cosineValues}


def filterByFilter(averageUpvote, averageViews, collabvalues, support, count):
    AVP__ = unicode(MAPPING.get(int(averageViews)))
    QSP__ = unicode(MAPPING.get(int(averageUpvote)))
    SSP__ = unicode(MAPPING.get(int(support)))

    avLow, avHigh = map(float, avp[0].get(AVP__).split("-"))
    avuLow, avuHigh = map(float, qsp[0].get(QSP__).split("-"))
    sspLow, sspHigh = map(float, ssp[0].get(SSP__).split("-"))

    def genFilterFn(relTopic, quirk, low, high):
        cursor = conn[DB][AGGREGATE].find({"Topic": relTopic})
        k__ = cursor[0].get(quirk)
        return low <= k__ and k__ <= high

    scoreFilter = filter(lambda x: genFilterFn(x[0], "Avg_Question_score", avuLow, avuHigh), collabvalues)
    viewFilter = filter(lambda x: genFilterFn(x[0], "Avg_View_count", avLow, avHigh), collabvalues)
    supportFilter = filter(lambda x: genFilterFn(x[0], "Support_Percentile", sspLow, sspHigh), collabvalues)
    resultValues = map(lambda x: (x[0],x[1],3), list(set(scoreFilter) & set(viewFilter) &
        set(supportFilter)))

    def mapIt(l,v):
        return map(lambda x:(x[0],x[1],v), l)
    def commonElementsNotAlreadyIncluded(resultList, list1, list2=None):
        if list2:
            return mapIt(list((set(list1) & set(list2)) - set(resultList)),2)
        else:
            return mapIt(list(set(list1) - set(resultList)),1)

    if len(resultValues) < count:
        resultValues = resultValues + commonElementsNotAlreadyIncluded(resultValues, viewFilter, scoreFilter)
        resultValues = resultValues + commonElementsNotAlreadyIncluded(resultValues, viewFilter, supportFilter)
        resultValues = resultValues + commonElementsNotAlreadyIncluded(resultValues, supportFilter, scoreFilter)
    resultList = map(lambda x: max(list(x[1]), key=lambda z:z[2]),
            groupby(sorted(resultValues, key=lambda c: c[0]), lambda y: y[0]))
    resultList = sorted(resultList, key=lambda x:x[1], reverse=True )
    if len(resultList) >= count:
        print len(resultList), count
        print "more than what we need"
        return resultList[0:count]
    else:
        print len(resultList)
        return resultList

@app.route("/", strict_slashes=False)
def home():
    return Response(response="Not authorized to view this page.", status=200)


@app.route("/heartbeat", strict_slashes=False)
def heartbeat():
    return jsonify({
        "heartbeat": "success"
    })


@app.route("/topicsList", methods=["GET"], strict_slashes=False)
def list_topics():
    return jsonify(get_topics())


@app.route("/<algo>", methods=["GET"], strict_slashes=False)
def get_filter_data(algo):
    if len(request.args) != 0:

        topic = request.args.get('topic')
        if topic:
            topics_list = request.args.get('list')
            if topics_list:
                return jsonify(get(algo, topic, topics_list))
            else:
                return jsonify(get(algo, topic))
    return jsonify({})


@app.route("/related", methods=["GET"], strict_slashes=False)
def get_related_data():
    if len(request.args) != 0:
        topic = request.args.get('topic')
        if topic:
            return jsonify({
                "collabf": get("collabf", topic),
                "cosine": get("cosine", topic)
            })


@app.route("/recommendation", methods=["GET"], strict_slashes=False)
def get_recommendation_data():
    if len(request.args):
        collabCount = int(request.args.get('collabCount'))
        cosineCount = int(request.args.get('cosineCount'))
        averageViews = request.args.get('view')
        averageUpvote = request.args.get('upvotes')
        support = request.args.get('support')
        topic = request.args.get('topic')
        print "topic, collabCount, cosineCount, averageViews, averageUpvote, support"
        print topic, collabCount, cosineCount, averageViews, averageUpvote, support
        return jsonify(filter_reco(topic, collabCount, cosineCount, averageViews, averageUpvote, support))


@app.route("/description", methods=["GET"], strict_slashes=False)
def get_description_():
    if len(request.args) != 0:
        topic = request.args.get('topic')
        if topic:
            return jsonify({
                "description": getDescription(topic)
            })


def question_list(topic, question_order):
    db_collection = conn[DB][AGGREGATE]
    cursor = db_collection.find({"Topic": topic})
    if cursor.count():
        if question_order == 1:
            return  cursor[0].get("Score_Question_list")
        elif question_order == 2:
            return cursor[0].get("View_Question_list")
        elif question_order == 3:
            return cursor[0].get("Recent_Question_list")
        elif question_order == 4:
            return cursor[0].get("Bounty_Question_list")
        elif question_order == 5:
            return cursor[0].get("Most_Answer_Question_list")
        else:
            return [{"Question": "Error - Option not found."}]
    else:
        return [{"Question": "Error - Option not found."}]


@app.route("/recommendedQuestion", methods=["GET"], strict_slashes=False)
def get_question_list():
    if len(request.args) != 0:
        try:
            topic = request.args.get('topic')
            if topic:
                question_order = request.args.get('sortOrder')
                if question_order:
                    return jsonify({
                        "topic": topic,
                        "question": question_list(topic, int(question_order))
                    })
                else:
                    return jsonify({"Error" : "No question_order"})
            else:
                return jsonify({"Error:":"No topic"})
        except Exception as e:
            print e.message
            print 'Error has occured when fetching the list of questions'
    return jsonify({})



if __name__ == '__main__':
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(filename="app_debug.log")
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
    qsp = map(lambda x: x, conn[DB][PERCENTILES].find({"Id": "Avg_Question_score"}))
    avp = map(lambda x: x, conn[DB][PERCENTILES].find({"Id": "Avg_View_count"}))
    ssp = map(lambda x: x, conn[DB][PERCENTILES].find({"Id": "Support_Percentile"}))
    app.run(host='0.0.0.0', port=3000)
