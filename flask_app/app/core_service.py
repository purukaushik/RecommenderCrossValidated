from flask import Flask, request, Response, jsonify
from pymongo import MongoClient

# MONGODB CONFIGURATION
#MONGODB_HOST = 'localhost'
MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
DB = 'dvproject'
PAGE_NO = 'pageNo'
COLLAB_FILTER = 'dbrelposts0'
COSINE_SIM = 'dbrelcosineposts0'
TOPICS = 'dbtopics0'

# Flask INIT
app = Flask(__name__)
app.config.from_object(__name__)

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

        return {"topic":  topic,
                "related_topics_list": related_topics_list
                }
    return {"topic": topic,
            "related_topics": related_topics[0]}

def get_topics():
    db_collection = conn[DB][TOPICS]
    cursor = db_collection.find()
    topics = [topic.get("name") for topic in cursor]
    return {"topics": topics}

@app.route("/", strict_slashes=False)
def home():
    return Response(response="Not authorized to view this page.", status=200)


@app.route("/heartbeat", strict_slashes=False)
def heartbeat():
    return jsonify({
        "heartbeat": "success"
    })


@app.route("/topicslist", methods=["GET"], strict_slashes=False)
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


if __name__ == '__main__':
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(filename="app_debug.log")
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
    app.run(host='0.0.0.0', port=3000)
