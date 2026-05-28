# Lab 9A — KG Construction

Follow the learner-facing lab guide on the AISPIRE course site.

**Deliverables:**

1. Extend `recipes_partial.ttl` from 5 recipes to 15. At least one recipe must use a cuisine whose label match only succeeds via `skos:altLabel`.
2. Complete the `TODO` in `load_dataset.py` so it POSTs the TTL to `http://localhost:3030/recipes/data` with `Content-Type: text/turtle`.
3. Implement `q1()`, `q2()`, `q3()` in `queries.py` per the docstrings.
4. Open a PR with an ontology summary and a note on the SKOS additions.

Local run:

```bash
pip install -r requirements.txt
docker compose up -d
python load_dataset.py
pytest tests/ -v
```

---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.
