""" Views for generated forms """

import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.contrib import messages

import requests
from django.urls import reverse

from ..decorators import bceid_required
from ..utils.derived import get_derived_data
from ..utils.user_response import get_responses_from_db

EXHIBITS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[::-1])

EFILING_HUB_API_URL = 'http://localhost:8080'

TEST_ACCOUNTS = {
    'vivian': '77da92db-0791-491e-8c58-1a969e67d2fa',
    'lynda': '77da92db-0791-491e-8c58-1a969e67d2fb',
    'bob': '88da92db-0791-491e-8c58-1a969e67d2fb'
}

def get_account_guid(request):
    name = request.user.display_name.lower()
    if name not in TEST_ACCOUNTS.keys():
        name = 'vivian'
    return TEST_ACCOUNTS[name]

@bceid_required
def submit(request, form_number):
    """ Test Only - Generate form and submit to eFiling Hub. Redirect to Hub afterwards."""
    form_number, responses = prepare_pdf_form(form_number, request)
    form_name = 'form{}'.format(form_number)

    pdf = __render_pdf(request, form_name, {
        'css_root': settings.WEASYPRINT_CSS_LOOPBACK,
        'responses': responses,
        'derived': get_derived_data(responses),
        'exhibits': EXHIBITS[:],
    })

    # generate package data
    package_data = {
        "clientApplication": {
            "displayName": "Online Divorce Assistant",
            "type": "string"
        },
        "filingPackage": {
            "documents": [
                {
                    "name": '{}.pdf'.format(form_name),
                    "type": "AFF"
                }
            ],
            "court": {
                "location": "string",
                "level": "string",
                "courtClass": "string",
                "division": "string",
                "fileNumber": "string",
                "participatingClass": "string"
            }
        },
        "navigation": {
            "success": {
                "url": request.build_absolute_uri(reverse('dashboard_nav', args=['check_with_registry']))
            },
            "error": {
                "url": request.build_absolute_uri(reverse('dashboard_nav', args=['print_form']))
            },
            "cancel": {
                "url": request.build_absolute_uri(reverse('dashboard_nav', args=['print_form']))
            }
        }
    }

    headers = {'X-Auth-UserId': get_account_guid(request)}

    response = requests.post('{}/submission/documents'.format(EFILING_HUB_API_URL), headers=headers,
                             files={'files': ('{}.pdf'.format(form_name), pdf.content)})
    response = json.loads(response.text)

    if "submissionId" in response and response['submissionId'] != "":
        # get the redirect url
        headers['Content-Type'] = 'application/json'
        response = requests.post('{}/submission/{}/generateUrl'.format(EFILING_HUB_API_URL, response['submissionId']),
                                 headers=headers, data=json.dumps(package_data))

        if response.status_code == 200:
            response = json.loads(response.text)
            return redirect(response['efilingUrl'])
        response = json.loads(response.text)

    # error ocurred .. add it to session
    messages.add_message(request, messages.ERROR, '{} - {}'.format(response['error'], response['message']))

    return redirect(reverse('dashboard_nav', args=['print_form']))


@bceid_required
def form(request, form_number):
    """ View for rendering PDF's and previews """

    form_number, responses = prepare_pdf_form(form_number, request)

    return __render_form(request, 'form%s' % form_number, {
        'css_root': settings.WEASYPRINT_CSS_LOOPBACK,
        'responses': responses,
        'derived': get_derived_data(responses),
        'exhibits': EXHIBITS[:],
    })


def prepare_pdf_form(form_number, request):
    responses = get_responses_from_db(request.user)
    if (form_number == '1' or form_number.startswith('37') or
            form_number.startswith('38') or
            form_number.startswith('35')):
        # Add an array of children that includes blanks for possible children
        under = int(responses.get('number_children_under_19') or 0)
        over = int(responses.get('number_children_under_19') or 0)
        actual = json.loads(responses.get('claimant_children', '[]'))
        total = len(actual)
        responses['num_actual_children'] = len(actual)
        responses['children'] = [actual[i] if i < total else {}
                                 for i in range(0, max(under + over, total))]
    if form_number == "37":
        responses["which_claimant"] = 'both'
    elif form_number == "37_claimant1":
        form_number = "37"
        responses = __add_claimant_info(responses, '_you')
        responses['which_claimant'] = 'Claimant 1'
    elif form_number == '37_claimant2':
        form_number = '37'
        responses = __add_claimant_info(responses, '_spouse')
        responses['which_claimant'] = 'Claimant 2'
    if form_number == "38":
        responses["which_claimant"] = 'both'
    elif form_number == '38_claimant1':
        form_number = '38'
        responses = __add_claimant_info(responses, '_you')
        responses['which_claimant'] = 'Claimant 1'
    elif form_number == '38_claimant2':
        form_number = '38'
        responses = __add_claimant_info(responses, '_spouse')
        responses['which_claimant'] = 'Claimant 2'
    return form_number, responses


def __render_pdf(request, form_name, context):
    output_as_html = request.GET.get('html', None) is not None

    if output_as_html:
        context['css_root'] = settings.FORCE_SCRIPT_NAME[:-1]

    # render to form as HTML
    rendered_html = render_to_string('pdf/' + form_name + '.html',
                                     context=context, request=request)

    # if '?html' is in the querystring, then return the plain html
    if output_as_html:
        return HttpResponse(rendered_html)

    # post the html to the weasyprint microservice
    url = settings.WEASYPRINT_URL + '/pdf?filename=' + form_name + '.pdf'
    pdf = requests.post(url, data=rendered_html.encode('utf-8'))

    return pdf


def __render_form(request, form_name, context):

    pdf = __render_pdf(request, form_name, context)

    # return the response as a pdf
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=' + form_name + '.pdf'

    return response


def __add_claimant_info(responses, claimant):
    claimant_info = {}
    for key in responses:
        if key.endswith(claimant):
            claimant_key = key.replace(claimant, '_claimant')
            claimant_info[claimant_key] = responses[key]
    responses.update(claimant_info)
    return responses
