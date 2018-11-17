from collections import namedtuple
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

TAG = namedtuple('Tag', 'tag_type index open')

FORMAT_CHARS = {'_': 'italic', '`': 'code', '>': 'quote', '*': 'bold'}

HTML_TAGS = {'italic': {True: '<span style="font-style: italic;">', False: '</span>'},
             'quote': {True: '<blockquote>', False: '</blockquote>'},
             'bold': {True: '<b>', False: '</b>'},
             'code': {True: '<code>', False: '</code>'},
             'escape': {True: '', False: ''}
             }


class Filter():
    """
    used for tracking the open and closed state of tags
    while determining tag locations within input text
    """

    def __init__(self, string):

        self.tags = []

        self.open_states = {'italic': False,
                            'code': False,
                            'quote': False,
                            'bold': False,
                            'code_block': False,
                            'escape': False}

        self.star_count, self.tick_count = 0, 0

        self.text = string

        self.text_list = list(string)

    def __repr__(self):

        return self.tags, self.text


def blog_filter(raw_text):

    filter = Filter(raw_text)

    for index, char in enumerate(filter.text_list):

        if char in FORMAT_CHARS:
            tag_type = FORMAT_CHARS[char]
            count_char(tag_type, index, filter)
        else:
            filter.star_count, filter.tick_count = 0, 0

    html = insert_tags(filter)

    if filter.tags:
        return html
    else:
        return raw_text


def count_char(tag_type, index, filter):

    within_code_block = filter.open_states['code_block']
    within_code_inline = filter.open_states['code']
    within_code = within_code_block or within_code_inline

    if tag_type == 'bold':

        filter.star_count += 1
        filter.tick_count = 0

        if filter.star_count == 2 and not within_code:
            if filter.text_list[index-2] == '\\':
                make_tag('escape', index-2, filter)
            else:
                make_tag(tag_type, index-1, filter)

    elif tag_type == 'code':

        filter.tick_count += 1
        filter.star_count = 0

        if filter.tick_count == 1 and filter.text_list[index+1] != '`':
            if not within_code_block:
                if filter.text_list[index-1] == '\\':
                    make_tag('escape', index-1, filter)
                else:
                    make_tag(tag_type, index, filter)

        elif filter.tick_count == 3:
            if filter.text_list[index-3] == '\\':
                make_tag('escape', index-3, filter)
            else:
                make_tag('code_block', index-2, filter)

    elif not within_code:

        if filter.text_list[index-1] == '\\':
            make_tag('escape', index-1, filter)
        else:
            make_tag(tag_type, index, filter)


def make_tag(tag_type, index, filter):

    filter.open_states[tag_type] = not filter.open_states[tag_type]

    tag = TAG(tag_type, index, filter.open_states[tag_type])
    filter.tags.append(tag)

    filter.star_count, filter.tick_count = 0, 0


def insert_tags(filter):

    raw_text = filter.text

    html_text = ''

    previous_tag_index = 0

    for current_index, tag in enumerate(filter.tags):

        if tag.tag_type == 'code_block':

            if tag.open:

                tags_slice_start = current_index

                html_text += raw_text[previous_tag_index:tag.index]

                filter.open_states['code_block'] = True

            else:

                escaped_text = remove_escapes(
                               filter.tags[tags_slice_start:current_index+1],
                               raw_text)

                html_text += '</p></div>' + \
                             highlight(escaped_text, PythonLexer(), HtmlFormatter()) + \
                             '<div><p>'

                filter.open_states['code_block'] = False

            index_offset = 3

            previous_tag_index = tag.index + index_offset

        else:

            html_tag = HTML_TAGS[tag.tag_type][tag.open]

            if not (tag.tag_type == 'escape' and filter.open_states['code_block']):
                html_text += raw_text[previous_tag_index:tag.index] + html_tag

            if tag.tag_type == 'bold':
                index_offset = 2
            else:
                index_offset = 1

            previous_tag_index = tag.index + index_offset

    html_text += raw_text[previous_tag_index:]

    return html_text


def remove_escapes(tags, raw_text):

    escaped_text = ''

    previous_index = tags[0].index + 3

    for tag in tags:

        if tag.tag_type == 'escape':
            escaped_text += raw_text[previous_index:tag.index]
            previous_index = tag.index + 1

    escaped_text += raw_text[previous_index:tags[-1].index]

    return escaped_text
