from collections import namedtuple

TAG = namedtuple('Tag', 'char index open void')

FORMAT_CHARS = set(['_', '`', '>', '*'])

HTML_TAGS = {'_': {'open': '<span style="font-style: italic;">', 'close': '</span>'},
             '>': {'open': '<blockquote>', 'close': '</blockquote>'},
             '**': {'open': '<b>', 'close': '</b>'},
             '`': {'open': '<code>', 'close': '</code>'},
             '```': {'open': '<pre><code>', 'close': '</code></pre>'}}


class FilterStates():
    """
    for tracking states during text filtering
    """

    def __init__(self, string):

        self.tags = []

        self.tag_states = {'_': False,
                           '`': False,
                           '>': False,
                           '**': False,
                           '```': False}

        self.star_count, self.tick_count = 0, 0

        self.string_list = list(string)

    def __repr__(self):

        return self.tags, ''.join(self.string_list)


def blog_filter(string):

    states = FilterStates(string)

    for index, char in enumerate(states.string_list):

        if char in FORMAT_CHARS:

            inspect_char(states, char, index)

    html = insert_tags(states, ''.join(states.string_list))

    return html


def inspect_char(states, char, index):

    if char == '*':

        states.star_count += 1
        states.tick_count = 0

        if states.star_count == 2:
            make_tag(states, '**', index-1, states.tag_states['```'])

    elif char == '`':

        states.tick_count += 1
        states.star_count = 0

        if states.tick_count == 1 and states.string_list[index+1] != '`':
            make_tag(states, char, index, states.tag_states['```'])

        elif states.tick_count == 3:
            make_tag(states, '```', index-2, False)

    else:

        make_tag(states, char, index, states.tag_states['```'])


def make_tag(states, char, index, void):

    states.tag_states[char] = not states.tag_states[char]
    tag = TAG(char, index, states.tag_states[char], void)
    states.tags.append(tag)
    states.star_count, states.tick_count = 0, 0


def insert_tags(states, string):

    html_text = ''

    prev = 0

    for tag in states.tags:

        if tag.void is False:

            if tag.open is True:
                html_tag = HTML_TAGS[tag.char]['open']
            else:
                html_tag = HTML_TAGS[tag.char]['close']

            html_text += string[prev:tag.index] + html_tag

            prev = tag.index + len(tag.char)

    html_text += string[prev:]

    return html_text
