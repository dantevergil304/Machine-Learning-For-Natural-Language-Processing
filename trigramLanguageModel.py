# -*- coding: utf-8 -*-
import codecs
import re


def getWords(training_data_path):
    file = codecs.open(training_data_path, encoding='utf-8')
    words = []
    for text in file.readlines():
        terms = re.split('\s|[\W0-9]+', text, flags=re.UNICODE)
        terms = filter(None, terms)
        words += terms
    ret = [word.lower() for word in words]
    ret.append('STOP')
    return ret


def getSetForDiscount(previousWords, wordList, dictionary):
    # Calculate two sets A(v) and B(v) for discounting method
    # where:
    # - A(previous words) = {w: #(v, w) > 0}
    # - B(previous words) = {w: #(v, w) = 0}
    A = set()
    B = set()
    for w in wordList:
        term = previousWords + ' ' + w
        if term in dictionary:
            A.add(w)
        else:
            B.add(w)
    return A, B


def missingProbabilityMass(previousWords, dictionary, Aset):
    total = 0
    for w in Aset:
        total += (dictionary[previousWords + ' ' + w] -
                  0.5) / float(dictionary[previousWords])
    return 1 - total


def qDiscountingBigram(previousWords, interestWord, dictionary, wordList):
    Aset, Bset = getSetForDiscount(previousWords, wordList, dictionary)
    if interestWord in Aset:
        return (dictionary[previousWords + ' ' + interestWord] - 0.5) / float(dictionary[previousWords])
    elif interestWord in Bset:
        # missing probability mass
        mpm = missingProbabilityMass(previousWords, dictionary, Aset)

        total = 0
        for t in Bset:
            total += dictionary[t]

        return mpm * dictionary[interestWord] / float(total)


def qDiscountingTrigram(previousWords, interestWord, dictionary, wordList):
    firstword = previousWords.split(' ')[0]
    secondword = previousWords.split(' ')[1]
    Aset, Bset = getSetForDiscount(previousWords, wordList, dictionary)

    print 'qd(', interestWord, '|', previousWords, ') =',

    if interestWord in Aset:
        ret = (dictionary[previousWords + ' ' + interestWord] -
               0.5) / float(dictionary[previousWords])

        print '#(', firstword, ',', secondword, ',', interestWord, ')* /', '#(', firstword, ',', secondword, ') =', ret
        print ''

        return ret
    elif interestWord in Bset:
        # missing probability mass
        mpm = missingProbabilityMass(previousWords, dictionary, Aset)

        total = 0
        for w in Bset:
            total += qDiscountingBigram(secondword, w, dictionary, wordList)

        ret = mpm * \
            qDiscountingBigram(secondword, interestWord,
                               dictionary, wordList) / float(total)

        print 'alpha(', firstword, ',', secondword, ') x qd(', interestWord, '|', secondword, ') / Sigma(qd( w |', secondword, ') where w is all words in B) =', ret
        print ''

        return ret


def getDictionary(training_data_path):
    file = codecs.open(training_data_path, encoding='utf-8')
    vocabs = {}

    numSentences = 0
    numWords = 0
    for text in file.readlines():
        # First-order terms
        terms = re.split('\s|[\W0-9]+', text, flags=re.UNICODE)
        terms = filter(None, terms)  # remove empty string

        numSentences += 1
        numWords += len(terms)

        for term in terms:
            term = term.lower()
            if term not in vocabs:
                vocabs[term] = 1
            else:
                vocabs[term] += 1

        # Second-order terms
        for ix in range(len(terms) - 1):
            term = terms[ix].lower() + ' ' + terms[ix + 1].lower()
            if term not in vocabs:
                vocabs[term] = 1
            else:
                vocabs[term] += 1

        # Third-order terms
        for ix in range(len(terms) - 2):
            term = terms[ix].lower() + ' ' + terms[ix + 1].lower() + \
                ' ' + terms[ix + 2].lower()
            if term not in vocabs:
                vocabs[term] = 1
            else:
                vocabs[term] += 1

    # for vocab, cnt in vocabs.items():
    #     print vocab, cnt

    file.close()
    return vocabs, numSentences, numWords


def addSTOPToken(dictionary, trainin_data_path):
    file = codecs.open(trainin_data_path, encoding='utf-8')
    for line in file.readlines():
        if line == '\n':
            continue
        term = 'STOP'
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1
    file.close()


def addTokenSecondOrder(dictionary, training_data_path):
    file = codecs.open(training_data_path, encoding='utf-8')
    for line in file.readlines():
        # Skip empty line
        if line == '\n':
            continue
        terms = re.split('[\W0-9]+', line, flags=re.UNICODE)
        terms = filter(None, terms)

        # Add '*' Token
        term = '*'
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

        # Add '* word' Token
        firstword = terms[0]
        term = '* ' + firstword.lower()
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

        # Add 'word STOP' Token
        lastword = terms[-1]
        term = lastword.lower() + ' ' + 'STOP'
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

    file.close()


def addTokenThirdOrder(dictionary, training_data_path):
    file = codecs.open(training_data_path, encoding='utf-8')
    for line in file.readlines():
        # Skip empty line
        if line == '\n':
            continue
        terms = re.split('[\W0-9]+', line, flags=re.UNICODE)
        terms = filter(None, terms)

        # Add '* *' Token
        term = '* *'
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

        # Add '* * word' Token
        firstword = terms[0]
        term = '* * ' + firstword.lower()
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

        # Add '* word word' Token
        secondword = terms[1]
        term = '* ' + firstword.lower() + ' ' + secondword.lower()
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

        # Add 'word word STOP' Token
        penultimateword = terms[-2]
        lastword = terms[-1]
        term = penultimateword + ' ' + lastword.lower() + ' ' + 'STOP'
        if term not in dictionary:
            dictionary[term] = 1
        else:
            dictionary[term] += 1

    file.close()


def qLinearInterpolation(previousWords, interestWord, dictionary, totalWordsWithSTOP):
    lambda1 = 0.4
    lambda2 = 0.3
    lambda3 = 0.3

    qml3rd = dictionary.get(previousWords + ' ' +
                            interestWord, 0) / float(dictionary.get(previousWords, 1))

    lastPrevWord = previousWords.split(' ')[-1]
    qml2nd = dictionary.get(lastPrevWord + ' ' +
                            interestWord, 0) / float(dictionary.get(lastPrevWord, 1))

    qml1st = dictionary.get(interestWord, 0) / float(totalWordsWithSTOP)

    # Print info
    print 'q(', interestWord, '|', previousWords, ') =', 'lambda1 x qml(', interestWord, '|', previousWords, ') +', 'lambda2 x qml(', interestWord, '|', lastPrevWord, ') +', 'lambda3 x qml(', interestWord, ')',
    print '=', lambda1, 'x', qml3rd, '+', lambda2, 'x', qml2nd, '+', lambda3, 'x', qml1st,

    ret = lambda1 * qml3rd + lambda2 * qml2nd + lambda3 * qml1st
    print '=', ret
    print ''

    return ret


def pLinearInterpolation(sentence, dictionary, totalWordsWithSTOP):
    sentence = '* * ' + sentence.lower() + ' STOP'
    wordList = sentence.split(' ')
    p = 1
    for ix in range(2, len(wordList)):
        previousWords = wordList[ix - 2] + ' ' + wordList[ix - 1]
        interestWord = wordList[ix]
        p *= qLinearInterpolation(previousWords,
                                  interestWord, dictionary, totalWordsWithSTOP)
    return p


def pDiscounting(sentence, dictionary, wordList):
    sentence = '* * ' + sentence.lower() + ' STOP'
    words = sentence.split(' ')
    p = 1
    for ix in range(2, len(words)):
        previousWords = words[ix - 2] + ' ' + words[ix - 1]
        interestWord = words[ix]
        k = qDiscountingTrigram(previousWords,
                                interestWord, dictionary, wordList)
        p *= k
    return p


wordList = getWords('./training_data_2')
dictionary, numSentences, numWords = getDictionary('./training_data_2')
addTokenSecondOrder(dictionary, './training_data_2')
addTokenThirdOrder(dictionary, './training_data_2')
addSTOPToken(dictionary, './training_data_2')

sentence = raw_input('\nINPUT SENTENCE: ')
sentence = unicode(sentence, 'utf-8')
prob = pDiscounting(sentence, dictionary, wordList)
print 'p(sentence) =', prob
# print qDiscountingBigram(u'lá', u'rừng', dictionary, wordList)
# print qDiscountingBigram(u'rừng', 'STOP', dictionary, wordList)
# print qDiscountingBigram('*', u'lá', dictionary, wordList)
# print qDiscountingTrigram('* *', u'nước', dictionary, wordList)
# print qDiscountingTrigram(u'* nước', u'ao', dictionary, wordList)
# print qDiscountingTrigram(u'trong veo', 'STOP', dictionary, wordList)
