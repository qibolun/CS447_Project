import random

from const import *
from dataProcess import *
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers.core import Dense



def buildModel(loadParamFromFile = False):
    model = Sequential()
    model.add(LSTM(4, input_shape=(2, 2), return_sequences=True))
    for i in range(DEPTH):
        model.add(LSTM(8, return_sequences=True))
    model.add(LSTM(2, return_sequences=True))
    model.summary()
    model.compile(optimizer='rmsprop',loss='mse')
    if loadParamFromFile:
        model.load_weights(MODELFILE)
    return model


def composeRap(bars, rhymes, model):
    originalBars = getAllBars(LYRICSFILE)
    startingIdx = random.randint(0, len(originalBars)-2)
    # Randomly pick two lines from original lyrics as starting point
    startingLines = originalBars[startingIdx:startingIdx+2]

    startingVector = []
    for bar in startingLines:
        startingVector.append((syllables(bar), ryhmeIndex(bar, rhymes)))
    # Generate True starting point
    startingVector = model.predict(np.array([startingVector]).flatten().reshape(1,2,2))
    rapVector = [startingVector]
    for i in range(100):
        rapVector.append(model.predict(np.array([rapVector[-1]]).flatten().reshape(1,2,2)))

    return rapVector


def calculatePenalty(bars, standardLine, penaltyIndex=0.2):
    # calculate the penalty score last word of all bars deviate from standline
    penalty = 0
    standardWord = standardLine.strip('?!,.').split(" ")[-1]
    for bar in bars:
        lastWord = bar.strip('?!,.').split(" ")[-1]
        if lastWord == standardWord:
            penalty += penaltyIndex
    return penalty


def calculateScore(vector, syllables, rhyme, rhymeListLen, penalty):
    if not rhyme:
        rhyme = 0.0
    desiredSyllables = float(vector[0]) * MAXSYLLABLES
    desiredRhyme = float(vector[1]) * rhymeListLen
    return 1.0 - (abs(desiredSyllables - float(syllables)) +
                  abs(desiredRhyme - float(rhyme))) - penalty


def convertVectorToSong(rapVector, generatedLyrics, rhymes):
    generatedData = []
    rhymeListLen = len(rhymes)
    for bar in generatedLyrics:
        generatedData.append([bar, syllables(bar), ryhmeIndex(bar, rhymes)])

    rap = []
    unfoldVector = []
    for vector in rapVector:
        unfoldVector.append(list(vector[0][0]))
        unfoldVector.append(list(vector[0][1]))

    for vector in unfoldVector:
        scoreList = []
        for bar, syllable, rhymeindex in generatedData:
            if len(rap) != 0:
                penalty = calculatePenalty(rap, bar)
            else:
                penalty = 0
            totalScore = calculateScore(vector, syllable, rhymeindex, rhymeListLen, penalty)
            scoreList.append([bar, totalScore])


        maxScore = max([float(score[1]) for score in scoreList])
        for bar, score in scoreList:
            if score == maxScore:
                rap.append(bar)
                for data in generatedData:
                    if bar == data[0]:
                        generatedData.remove(data)
                        break
                break
    return rap


def train(x_data, y_data, model):
    model.fit(np.array(x_data, dtype=np.float64), np.array(y_data, dtype=np.float64),
              batch_size=2,
              epochs=5,
              verbose=1)
    model.save_weights(MODELFILE)



if __name__ == "__main__":
    trainModel = True

    model = buildModel(loadParamFromFile=False)
    print ("finish building the model")
    bars = getAllBars(LYRICSFILE)
    print ("finish generate bars from lyric file")
    rhymes = getAllRhyme(bars, readFromFile=True)
    print ("finish generate rhymes from lyric file")
    if trainModel:
        xData, yData = buildDataSet(bars, rhymes)
        import pdb; pdb.set_trace()
        print ("finish building the dataset")
        train(xData, yData, model)
        print ("finish trainning the model")
    generatedBars = generateLyrics(LYRICSFILE)
    print ("finish generate new bars from exist lyric")
    rapVector = composeRap(generatedBars, rhymes, model)
    print ("finish generate lyric vector using model")
    lyric = convertVectorToSong(rapVector, generatedBars, rhymes)
    print lyric
    for line in lyric:
        print lyric
