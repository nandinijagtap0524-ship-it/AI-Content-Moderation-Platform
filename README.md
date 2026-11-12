# AI Content Moderation Platform

A small, local web app that classifies text with a Multinomial Naive Bayes model. It demonstrates automated content triage across safe, harassment, hate, violence, sexual-content, and self-harm categories.

## Run locally

Requires Python 3.9 or newer. The project uses only the Python standard library.

```powershell
cd ai-content-moderation
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Use the classifier

Enter text in the web interface, or send a JSON request:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/moderate `
  -Method Post -ContentType "application/json" `
  -Body '{"text":"Thanks for helping me today"}'
```

The API returns the predicted category, moderation action, confidence estimate, and the most influential words from the input.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Limitations

This is an educational prototype, not a production moderation system. Its compact, hand-written training set is not representative of real users or language, and its confidence estimates are not calibrated. Expect false positives and false negatives, especially for slang, reclaimed language, context-dependent speech, and languages other than English. Do not use it as the sole basis for consequential decisions; production systems need representative data, human review, privacy protections, monitoring, and regular evaluation.
