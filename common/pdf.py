"""
Running pypeteer surprisingly requires a lot of magic,
so it is all placed here
"""
import asyncio
import tempfile
from multiprocessing import Process, Queue

import pyppeteer
from django.conf import settings
from django.utils.module_loading import import_string


PYPPETEER_OPTIONS = {
    'headless': True,

    # without these options it works very long time
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-gpu',
    ],
}


async def _async_generate_pdf(html_file):
    """
    pyppeteer is async, so we write it in async style
    and wrap it later with sync real_generate_pdf()
    """
    browser = await pyppeteer.launch(options=PYPPETEER_OPTIONS)
    page = await browser.newPage()
    await page.goto(f'file://{html_file.name}')
    pdf = await page.pdf(
        format='A4',
        printBackground=True,
        margin={'top': '5mm', 'bottom': '5mm'},
    )
    await browser.close()
    return pdf


def _get_or_create_eventloop():
    """
    Taken from https://bit.ly/3q8FXRv
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


def _html_to_pdf_through_queue(queue, html):
    """
    A sync wrapper for async _async_generate_pdf()
    It takes html string and returns PDF object in bytes.
    We also need to use temp file because of puppeteer limitations.
    Without it it won't display images in resulting PDF.
    """
    loop = _get_or_create_eventloop()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html') as html_file:
        html_file.write(html)
        html_file.flush()
        coroutine = _async_generate_pdf(html_file)
        pdf = loop.run_until_complete(coroutine)

    queue.put(pdf)


def real_generate_pdf(html):
    """
    Convert provided html into PDF using pyppeteer package.
    Without extracting to a separate process it raises weird asyncio exceptions,
    like 'ValueError: signal only works in main thread'.
    """
    queue = Queue()
    process = Process(target=_html_to_pdf_through_queue, args=(queue, html))
    process.start()
    pdf = queue.get()
    process.join()
    return pdf


def mock_generate_pdf(html):
    """
    Mock to use for testing
    """
    return b'%PDF-1.4'


def generate_pdf(html):
    """
    Import PDF backend from settings and use it
    to turn provided html into pdf, returned in bytes
    """
    try:
        pdf_backend = import_string(settings.PDF_BACKEND)
    except (AttributeError, ImportError):
        # in case of error try to load real backend
        pdf_backend = import_string('common.pdf.real_generate_pdf')

    pdf = pdf_backend(html)
    return pdf
