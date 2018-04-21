# -*- coding: utf-8 -*-
import codecs
import re


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

    print 'q(', interestWord, '|', previousWords, ') =', 'lambda1 x qml(', interestWord, '|', previousWords, ') +', 'lambda2 x qml(', interestWord, '|', lastPrevWord, ') +', 'lambda3 x qml(', interestWord, ')',
    print '=', lambda1, 'x', qml3rd, '+', lambda2, 'x', qml2nd, '+', lambda3, 'x', qml1st,

    ret = lambda1 * qml3rd + lambda2 * qml2nd + lambda3 * qml1st
    print '=', ret
    print ''

    return ret


def p(sentence, dictionary, totalWordsWithSTOP):
    sentence = '* * ' + sentence.lower() + ' STOP'
    wordList = sentence.split(' ')
    p = 1
    for ix in range(2, len(wordList)):
        previousWords = wordList[ix - 2] + ' ' + wordList[ix - 1]
        interestWord = wordList[ix]
        p *= qLinearInterpolation(previousWords,
                                  interestWord, dictionary, totalWordsWithSTOP)
    return p


dictionary, numSentences, numWords = getDictionary('./training_data')
addTokenSecondOrder(dictionary, './training_data')
addTokenThirdOrder(dictionary, './training_data')
addSTOPToken(dictionary, './training_data')
# for vocab, cnt in dictionary.items():
#     print vocab, cnt

sentence = raw_input('\nINPUT SENTENCE: ')
sentence = unicode(sentence, 'utf-8')
prob = p(sentence, dictionary, numSentences + numWords)
print 'p(sentence) =', prob
