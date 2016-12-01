## Usage

0. If a topic doesn't exist in the database, you get an empty json like this
```json
    {
    "related_topics": [],
    "topic": "lik"
  }
```
1. Collab filtering metrics for a topic=likert

```bash
    curl http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000/collabf?topic=likert
```
  returns all related topics to `likert` obtained using collaborative filtering.
  Result looks like:
```json
  {
    "related_topics": [
      {
        "name": "invariance", 
        "value": 0.0
      }, 
      ...
    ], 
      "topic": "likert"
  }
```

2. Content based cosine similarities for a topic=likert
```bash
    curl http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000/cosine?topic=likert
```
  returns all related topics to topic `likert` based on cosine similarity.
  Output looks like this:
```json
    {
    "related_topics": [
      {
        "name": "invariance", 
        "value": 0.0
      }, 
      ...
    ], 
      "topic": "likert"
  }
```

3. List topics :

   `curl http://ec2-52-43-158-164.us-west-2.compute.amazonaws.com:3000/collabf?topic=likert&list=true`

   Result looks like this:

   ```json
   {
     "related_topics_list": [
       "invariance", 
       "likert", 
       "nnet", 
       ...
       "aic"
     ], 
     "topic": "likert"
   }
   ```

   ​