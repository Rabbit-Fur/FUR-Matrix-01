# Fine-Tuning Pipeline

The `Fine-Tuning Pipeline` GitHub Action automates training of the conversation model.
It reads chat logs and user feedback from MongoDB, transforms them into a dataset
and invokes `scripts/fine_tune.py` to train a new model. After training,
the updated weights are committed back to the repository and the MongoDB
vector index is refreshed.

## Usage

1. Define `MONGODB_URI` and `OPENAI_API_KEY` as repository secrets. These are
   passed to the workflow and used by the training script.
2. Trigger the workflow manually from the GitHub Actions tab or wait for the
   weekly schedule (Monday 03:00 UTC).
3. The script should write the model artifact to `models/` and update the
   corresponding vector index.

To run the process locally you can execute:

```bash
python scripts/fine_tune.py
```

`fine_tune.py` is responsible for extracting `chat_history` and `feedback`
collections, building a training dataset (e.g. JSONL) and running a fine-tune
with the Transformers library or the OpenAI API.
