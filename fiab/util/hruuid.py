import random

ADJECTIVES = [
    'adaptable',
    'adventurous',
    'affectionate',
    'agreeable',
    'amazing',
    'amusing',
    'ambitious',
    'appreciated',
    'authentic',
    'aware',
    'awesome',
    'balanced',
    'beautiful',
    'blessed',
    'blissful',
    'boisterous',
    'brave',
    'bright',
    'brilliant',
    'calm',
    'capable',
    'charming',
    'cheerful',
    'clever',
    'compassionate',
    'confident',
    'conscientious',
    'considerate',
    'cool',
    'cooperative',
    'courageous',
    'courteous',
    'creative',
    'curious',
    'daring',
    'decisive',
    'deep',
    'delightful',
    'determined',
    'devoted',
    'diligent',
    'diplomatic',
    'dutiful',
    'dynamic',
    'eager',
    'earnest',
    'efficient',
    'empowered',
    'energetic',
    'enthusiastic',
    'excitable',
    'experienced',
    'exuberant',
    'fabulous',
    'fearless',
    'flexible',
    'focused',
    'friendly',
    'funny',
    'generous',
    'genuine',
    'gentle',
    'giving',
    'great',
    'gregarious',
    'grounded',
    'happy',
    'helpful',
    'hopeful',
    'humorous',
    'imaginative',
    'impressive',
    'important',
    'innovative',
    'involved',
    'inspiring',
    'intelligent',
    'interesting',
    'inventive',
    'irresistible',
    'jovial',
    'joyful',
    'joyous',
    'just',
    'keen',
    'kind',
    'kooky',
    'knowledgeable',
    'lively',
    'logical',
    'lovable',
    'lovely',
    'loyal',
    'magical',
    'magnificent',
    'marvelous',
    'mature',
    'methodical',
    'mindful',
    'modest',
    'motivated',
    'musical',
    'natural',
    'nice',
    'obliging',
    'observant',
    'openhearted',
    'optimistic',
    'orderly',
    'organised',
    'outgoing',
    'outspoken',
    'outstanding',
    'passionate',
    'peaceful',
    'persistent',
    'playful',
    'pleasant',
    'polite',
    'popular',
    'positive',
    'powerful',
    'practical',
    'precious',
    'proactive',
    'proficient',
    'proud',
    'punctual',
    'radiant',
    'realistic',
    'reassuring',
    'rational',
    'reliable',
    'resourceful',
    'respectful',
    'responsible',
    'resilient',
    'sassy',
    'sensational',
    'sensitive',
    'sensible',
    'sentimental',
    'serene',
    'sincere',
    'sharp',
    'smart',
    'sophisticated',
    'soulful',
    'spirited',
    'strong',
    'successful',
    'sweet',
    'sympathetic',
    'tactful',
    'talented',
    'thankful',
    'thrilled',
    'tidy',
    'thoughtful',
    'tolerant',
    'tranquil',
    'unaffected',
    'unassuming',
    'understanding',
    'unique',
    'uplifted',
    'valuable',
    'versatile',
    'vibrant',
    'vigilant',
    'vivacious',
    'warm',
    'warmhearted',
    'watchful',
    'welcoming',
    'wise',
    'willing',
    'witty',
    'wonderful',
    'worthy',
    'zealous',
]

NAMES = [
    'ampere', # https://en.wikipedia.org/wiki/Andr%C3%A9-Marie_Amp%C3%A8re
    'bennett', # A friend
    'byott', # A friend
    'cookie', # Our guinea pig Cookie
    'euclid', # https://en.wikipedia.org/wiki/Euclid
    'euler', # https://en.wikipedia.org/wiki/Leonhard_Euler
    'gates', # https://en.wikipedia.org/wiki/Bill_Gates
    'gingging', # An old guinea pig from my childhood
    'grabarczyk', # friend
    'hernandez', # A friend
    'hopper', # Our guinea pig Hopper, named after Grace Hopper
    'huang', # https://en.wikipedia.org/wiki/Jensen_Huang
    'ip', # A friend
    'kittio', # An old cat from my childhood
    'lee', # my SO
    'leroy', # An old cat from my childhood
    'lovelace', # https://en.wikipedia.org/wiki/Ada_Lovelace
    'lucy', # My parent's cat
    'mango', # Our guinea pig Mango
    'marking', # A friend
    'massie', # A friend
    'musk', # https://en.wikipedia.org/wiki/Elon_Musk
    'ng', # https://en.wikipedia.org/wiki/Andrew_Ng
    'obama', # https://en.wikipedia.org/wiki/Barack_Obama
    'pengra', # myself
    'pumpkin', # An old guinea pig from my childhood
    'sanders', # https://en.wikipedia.org/wiki/Bernie_Sanders
    'sanger', # https://en.wikipedia.org/wiki/Larry_Sanger
    'setzer', # A friend
    'sharp', # A friend
    'shimogawa', # A friend
    'shuttleworth', # https://en.wikipedia.org/wiki/Mark_Shuttleworth
    'torvalds', # https://en.wikipedia.org/wiki/Linus_Torvalds
    'truman', # Our guinea pig Truman, named after Bess Truman
    'turing', # https://en.wikipedia.org/wiki/Alan_Turing,
    'um', # A friend
    'uzi', # Our guinea pig Uzi, named after the nation Uzbekistan
    'volta', # https://en.wikipedia.org/wiki/Alessandro_Volta
    'wales', # https://en.wikipedia.org/wiki/Jimmy_Wales
    'yee', # A friend
    'young', # A friend
    'yuumei', # https://www.yuumeiart.com/
]

HEX = [
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9'
]

def hruuid(sep='-') -> str:
    adj = random.choice(ADJECTIVES)
    name = random.choice(NAMES)
    add = str(hex(random.randint(1118481,16777215)))[2:]
    return sep.join((adj, name, add))