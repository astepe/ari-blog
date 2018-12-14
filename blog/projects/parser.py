import re
from PyPDF2 import PdfFileReader
from collections import namedtuple


class ChemicalData:

    CATEGORY = namedtuple('category', 'name regex')

    CATEGORIES = (
        CATEGORY('Product Name', re.compile(r"[P|p]roduct (([N|n]ame)|([D|d]escription)).*?(?P<data>[^ :\n].*?)(P|C)", re.DOTALL)),
        CATEGORY('Flash Point', re.compile(r"([F|f]lash [P|p]oint)([\s:\d.°C]{0,18}\s{0,8}\(\s{0,4})?(?P<data>[0-9.]*\s*°?\s?F)?", re.DOTALL)),
        CATEGORY('Specific Gravity', re.compile(r"([R|r]elative [D|d]ensity|[S|s]pecific [G|g]ravity)\s*(?P<data>[0-9.]*\s)?", re.DOTALL)),
        CATEGORY('CAS #', re.compile(r"CAS.*?(?P<data>\d{2,7}\n*?-\n*?\d{2}\n*?-\n*?\d)", re.DOTALL)),
        CATEGORY('NFPA Fire', re.compile(r"NFPA.*?[F|f]ire.*?(?P<data>[0-4])", re.DOTALL)),
        CATEGORY('NFPA Health', re.compile(r"NFPA.*?[H|h]ealth.*?(?P<data>[0-4])", re.DOTALL)),
        CATEGORY('NFPA Reactivity', re.compile(r"NFPA.*?(([R|r]eactivity)|([I|i]nstability)).*?(?P<data>[0-4])", re.DOTALL)),
        CATEGORY('SARA 311/312', re.compile(r"SARA 311.*?(?P<data>(Chronic|Acute|Fire|Reactive)+?(.{0,25}(Hazard|Reactive))+)", re.DOTALL)),
        CATEGORY('Revision Date', re.compile(r"[R|r]evision [D|d]ate.*?(?P<data>\d.*?\s)", re.DOTALL)),
        CATEGORY('Physical State', re.compile(r"F[\s]*?o[\s]*?r[\s]*?m[\s]*?\W(.)*?(?P<data>\w+)\s", re.DOTALL))
        )


def sds_parser(sds_file):

        sds_text = get_pdf_text(sds_file)

        chemical_data = get_chemical_data(sds_text)

        return chemical_data


def get_chemical_data(text):

    chemical_data = {}

    for category in ChemicalData.CATEGORIES:

        match_found = category.regex.search(text)

        if match_found:

            if match_found.group('data'):
                match = match_found.group('data').replace('\n', '')
            else:
                match = 'Not Listed'
            chemical_data[category.name] = match
            print(category.name + ': ' + match)

        else:

            chemical_data[category.name] = 'Not Found'
            print(category.name + ': ' + 'Not Found')

    return chemical_data


def get_pdf_text(file_path):

    text = ''

    with open(file_path, "rb") as _:
        pdf = PdfFileReader(_, 'rb')

        for page_num in range(pdf.getNumPages()):
            # TODO: unknown error from certain files
            try:
                text += pdf.getPage(page_num).extractText()
            except:
                pass

    return text


if __name__ == '__main__':
    sds_to_csv()
