# documents = (
# "The sky is blue blue blue blue",
# "The sun is bright",
# "The in the sky is bright sun blue blue blue",
# "We can see the shining sun, the bright sun"
# )

with open('test.txt') as f:
	testLyric = ''
	for line in f:
		line = line.strip()
		testLyric += line + ' '

trainSong = []

with open('lyrics.txt') as f:
	trainLyric = ''
	for line in f:
		line = line.strip()
		if not line:
			trainSong.append(trainLyric)
			trainLyric = ''
			continue
		trainLyric += line + ' '

# print testLyric
# print trainLyric
trainSong.insert(0, testLyric)
documents = tuple(trainSong)

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

from sklearn.metrics.pairwise import cosine_similarity
result =  cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
print result[0]

