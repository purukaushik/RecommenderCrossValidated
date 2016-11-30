# Motivation and Relevant Work

- Lu, Y. & **Hsiao, I-H.** Personalized Information Seeking Assistant (PiSA): From Programming Information Seeking To Learning, *Information Retrieval Journal*
- Parra, D., Brusilovsky, P., & Trattner, C. (2014). *See what you want to see: visual user-driven approach for hybrid recommendation*. Paper presented at the Proceedings of the 19th international conference on Intelligent User Interfaces, Haifa, Israel.

# Questions

How can we get a self-motivated learner to discover topics through visual and  textual recommendations?

How can we leverage the 

# Methodology

How we topic model — list of tags from stackexchange, wikipedia titles and the question/answer corpus to generate top-5 topic labels for each post(question+answers) using LDA.

We measure similarity between topics by 1) computing cosine similarity between topics  using their question/answer text and by 2) computing a collaborative filtering item-based similarity score from users and their interactions with posts belonging to various topics.

—do— apply filters

# Data Collection

crawling, cleaning, aggregation, etc

# Findings

correlation between topics in collaborative and content based recommendations







# How will it help someone self learning STATS101 class? — Stakeholder and 'why'

The cross validated site provides a platform for fledglings in the domain to ask questions to understand statistics better and there are domain experts who take time to answer questions and clarify doubts.

So this is  an ideal data set to generate models of user interests in topics. This can help us build recommendations to help beginners and self-learners discover topics that they might be interested in related to the topic that they're studying or querying stackoverflow for



## collaborative filtering 'why'

people learning in a similar pattern or people who are experts in a similar pattern. 

## content-based similarity 'why'

questions tagged under X are highly probable to be tagged in a neighboring topic in the graph



# The how  — filters, collab filtering, content-based

one size fit all doesnt exist -> customize -> on his requirements -> need for filters