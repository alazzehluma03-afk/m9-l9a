"""Three SPARQL queries against the recipes ontology.

Each function returns a SPARQL query string. The autograder parses your TTL
file with rdflib and runs each query both in-memory and against the live
Fuseki endpoint at http://localhost:3030/recipes/sparql.
"""


def q1():
    """Q1 — List all recipes and their names.

    Variables in the SELECT: ?recipe ?name.
    Returns: 15 rows once the TTL has been extended to 15 recipes.
    """
    # write a SELECT that returns every :Recipe instance and its :name.
    
    return """
    PREFIX : <http://aispire.example.org/recipes/>
    
    SELECT ?recipe ?name
    WHERE {
        ?recipe a :Recipe ;
                :name ?name .
    }
    """


def q2():
    """Q2 — List all Italian recipes matching either skos:prefLabel "Italian"
    OR skos:altLabel "italiano".

    Variables in the SELECT: ?recipe ?name.
    The query must NOT silently miss recipes whose cuisine is only matched
    via skos:altLabel. Use the SKOS disambiguation pattern from reading §7.
    """
    #  write a SELECT that filters on Italian cuisine via prefLabel OR altLabel.
    return """
    PREFIX : <http://aispire.example.org/recipes/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?recipe ?name
    WHERE {
        ?recipe a :Recipe ;
                :name ?name ;
                :cuisine ?cuisine .
        ?cuisine skos:prefLabel | skos:altLabel ?label .
        FILTER (?label = "Italian" || ?label = "italiano")
    }
    """


def q3():
    """Q3 — List recipes published after 2020 with their primary ingredient.

    Variables in the SELECT: ?recipe ?ingredient.
    Return the ingredient resource (URI), not its label. Use FILTER (?year > 2020).
    """
    #  write a SELECT joining :year, :primaryIngredient, with a year FILTER.
    return """
    PREFIX : <http://aispire.example.org/recipes/>
    
    SELECT ?recipe ?ingredient
    WHERE {
        ?recipe a :Recipe ;
                :primaryIngredient ?ingredient ;
                :year ?year .
        FILTER (?year > 2020)
    }
    """
