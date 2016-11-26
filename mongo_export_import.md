## MONGOEXPORT from SERVER to local fs
```bash
mongoexport -h  ec2-52-43-158-164.us-west-2.compute.amazonaws.com:27017  -d dvproject -c dbquestion -o questions.json
```

###Usage
`mongoexport -h <HOST:PORT> -d <DATABASE_NAME> -c <COLLECTION_NAME> -o <OUTPUT_FILE_PATH/FILENAME>`

##MONGOIMPORT from local fs to local db

```bash
mongoimport --db dvproject --collection dbquestion --file questions.json
```

##PUSH data to SERVER

```bash
scp -i <PRIVATE_KEY> questions.json ec2-user@ec2-52-43-158-164.us-west-2.compute.amazonaws.com:~/
```

```bash
mongoimport --db dvproject --collection dbquestion --file ~/questions.json
```
