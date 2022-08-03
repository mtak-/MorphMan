# -*- coding: utf-8 -*-
import re
import os
from functools import lru_cache

from .deps.hunspell import hunspell
from .deps.hunspell import stemmer

from .morphemes import Morpheme
from .deps.zhon.hanzi import characters
from .mecab_wrapper import getMorphemesMecab, getMecabIdentity
from .deps.jieba import posseg

####################################################################################################
# Base Class
####################################################################################################

class Morphemizer:
    def __init__(self):
        pass
    
    @lru_cache(maxsize=131072)
    def getMorphemesFromExpr(self, expression):
        # type: (str) -> [Morpheme]
        
        morphs = self._getMorphemesFromExpr(expression)
        return morphs
    
    def _getMorphemesFromExpr(self, expression):
        # type: (str) -> [Morpheme]
        """
        The heart of this plugin: convert an expression to a list of its morphemes.
        """
        return []

    def getDescription(self):
        # type: () -> str
        """
        Returns a single line, for which languages this Morphemizer is.
        """
        return 'No information available'

    def getName(self):
        # type: () -> str
        return self.__class__.__name__


####################################################################################################
# Morphemizer Helpers
####################################################################################################

morphemizers = None
morphemizers_by_name = {}

def getAllMorphemizers():
    # type: () -> [Morphemizer]
    global morphemizers
    if morphemizers is None:
        morphemizers = [SpaceMorphemizer(), RussianMorphemizer(), BasqueMorphemizer(), MecabMorphemizer(), JiebaMorphemizer(), CjkCharMorphemizer()]

        for m in morphemizers:
            morphemizers_by_name[m.getName()] = m

    return morphemizers

def getMorphemizerByName(name):
    # type: (str) -> Optional(Morphemizer)
    getAllMorphemizers()
    return morphemizers_by_name.get(name, None)


####################################################################################################
# Mecab Morphemizer
####################################################################################################

space_char_regex = re.compile(' ')

class MecabMorphemizer(Morphemizer):
    """
    Because in japanese there are no spaces to differentiate between morphemes,
    a extra tool called 'mecab' has to be used.
    """

    def _getMorphemesFromExpr(self, expression):
        # Remove simple spaces that could be added by other add-ons and break the parsing.
        if space_char_regex.search(expression):
            expression = space_char_regex.sub('', expression)

        return getMorphemesMecab(expression)

    def getDescription(self):
        try:
            identity = getMecabIdentity()
        except:
            identity = 'UNAVAILABLE'
        return 'Japanese ' + identity


####################################################################################################
# Space Morphemizer
####################################################################################################

class SpaceMorphemizer(Morphemizer):
    """
    Morphemizer for languages that use spaces (English, German, Spanish, ...). Because it is
    a general-use-morphemizer, it can't generate the base form from inflection.
    """

    def _getMorphemesFromExpr(self, expression):
        word_list = [word.lower()
                     for word in re.findall(r"\b[^\s\d]+\b", expression, re.UNICODE)]
        return [Morpheme(word, word, word, word, 'UNKNOWN', 'UNKNOWN') for word in word_list]

    def getDescription(self):
        return 'Language w/ Spaces'


####################################################################################################
# Basque/hunspell Morphemizer
####################################################################################################
class BasqueMorphemizer(Morphemizer):
    """
    Morphemizer for Basque using hunspell and freedesktop/libreoffice dictionaries.
    """
    hspell = hunspell.HunSpell(
        os.path.join(stemmer.HUNSPELL_DIR, 'eu_ES.dic'),
        os.path.join(stemmer.HUNSPELL_DIR, 'eu_ES.aff'))

    def getMorphemesFromExpr(self, e): # Str -> [Morpheme]
        wordList = [word for word in re.findall(r"\w+", e, re.UNICODE)]
        morphemes = []
        for word in wordList:
            (word, stem) = stemmer.stemmer(self.hspell, word)
            morphemes.append(Morpheme(stem, stem, word, stem, 'UNKNOWN', 'UNKNOWN'))
        return morphemes

    def getDescription(self):
        return 'Basque Hunspell'


####################################################################################################
# Russian/hunspell Morphemizer
####################################################################################################
class RussianMorphemizer(Morphemizer):
    """
    Morphemizer for Russian using hunspell and freedesktop/libreoffice dictionaries.
    """
    hspell = hunspell.HunSpell(
        os.path.join(stemmer.HUNSPELL_DIR, 'ru_RU.dic'),
        os.path.join(stemmer.HUNSPELL_DIR, 'ru_RU.aff'))

    def getMorphemesFromExpr(self, e): # Str -> [Morpheme]
        wordList = [word for word in re.findall(r"\w+", e, re.UNICODE)]
        morphemes = []
        for word in wordList:
            (word, stem) = stemmer.stemmer(self.hspell, word)
            morphemes.append(Morpheme(stem, stem, word, stem, 'UNKNOWN', 'UNKNOWN'))
        return morphemes

    def getDescription(self):
        return 'Russian Hunspell'


####################################################################################################
# CJK Character Morphemizer
####################################################################################################

class CjkCharMorphemizer(Morphemizer):
    """
    Morphemizer that splits sentence into characters and filters for Chinese-Japanese-Korean logographic/idiographic
    characters.
    """

    def _getMorphemesFromExpr(self, expression):
        return [Morpheme(character, character, character, character, 'CJK_CHAR', 'UNKNOWN') for character in
                re.findall('[%s]' % characters, expression)]

    def getDescription(self):
        return 'CJK Characters'


####################################################################################################
# Jieba Morphemizer (Chinese)
####################################################################################################

class JiebaMorphemizer(Morphemizer):
    """
    Jieba Chinese text segmentation: built to be the best Python Chinese word segmentation module.
    https://github.com/fxsjy/jieba
    """

    def _getMorphemesFromExpr(self, expression):
        # remove all punctuation
        expression = ''.join(re.findall('[%s]' % characters, expression))
        return [Morpheme(m.word, m.word, m.word, m.word, m.flag, 'UNKNOWN') for m in
                posseg.cut(expression)]  # find morphemes using jieba's POS segmenter

    def getDescription(self):
        return 'Chinese'
