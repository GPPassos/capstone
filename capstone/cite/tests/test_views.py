import re
import json
import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.text import slugify
from capapi.tests.helpers import check_response, is_cached
from capweb.helpers import reverse
from capweb import helpers

from scripts.helpers import parse_xml


@pytest.mark.django_db
def test_home(client, django_assert_num_queries, ingest_metadata):
    """ Test / """
    with django_assert_num_queries(select=2):
        response = client.get(reverse('cite_home', host='cite'))
    check_response(response, content_includes="Alabama Appellate Courts Reports")


@pytest.mark.django_db
def test_series(client, django_assert_num_queries, volume_factory):
    """ Test /series/ """

    # make sure we correctly handle multiple reporters with same slug
    volume_1, volume_2 = [volume_factory() for _ in range(2)]
    volume_2.reporter.short_name_slug = volume_1.reporter.short_name_slug
    volume_2.reporter.save()

    with django_assert_num_queries(select=2):
        response = client.get(reverse('series', args=[volume_1.reporter.short_name_slug], host='cite'))
    check_response(response)
    content = response.content.decode()
    for vol in (volume_1, volume_2):
        assert vol.volume_number in content
        assert vol.reporter.full_name in content

    # make sure we redirect if series is not slugified
    series_slug = volume_1.reporter.short_name_slug.replace('-', '. ').upper()
    response = client.get(reverse('series', args=[series_slug], host='cite'))
    check_response(response, status_code=302)
    with django_assert_num_queries(select=2):
        response = client.get(reverse('series', args=[series_slug], host='cite'), follow=True)
    check_response(response, status_code=200)


@pytest.mark.django_db
def test_volume(client, django_assert_num_queries, case_factory):
    """ Test /series/volume/ """

    # make sure we correctly handle multiple reporters with same slug
    case_1, case_2, case_3 = [case_factory() for _ in range(3)]
    for case in [case_2, case_3]:
        case.reporter.short_name_slug = case_1.reporter.short_name_slug
        case.reporter.save()
        case.volume.volume_number = case_1.volume.volume_number
        case.volume.save()

    # make sure we exclude dupes
    case_3.duplicative = True
    case_3.save()

    with django_assert_num_queries(select=3):
        response = client.get(
            reverse('volume', args=[case_1.reporter.short_name_slug, case_1.volume.volume_number], host='cite'))
    check_response(response)
    content = response.content.decode()
    for case in (case_1, case_2):
        assert case.volume.volume_number in content
        assert case.reporter.full_name in content
        assert case.citations.first().cite in content

    assert case_3.citations.first().cite not in content

    # make sure we redirect if reporter name / series is not slugified
    series_slug = case_1.reporter.short_name_slug.replace('-', '. ').upper()
    response = client.get(reverse('volume', args=[series_slug, case_1.volume.volume_number], host='cite'))
    check_response(response, status_code=302)
    with django_assert_num_queries(select=3):
        response = client.get(reverse('volume', args=[series_slug, case_1.volume.volume_number], host='cite'), follow=True)
    check_response(response, status_code=200)


@pytest.mark.django_db
def test_case_not_found(client, django_assert_num_queries):
    """ Test /series/volume/case/ not found """
    with django_assert_num_queries(select=2):
        response = client.get(reverse('citation', args=['fake', '123', '456'], host='cite'))
    check_response(response, content_includes='Citation "123 Fake 456" was not found')


@pytest.mark.django_db
def test_cases_multiple(client, django_assert_num_queries, three_cases):
    """ Test /series/volume/case/ with multiple matching cases """
    first_case = three_cases[0]
    cite = first_case.citations.first()
    for i, case in enumerate(three_cases[1:]):
        case.citations.all().delete()
        cite.pk = None
        cite.case = case
        cite.save()
        case.name_abbreviation += str(i)
        case.save()
    cite_parts = re.match(r'(\S+)\s+(.*?)\s+(\S+)$', cite.cite).groups()
    with django_assert_num_queries(select=4):
        response = client.get(
            reverse('citation', args=[slugify(cite_parts[1]), cite_parts[0], cite_parts[2]], host='cite'))
    check_response(response, content_includes='Multiple cases match')
    content = response.content.decode()
    for case in three_cases:
        assert case.name_abbreviation in content

    # load one of the results
    first_case.jurisdiction.whitelisted = True
    first_case.jurisdiction.save()
    response = client.get(
        reverse('citation', args=[slugify(cite_parts[1]), cite_parts[0], cite_parts[2], first_case.id], host='cite'))
    check_response(response)


@pytest.mark.django_db
def test_single_case(client, auth_client, django_assert_num_queries, case):
    """ Test /series/volume/case/ with one matching case """

    # setup
    url = case.get_frontend_url()
    parsed = parse_xml(case.case_xml.orig_xml)
    case_text = parsed('casebody|casebody').children()[10].text.replace('\xad', '')

    ### can load whitelisted case

    case.jurisdiction.whitelisted = True
    case.jurisdiction.save()
    with django_assert_num_queries(select=3):
        response = client.get(url)
    check_response(response, content_includes=case_text)

    ### can load blacklisted case while logged out, via redirect

    case.jurisdiction.whitelisted = False
    case.jurisdiction.save()

    # first we get redirect to JS page
    with django_assert_num_queries(select=3):
        response = client.get(url, follow=True)
    check_response(response, content_includes="Click here to continue")

    # POSTing will set our cookies and let the case load
    with django_assert_num_queries(select=3):
        response = client.post(reverse('set_cookie'), {'not_a_bot': 'yes', 'next': url}, follow=True)
    check_response(response, content_includes=case_text)
    session = client.session
    assert session['case_allowance_remaining'] == settings.API_CASE_DAILY_ALLOWANCE - 1

    # we can now load directly
    response = client.get(url)
    check_response(response, content_includes=case_text)
    session = client.session
    assert session['case_allowance_remaining'] == settings.API_CASE_DAILY_ALLOWANCE - 2

    # can no longer load if quota used up
    session['case_allowance_remaining'] = 0
    session.save()
    response = client.get(url)
    check_response(response)
    assert case_text not in response.content.decode()
    session = client.session
    assert session['case_allowance_remaining'] == 0

    # check daily quota resettest_unlimited_access
    session['case_allowance_last_updated'] -= 60 * 60 * 24 + 1
    session.save()
    response = client.get(url)
    check_response(response, content_includes=case_text)
    session = client.session
    assert session['case_allowance_remaining'] == settings.API_CASE_DAILY_ALLOWANCE - 1

    ### can load normally as logged-in user

    response = auth_client.get(url)
    check_response(response, content_includes=case_text)
    auth_client.auth_user.refresh_from_db()
    assert auth_client.auth_user.case_allowance_remaining == settings.API_CASE_DAILY_ALLOWANCE - 1


@pytest.mark.django_db
def test_case_series_name_redirect(client, django_assert_num_queries, case):
    """ Test /series/volume/case/ with series redirect when not slugified"""
    cite = case.citations.first()
    cite_parts = re.match(r'(\S+)\s+(.*?)\s+(\S+)$', cite.cite).groups()

    # series is not slugified, expect redirect
    response = client.get(
        reverse('citation', args=[cite_parts[1], cite_parts[0], cite_parts[2]], host='cite'))
    check_response(response, status_code=302)

    response = client.get(
        reverse('citation', args=[cite_parts[1], cite_parts[0], cite_parts[2]], host='cite'), follow=True)
    check_response(response)

    # series redirect works with case_id
    response = client.get(
        reverse('citation', args=[cite_parts[1], cite_parts[0], cite_parts[2], case.id], host='cite'))
    check_response(response, status_code=302)

    response = client.get(
        reverse('citation', args=[cite_parts[1], cite_parts[0], cite_parts[2]], host='cite'), follow=True)
    check_response(response)


def get_schema(response):
    soup = BeautifulSoup(response.content.decode(), 'html.parser')
    scripts = soup.find_all('script', {'type': 'application/ld+json'})
    assert len(scripts) == 1
    script = scripts[0]
    return json.loads(script.text)


@pytest.mark.django_db
def test_schema_in_case(client, case):
    # setup
    url = case.get_frontend_url()
    parsed = parse_xml(case.case_xml.orig_xml)
    case_text = parsed('casebody|casebody').children()[10].text.replace('\xad', '')

    ### whitelisted case

    case.jurisdiction.whitelisted = True
    case.jurisdiction.save()

    response = client.get(url)
    check_response(response, content_includes=case_text)

    schema = get_schema(response)
    assert schema["headline"] == case.name_abbreviation
    assert schema["author"]["name"] == case.court.name

    # if case is whitelisted, extra info about inaccessibility is not needed
    # https://developers.google.com/search/docs/data-types/paywalled-content
    assert "hasPart" not in schema

    ### blacklisted case

    case.jurisdiction.whitelisted = False
    case.jurisdiction.save()

    response = client.post(reverse('set_cookie'), {'not_a_bot': 'yes', 'next': url}, follow=True)
    check_response(response, content_includes=case_text)

    schema = get_schema(response)
    assert schema["headline"] == case.name_abbreviation
    assert schema["author"]["name"] == case.court.name

    # if case is blacklisted, we include more data
    assert "hasPart" in schema
    assert schema["hasPart"]["isAccessibleForFree"] == 'False'


@pytest.mark.django_db()
def test_schema_in_case_as_google_bot(client, case, monkeypatch):
    # setup
    url = case.get_frontend_url()
    parsed = parse_xml(case.case_xml.orig_xml)
    case_text = parsed('casebody|casebody').children()[10].text.replace('\xad', '')

    def mock_is_google_bot(request):
        return True

    monkeypatch.setattr(helpers, 'is_google_bot', mock_is_google_bot)

    # our bot has seen too many cases!
    session = client.session
    session['case_allowance_remaining'] = 0
    session.save()
    assert session['case_allowance_remaining'] == 0

    case.jurisdiction.whitelisted = False
    case.jurisdiction.save()

    response = client.get(url, follow=True)

    assert not is_cached(response)

    # show cases anyway
    check_response(response, content_includes=case_text)
    schema = get_schema(response)
    assert schema["headline"] == case.name_abbreviation
    assert schema["author"]["name"] == case.court.name
    assert "hasPart" in schema
    assert schema["hasPart"]["isAccessibleForFree"] == 'False'


@pytest.mark.django_db()
def test_no_index(auth_client, case):
    case.no_index = True
    case.save()

    response = auth_client.get(case.get_frontend_url())
    check_response(response, content_includes='content="noindex"')
