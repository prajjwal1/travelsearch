import re
from unidecode import unidecode


def remove_non_alphanumeric(txt):
    """ Remove all non-alphanumeric characters, except space, from the text
    """
    return re.sub(r'[^a-zA-Z0-9 ]+', '', txt)


def transliterate(txt):
    """ Transliterate foreign characters into its Latin spelling.
    For example, '\u5317\u4EB0' will be transliterated to 'Bei Jing'
    """
    return unidecode(txt)

def collapse_white_spaces(txt):
    """Collapse multiple white spaces into one white space
    """
    clean_txt = ''
    prev = None
    for c in txt:
        if c == ' ' and prev == ' ':
            continue
        else:
            clean_txt += c
        prev = c
    return clean_txt


def connect_lines(txt, line_sep='\n'):
    """ This happens when you crawl text from a webpage and
    they have random breaking lines mid-sentence.
    This function is to connect those lines.
    Two consecutive lines are separated by line_sep.
    """
    lines = txt.split('\n')

    result, curr = '', ''
    for line in lines:
        line = line.strip()
        if not line:
            if curr:
                result += (curr + '\n')
            result += line_sep
            curr = ''
        else:
            curr += (line + ' ')

    return result + curr


def clean_text(txt):
    txt = txt.strip()
    if not txt:
        return ''
    txt = remove_non_alphanumeric(txt)
    txt = transliterate(txt)
    txt = collapse_white_spaces(txt)
    txt = connect_lines(txt)
    return txt

