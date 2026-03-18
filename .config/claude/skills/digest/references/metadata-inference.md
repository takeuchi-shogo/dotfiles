# Metadata Inference Rules

## Source Type Detection

| Pattern | source_type |
|---------|-------------|
| youtube.com, youtu.be | YouTube |
| arxiv.org | Paper |
| github.com | Repository |
| *.pdf URL | PDF |
| podcast/episode in text | Podcast |
| Default | Article |

## Auto-Inference Fields

| Field | Method |
|-------|--------|
| title | First H1 or bold text |
| author | Byline, channel name, or "Unknown" |
| url | Extracted URL or empty |
| language | Text language detection (ja/en) |
| tags | Extract from content keywords (max 5) |
| date | Publication date or today |
