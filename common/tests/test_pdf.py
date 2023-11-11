from common.tests.base import PortalBaseTest
from common.pdf import generate_pdf


class PdfTest(PortalBaseTest):

    def test_generate_pdf(self):
        html = '<b>im b</b>'
        pdf = generate_pdf(html)
        self.assertTrue(pdf.startswith(b'%PDF-1.4'))
