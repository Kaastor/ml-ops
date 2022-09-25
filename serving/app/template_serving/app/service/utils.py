import json
import os
from pathlib import Path
from typing import List

DIR = str(Path(os.path.realpath(__file__)).parent.parent)
MODEL_ONNX_FILE = 'model.onnx'

ENCODING_MAX_LEN = 192  # todo: parametrize somehow?
OOV_TOKEN = '<OOV>'
OOV_TOKEN_ID = 1
PAD_TOKEN = '<PAD>'
PAD_TOKEN_ID = 0


def load_json(path):
    with open(path, 'r') as fp:
        file = json.load(fp)
    return file


# todo: use AI.SCRIPTSET inside prediction DAG?
def tokenize_url(sentence: str, vocab):
    return _tokenize_sentence([char for char in sentence], vocab, ENCODING_MAX_LEN)


def _tokenize_sentence(tokenized_sentence: List[str], vocab, encoding_max_len=200):
    """
    :param encoding_max_len: length of the encoding, not filled elements will be padded
    :param tokenized_sentence: list of string tokens
    :param vocab: dict: {'token': id}
    """
    encoded = []
    for token in tokenized_sentence[:encoding_max_len]:
        if token in vocab:
            encoding = vocab[token]
        else:
            encoding = OOV_TOKEN_ID
        encoded.append(encoding)
    i = len(encoded)
    while i < encoding_max_len:
        encoded.append(PAD_TOKEN_ID)
        i += 1

    return encoded
