import requests
from bs4 import BeautifulSoup

from app import endpoints
from app.models.activity import Activity
from app.models.grade import Grade
from app.models.perfil import Perfil


def authenticate(data):
    fields = [
        "login",
        "password"
    ]

    user = {field: data[field] for field in fields}

    headers, token = _get_cookies(requests.get(endpoints.acadonline.home))

    requests.post(endpoints.acadonline.auth, user, headers=headers)

    return token


def get_perfil(token):
    perfil_page = requests.get(
        endpoints.acadonline.perfil_get,
        headers=_get_headers(token)
    )

    perfil = _parse_perfil(perfil_page)

    return perfil


def set_perfil(token, data):
    fields = [
        "bairro",
        "cep",
        "cidade",
        "complemento",
        "ddd",
        "email",
        "id",
        "logradouro",
        "numeroTelefone",
        "numero_residencia",
        "uf",
        "url_lattes",
    ]

    perfil = {field: data[field] for field in fields}
    perfil["id"] = "72403"
    perfil["_action_update"] = "Alterar"

    update_perfil = requests.post(
        endpoints.acadonline.perfil_set,
        perfil,
        headers=_get_headers(token)
    )

    return update_perfil


def set_password(token, data):
    fields = [
        "senha1",
        "senha2"
    ]

    password = {field: data[field] for field in fields}
    password["id"] = "72403"
    password["_action_update"] = "Alterar"
    password["_method"] = "PUT"

    update_password = requests.post(
        endpoints.acadonline.password,
        password,
        headers=_get_headers(token)
    )

    return update_password


def remember_password(token):
    params = {"_action_passo2": "OK", "registroAcademico": "14147326"}

    request_remember_page = requests.post(
        endpoints.acadonline.remember_password,
        params,
        headers=_get_headers(token)
    )

    return request_remember_page


def get_grades(token):
    grades_page = requests.get(
        endpoints.acadonline.grades,
        headers=_get_headers(token)
    )

    grades = _parse_grades(grades_page)["disciplines"]

    return grades


def get_additional_activities(token):
    activities_page = requests.get(
        endpoints.acadonline.activities,
        headers=_get_headers(token)
    )

    activities = _parse_additional_activities(activities_page)

    return activities


def _parse_additional_activities(activities_page):
    activities_raw = [
        [cell.text for cell in row("td")]
        for row in BeautifulSoup(activities_page.content, features="lxml")("tr", "even")
    ]
    activities = [
        Activity(*[field for field in activity_raw]).__dict__
        for activity_raw in activities_raw
    ]
    return activities


def _parse_grades(grades_page):
    try:
        grades_raw = [
                         [cell.text for cell in row("td")]
                         for row in BeautifulSoup(grades_page.content, features="lxml")("tr")
                     ][1:]

        grades = Grade(grades_raw).__dict__
    except:
        grades = None

    return grades


def _parse_perfil(perfil_page):
    try:
        perfil_raw = [
            value.find("td", "value")
                .text.replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
                .replace("/\s\s+/", "")
                .strip()
            for value in BeautifulSoup(perfil_page.content, features="lxml")("tr", "prop")
        ]

        perfil = Perfil(*[field for field in perfil_raw]).__dict__
    except:
        perfil = None

    return perfil


def _get_cookies(response):
    headers_raw = dict((key, value) for key, value in response.cookies.items())
    headers = {"cookie": f'JSESSIONID={headers_raw["JSESSIONID"]};'}
    return headers, headers_raw["JSESSIONID"]


def _get_headers(jsession):
    return {"cookie": f"JSESSIONID={jsession};"}
