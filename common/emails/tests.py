from django.core import mail

from common.emails import send_mail
from common.tests.base import PortalBaseTest


class SendEmailTest(PortalBaseTest):

    def setUp(self):
        super().setUp()
        self.assertEqual(len(mail.outbox), 0)
        self.subject = 'Terry'
        self.body = '<b>Gilliam</b>'
        self.to = 'graham@chapman'

    def test_send_html_body(self):
        is_sent = send_mail(to=self.to, subject=self.subject, body=self.body)

        self.assertTrue(is_sent)
        self.assertEqual(len(mail.outbox), 1)

        outbox_message = mail.outbox[-1]
        self.assertEqual(outbox_message.subject, 'Terry')
        self.assertEqual(outbox_message.body, 'Gilliam')
        self.assertEqual(outbox_message.to, ['graham@chapman'])
        self.assertEqual(outbox_message.alternatives, [('<b>Gilliam</b>', 'text/html')])

    def test_send_html_with_images(self):
        body_with_img = 'text<img src="cid:logo.png">'
        is_sent = send_mail(
            to=self.to, subject=self.subject, body=body_with_img, images=['logo.png'],
        )

        self.assertTrue(is_sent)
        self.assertEqual(len(mail.outbox), 1)

        outbox_message = mail.outbox[-1]
        self.assertEqual(outbox_message.body, 'text')
        self.assertEqual(outbox_message.alternatives, [(body_with_img, 'text/html')])
        self.assertEqual(len(outbox_message.attachments), 1)

        attachment = outbox_message.attachments[0]
        self.assertEqual(attachment.values(), ['image/png', '1.0', 'base64', '<logo.png>'])

    def test_plain_body_without_css(self):
        body = (
            '<html><head><style>body {\nmargin: 0 !important;\n}</style></head></html>'
            '<body>Gilliam</body>'
        )
        send_mail(to=self.to, subject=self.subject, body=body)
        self.assertNotIn('body {', mail.outbox[-1].body)
