import pronouncing
import re
import math

from collections import defaultdict

BUILDTESTFILE = False
DISTRFILE = "rhymeDistribution.txt"
LYRICSFILE = "lyrics.txt"
RHYMESFILE = "rhymes.txt"

def getAllsong():
    songs = [[]]
    with open(LYRICSFILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                songs.append([])
                continue
            songs[-1].append(line)
    return songs

def getDistribution(rhymes, song):
    rhymeDict = defaultdict(float)
    for rh in rhymes:
        rhymeDict[rh] = 0.0

    counter = 0.0

    for bar in song:
        lastWord = bar.split(" ")[-1].lower()
        if not lastWord.isalpha():
            lastWord = re.sub(r"\W+", '', lastWord)
        # Skip the word that does not qualifiy for the rhyme generation
        if not lastWord.isalpha() or len(lastWord)<2:
            continue

        rhymesList = [word.encode('UTF8')[-2:] for word in pronouncing.rhymes(lastWord)]
        if rhymesList:
            rhymeEnd = max(set(rhymesList), key=rhymesList.count)
        else:
            rhymeEnd = lastWord[-2:]
        if rhymeEnd in rhymeDict:
            rhymeDict[rhymeEnd] += 1.0
            counter += 1.0

    # Normalize
    if counter:
        for key in rhymeDict:
            rhymeDict[key]/=counter


    return rhymeDict

def genDistribution():
    allrhymes = []
    with open(RHYMESFILE) as f:
        for line in f:
            line = line.strip()
            allrhymes.append(line)

    songs = getAllsong()
    allDict = []

    for song in songs:
        if song:
            distriDict = getDistribution(allrhymes, song)
            allDict.append(distriDict)

    # Write result to file
    f = open(DISTRFILE, 'w')
    for dic in allDict:
        for key in sorted(dic):
            f.write(key + ' ' + str(dic[key]) + '\n')
        f.write('\n')

    f.close()


def getCosineSim(testDict, trainDict):
    sumA = 0.0
    sumB = 0.0
    sumAB = 0.0
    #print testDict
    #print trainDict

    for key in testDict:
        sumA += testDict[key]**2
        sumB += trainDict[key]**2
        sumAB += testDict[key]*trainDict[key]

    return sumAB/(math.sqrt(sumA) * math.sqrt(sumB))


def findSimilarity(fileName):
    # Parse the input file
    allrhymes = []
    with open(RHYMESFILE) as f:
        for line in f:
            line = line.strip()
            allrhymes.append(line)

    song = []
    with open(fileName) as f:
        for line in f:
            line = line.strip()
            if line:
                song.append(line)

    testDict = getDistribution(allrhymes, song)

    # Parse all lyrics density distribution
    trainDicts = [defaultdict(float)]
    with open(DISTRFILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                trainDicts.append(defaultdict(float))
                continue
            key, prop = line.split(' ')
            trainDicts[-1][key] = float(prop)

    sims = []
    for trainDic in trainDicts:
        if trainDic:
            prop = getCosineSim(testDict, trainDic)
            sims.append(prop)
    return max(sims)



if __name__ == "__main__":
    if BUILDTESTFILE:
        genDistribution()
    print findSimilarity('test.txt')
