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
TOPICS = 'dbtopics0'
PERCENTILES = ''
AGGREGATE = 'dbaggregate0'
# Flask INIT
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

# MONGODB Connection
conn = MongoClient(host=app.config['MONGODB_HOST'], port=app.config['MONGODB_PORT'])


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

        return {"topic": topic,
                "related_topics_list": related_topics_list
                }
    return related_topics[0]


def getDescription(topic):    
    cursor = conn[DB][TOPICS].find({"name": topic}, {"description": 1})
    description = cursor[0].get("description")
    return description


def get_topics():
    db_collection = conn[DB][TOPICS]
    cursor = db_collection.find()
    topics = [topic.get("name") for topic in cursor]
    return {"topics": topics}


def filter_reco(topic, collabCount, cosineCount, averageViews, averageUpvote, support):
    # 1. COLLAB
    # .. i. Get the collab topics from DB with metric, sort them by value
    cursor = conn[DB][COLLAB_FILTER].find({"name": topic}, {"related_topics": 1})
    collabvalues = sorted(cursor[0].get('related_topics'), key=lambda x: x.get('value'), reverse=True)

    # .. ii. For each apply averageViews filter ->
    # ....a. obtain %le from other table,
    cursor = conn[DB][PERCENTILES].find({"name": topic})
    minViewPerc, maxViewPerc = map(int, cursor[0].get(averageViews).split("-"))
    minUpVotePerc, maxUpVotePerc = map(int, cursor[0].get(averageUpvote).split("-"))
    minSupportPerc, maxSupportPerc = map(int, cursor[0].get(support).split("-"))


    # ....b. get values for this topic
    cursor = conn[DB][AGGREGATE].find({"name": topic})
    avgViewCount = cursor[0].get("Avg_View_count")
    averageUpvoteCount = cursor[0].get("Avg_Question_score")
    supportCount = cursor[0].get("Support_Percentile")

    # ....c. check %le with averageViews

    # ....d. filter if averageViews in curr topic %le
    # ...iii. Do the same for averageUpvote

    # 2. COSINE -> do same steps as above

    return {}


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


# NOT IN USE
def deprecated(dummy):
    """
    Function is deprecated
    :return:
    """
    yield NotImplementedError


@deprecated
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
        return jsonify(filter_reco(topic, collabCount, cosineCount, averageViews, averageUpvote, support))

@app.route("/description", methods=["GET"], strict_slashes=False)
def get_related_data():
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
    app.run(host='0.0.0.0', port=3000)
