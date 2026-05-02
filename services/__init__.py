# services/__init__.py
#
# Intentionally empty — do NOT eagerly import ML service modules here.
#
# Whisper, BART, and spaCy are large optional dependencies that are loaded
# lazily inside services/pipeline.py the first time the pipeline is called.
#
# Blueprint routes import directly from individual service modules:
#   from services.pipeline import run_clario_pipeline
