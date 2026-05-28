"""Autograder for Lab 9A — KG Construction.

The repo root after Classroom acceptance contains recipes_partial.ttl,
queries.py, load_dataset.py at the top level. These tests sys.path the
repo root and import directly from there.
"""

import json
import os
import sys
import time
from collections import Counter

import pytest
import requests
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import SKOS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from queries import q1, q2, q3  # noqa: E402

NS = Namespace("http://aispire.example.org/recipes/")
TTL_FILE = os.path.join(os.path.dirname(__file__), "..", "recipes_partial.ttl")
FUSEKI_SPARQL = "http://localhost:3030/recipes/sparql"
FUSEKI_PING = "http://localhost:3030/$/ping"


@pytest.fixture(scope="module")
def g():
    graph = Graph()
    graph.parse(TTL_FILE, format="turtle")
    return graph


@pytest.fixture(scope="module")
def fuseki_ready():
    """Wait briefly for the Fuseki service to come up. Skip Fuseki-dependent
    tests when the endpoint is not reachable (local-only smoke runs).
    """
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            r = requests.get(FUSEKI_PING, timeout=2)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def _ask_fuseki():
    r = requests.get(
        FUSEKI_SPARQL,
        params={"query": "ASK { ?s ?p ?o }"},
        headers={"Accept": "application/sparql-results+json"},
        timeout=5,
    )
    r.raise_for_status()
    return r.json().get("boolean", False)


def _select_fuseki(query):
    r = requests.get(
        FUSEKI_SPARQL,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["results"]["bindings"]


# ------------------------------ Structural tests ------------------------------

def test_ttl_parses(g):
    assert len(g) >= 60, (
        f"Expected at least 60 triples (~15 recipes x ~4 properties + class triples); "
        f"got {len(g)}. Did you extend recipes_partial.ttl to 15 recipes?"
    )


def test_all_recipes_have_required_properties(g):
    recipes = list(g.subjects(predicate=NS.cuisine))
    assert len(recipes) >= 15, (
        f"Need at least 15 recipes; found {len(recipes)}."
    )
    required = [NS.name, NS.cuisine, NS.primaryIngredient, NS.author, NS.year]
    missing = []
    for r in recipes:
        for p in required:
            if (r, p, None) not in g:
                missing.append((str(r), str(p)))
    assert not missing, f"Recipes missing required properties: {missing[:5]}"


def test_cuisine_classes_have_skos_labels(g):
    cuisines = set(g.objects(predicate=NS.cuisine))
    assert len(cuisines) >= 3, (
        f"Expected at least 3 distinct cuisines (the starter ships 2; the "
        f"third is a TODO that's required to push 15 recipes through 3+ "
        f"cuisines); found {len(cuisines)}."
    )
    missing_pref = [c for c in cuisines if (c, SKOS.prefLabel, None) not in g]
    missing_alt = [c for c in cuisines if (c, SKOS.altLabel, None) not in g]
    assert not missing_pref, f"Cuisines missing skos:prefLabel: {missing_pref}"
    assert not missing_alt, (
        f"Cuisines missing skos:altLabel: {missing_alt}. Q2 needs at least one "
        f"altLabel to exercise the SKOS disambiguation path."
    )


# ------------------------------ Fuseki tests ----------------------------------

def test_fuseki_dataset_loaded(fuseki_ready):
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable on localhost:3030 (services block not running).")
    assert _ask_fuseki() is True, (
        "ASK against http://localhost:3030/recipes/sparql returned false. "
        "Did load_dataset.py POST the TTL to /recipes/data?"
    )


# ------------------------------ Query tests -----------------------------------

def test_q1_returns_all_recipes(g):
    sparql = q1()
    assert sparql.strip(), "q1() returned an empty string."
    rows = list(g.query(sparql))
    assert len(rows) >= 15, f"q1 expected >= 15 rows; got {len(rows)}."
    # Each row binds (?recipe, ?name).
    assert all(len(r) == 2 for r in rows), "q1 must SELECT ?recipe ?name."


def test_q2_handles_italian_skos_variants(g):
    sparql = q2()
    assert sparql.strip(), "q2() returned an empty string."
    rows = list(g.query(sparql))
    assert rows, "q2 returned zero rows; expected Italian recipes."
    # All returned recipes must have :cuisine :Italian (the only cuisine whose
    # SKOS labels include "Italian"/"italiano").
    bad = [r for r in rows if (URIRef(str(r[0])), NS.cuisine, NS.Italian) not in g]
    assert not bad, (
        f"q2 returned recipes whose cuisine is not :Italian: {bad[:3]}. "
        f"Check your prefLabel/altLabel filter."
    )
    # Cross-check: distinct ?recipe subjects must equal ground truth.
    # A learner who writes the prefLabel-OR-altLabel pattern without DISTINCT
    # produces 2x rows (one per matching label) for every Italian recipe; the
    # set of returned ?recipe URIs must still equal the ground-truth set.
    expected = set(g.subjects(predicate=NS.cuisine, object=NS.Italian))
    returned = {URIRef(str(r[0])) for r in rows}
    assert returned == expected, (
        f"q2 returned recipe set {sorted(returned)}; expected {sorted(expected)}. "
        f"The most common cause is filtering only on skos:prefLabel and missing "
        f"the altLabel side."
    )


def test_q3_filters_post_2020_with_ingredient(g):
    sparql = q3()
    assert sparql.strip(), "q3() returned an empty string."
    rows = list(g.query(sparql))
    assert all(len(r) == 2 for r in rows), "q3 must SELECT ?recipe ?ingredient."
    # Ground truth: recipes whose :year > 2020.
    expected = set()
    for r, _, y in g.triples((None, NS.year, None)):
        try:
            if int(y) > 2020:
                expected.add(r)
        except (TypeError, ValueError):
            continue
    returned = {URIRef(str(r[0])) for r in rows}
    assert returned == expected, (
        f"q3 returned {sorted(returned)}; expected {sorted(expected)}. "
        f"Check FILTER (?year > 2020) — note strict > not >=."
    )


# ------------------------------ Round-trip ------------------------------------

def test_queries_agree_with_fuseki(g, fuseki_ready):
    """The three queries should return the same row counts when run against
    Fuseki as they do against the local rdflib graph."""
    if not fuseki_ready:
        pytest.skip("Fuseki not reachable on localhost:3030.")
    for label, fn in [("q1", q1), ("q2", q2), ("q3", q3)]:
        sparql = fn()
        local_count = len(list(g.query(sparql)))
        fuseki_count = len(_select_fuseki(sparql))
        assert local_count == fuseki_count, (
            f"{label}: rdflib returned {local_count} rows; Fuseki returned "
            f"{fuseki_count}. Did you POST the TTL with load_dataset.py?"
        )
