import markovify
import numpy as np
import pronouncing
import re

from const import *

# Split lyric files into list of bars
def getAllBars(file):
	ret = []
	with open(file) as f:
		for line in f:
			line = line.strip()
			if line:
				ret.append(line)
	return ret

# Get list of rhymes from list of bars
def getAllRhyme(bars, readFromFile=False):
	if not readFromFile:
		rhymes = set()
		visited = set()
		for bar in bars:
			lastWord = bar.split(" ")[-1].lower()
			if not lastWord.isalpha():
				lastWord = re.sub(r"\W+", '', lastWord)
			# Skip the word that does not qualifiy for the rhyme generation
			if lastWord in visited or not lastWord.isalpha() or len(lastWord)<2:
				continue
			rhymesList = [word.encode('UTF8')[-2:] for word in pronouncing.rhymes(lastWord)]
			if rhymesList:
				rhymeEnd = max(set(rhymesList), key=rhymesList.count)
			else:
				rhymeEnd = lastWord[-2:]
			visited.add(lastWord)
			rhymes.add(rhymeEnd)
		rhymes = list(rhymes)
		rhymes.sort(key=lambda x: x[-1])
	else:
		rhymes = []
		with open(RHYMESFILE) as f:
			for line in f:
				rhymes.append(line.strip())
	return rhymes

# Get syllables percentage of a bar
def syllables(bar):
	count = 0
	helper = lambda w:len(''.join(" x"[c in"aeiouy"]for c in w.rstrip('e')).split())
	for word in bar:
		count += helper(word)
	return count/MAXSYLLABLES


# Get index of rhyme as a float
def ryhmeIndex(line, rhyme_list):
	# Find last word in bar
	word = re.sub(r"\W+", '', line.split(" ")[-1]).lower()
	rhymeslist = pronouncing.rhymes(word)
	rhymeslist = [x.encode('UTF8') for x in rhymeslist]
	rhymeslistends = []
	for i in rhymeslist:
		rhymeslistends.append(i[-2:])
	try:
		rhymescheme = max(set(rhymeslistends), key=rhymeslistends.count)
	except Exception:
		rhymescheme = word[-2:]
	try:
		float_rhyme = rhyme_list.index(rhymescheme)
		float_rhyme = float_rhyme / float(len(rhyme_list))
		return float_rhyme
	except Exception:
		return 0.0

# Build trainning data set
def buildDataSet(bars, rhymes):
	xData, yData = [], []
	datas = []
	for bar in bars:
		datas.append((syllables(bar), ryhmeIndex(bar, rhymes)))

	for i in range(len(datas)-3):
		# sentence1->sentence2,  sentence3->sentence4
		x = np.array([datas[i][0], datas[i][1], datas[i+2][0], datas[i+2][1]], dtype=np.float64).reshape(2,2)
		xData.append(x)

		y = np.array([datas[i+1][0], datas[i+1][1], datas[i+3][0], datas[i+3][1]], dtype=np.float64).reshape(2,2)
		yData.append(y)

	return np.array(xData), np.array(yData)

# Generate new lyric from exist lyric files
def generateLyrics(textFile, barLimit=500, lyricLimitIndex=2):
	bars = []
	lastWords = []
	count = 0
	markovModel = markov(textFile)
	with open(textFile, 'r') as f:
		totalBars = len(f.read().split('\n'))
		lyricLimit = totalBars * lyricLimitIndex

	while len(bars) < barLimit and count < lyricLimit:
		bar = markovModel.make_sentence()
		if bar and syllables(bar) < 1:
			last_word = bar.strip('!.?,').split(" ")[-1]
		if bar not in bars and lastWords.count(last_word) < 3:
			bars.append(bar)
			lastWords.append(last_word)
			count += len(bar.split(' '))
	return bars

def markov(text_file):
	read = open(text_file, "r").read()
	text_model = markovify.NewlineText(read)
	return text_model


if __name__ == "__main__":
	bars = getAllBars(LYRICSFILE)
	#print bars
	rhymes = getAllRhyme(bars)
	f = open(RHYMESFILE, 'w')
	f.write("NULL"+"\n")
	for rhyme in rhymes:
		f.write(rhyme+'\n')
	f.close()
