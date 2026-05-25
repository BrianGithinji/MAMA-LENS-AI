# MOTHER Dataset — Download Instructions

**Dataset:** MOTHER: A Maternal Online Technology for Health Care Dataset  
**Source:** Harvard Dataverse  
**DOI:** https://doi.org/10.7910/DVN/EZLCH3  
**Paper:** https://link.springer.com/article/10.1186/s13104-025-07230-2  
**License:** Open access (CC0 / public domain)

## What it contains
- 503 validated Q&A pairs on maternal health
- Covers 1st, 2nd and 3rd trimesters
- Collected from rural/semi-urban Uganda
- Answers validated by professional medical personnel
- Designed for conversational chatbot development

## How to download

1. Go to: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EZLCH3
2. Click **Access Dataset** → **Download ZIP** (or download the CSV directly)
3. Place the CSV file in this directory:
   ```
   ai/mama_model/mother_dataset/MOTHER_dataset.csv
   ```

## Expected CSV columns
The finetune.py script auto-detects these column name variants:
- Question column: `question`, `Question`, `QUESTION`, `q`, `Q`, `input`
- Answer column: `answer`, `Answer`, `ANSWER`, `a`, `A`, `output`, `response`

## After downloading, train the model

```bash
cd "MAMA-LENS AI/SYSTEM"
.venv311\Scripts\python.exe ai/mama_model/finetune.py --epochs 5
```

This will combine the 503 MOTHER examples with the local multilingual
training_data.json (English + Swahili pairs) for a total of ~543 examples.
