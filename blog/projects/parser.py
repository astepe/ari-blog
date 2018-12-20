import re
from PyPDF2 import PdfFileReader
from collections import namedtuple


class SDSParser:

    CATEGORY = namedtuple('category', 'name regex')

    CATEGORIES = (
        CATEGORY('Product Name', re.compile(r"[P|p]roduct (([N|n]ame)|([D|d]escription)).*?(?P<data>[^ :\n].*?)(P|C)", re.DOTALL)),
        CATEGORY('Flash Point (°F)', re.compile(r"([F|f]lash [P|p]oint)([\sC\d°:\(.]*?(?P<data>[0-9°.]*)\s*?°?\s?F)?", re.DOTALL)),
        CATEGORY('Specific Gravity', re.compile(r"([R|r]elative [D|d]ensity|[S|s]pecific [G|g]ravity)\s*(?P<data>[0-9.]*\s)?", re.DOTALL)),
        CATEGORY('CAS #', re.compile(r"CAS.*?(?P<data>\d{2,7}\n*?-\n*?\d{2}\n*?-\n*?\d)", re.DOTALL)),
        CATEGORY('NFPA Fire', re.compile(r"NFPA.*?[F|f]ire.*?(?P<data>[0-4])", re.DOTALL)),
        CATEGORY('NFPA Health', re.compile(r"NFPA.*?[H|h]ealth.*?(?P<data>[0-4])", re.DOTALL)),
        CATEGORY('NFPA Reactivity', re.compile(r"NFPA.*?(([R|r]eactivity)|([I|i]nstability)).*?(?P<data>[0-4])", re.DOTALL)),
        CATEGORY('SARA 311/312', re.compile(r"SARA 311.*?(?P<data>(Chronic|Acute|Fire|Reactive)+?(.{0,25}(Hazard|Reactive))+)", re.DOTALL)),
        CATEGORY('Revision Date', re.compile(r"[R|r]evision [D|d]ate.*?(?P<data>\d.*?\s)", re.DOTALL)),
        CATEGORY('Physical State', re.compile(r"F[\s]*?o[\s]*?r[\s]*?m[\s]*?\W(.)*?(?P<data>\w+)\s", re.DOTALL))
        )

    def __init__(self):
        self.category_checks = {category.name: True for category in self.CATEGORIES}

    def parse_sds(self, sds_file, category_checks=None):

            if category_checks:
                self.category_checks.update(category_checks)

            sds_text = self.get_pdf_text(sds_file)

            chemical_data = self.get_chemical_data(sds_text)

            return chemical_data

    def get_chemical_data(self, text):

        chemical_data = {}

        for category in self.CATEGORIES:

            if self.category_checks[category.name] is True:

                match_found = category.regex.search(text)

                if match_found:

                    if match_found.group('data'):
                        match = match_found.group('data').replace('\n', '')
                    else:
                        match = 'No data available'
                    chemical_data[category.name] = match
                    #print(category.name + ': ' + match)

                else:

                    chemical_data[category.name] = 'Data not listed'
                    #print(category.name + ': ' + 'Not Found')

        return chemical_data

    @staticmethod
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
