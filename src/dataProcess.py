import pronouncing
import re

def getAllBars(file):
	ret = []
	with open(file) as f:
		for line in f:
			line = line.strip()
			if line:
				ret.append(line)
	return ret

def getAllRhyme(bars):
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
	return rhymes


if __name__ == "__main__":
	bars = getAllBars("lyrics.txt")
	#print bars
	rhymes = getAllRhyme(bars)
	print rhymes