from flask import Flask, request, Response, jsonify
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
TOPICS = 'dbtopics1'
PERCENTILES = 'dbmetadata0'
AGGREGATE = 'dbaggregate0'
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
    collabvalues = sorted(cursor[0].get('related_topics'), key=lambda x: x.get('value'), reverse=True)

    cursor = conn[DB][COSINE_SIM].find({"name": topic}, {"related_topics": 1})
    cosineValues = sorted(cursor[0].get('related_topics'), key=lambda x: x.get('value'), reverse=True)

    collabvalues = filterByFilter(averageUpvote, averageViews, collabvalues, support)
    cosineValues = filterByFilter(averageUpvote, averageViews, cosineValues, support)

    return {"collab" : collabvalues, "cosine" : cosineValues}


def filterByFilter(averageUpvote, averageViews, collabvalues, support):

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

    collabvalues = filter(lambda x: genFilterFn(x.get("name"), "Avg_Question_score", avuLow, avuHigh), collabvalues)
    collabvalues = filter(lambda x: genFilterFn(x.get("name"), "Avg_View_count", avLow, avHigh), collabvalues)
    collabvalues = filter(lambda x: genFilterFn(x.get("name"), "Support_Percentile", sspLow, sspHigh), collabvalues)
    return collabvalues


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
        collabCount = request.args.get('collabCount')
        cosineCount = request.args.get('cosineCount')
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
