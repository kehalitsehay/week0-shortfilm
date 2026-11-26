PY ?= python3
SHOT ?= s01

setup:      ## install dependencies (also needs ffmpeg on PATH)
	$(PY) -m pip install -r requirements.txt
validate:   ## schema-check storyboard.json
	$(PY) -m pipeline validate
smoke:      ## call each provider once, log latency
	$(PY) -m pipeline smoke
radio:      ## narration-only cut for user test 1
	$(PY) -m pipeline radio
film:       ## the whole pipeline, cached (the one documented command)
	$(PY) -m pipeline validate && $(PY) -m pipeline run
shot:       ## regenerate one shot: make shot SHOT=s03
	$(PY) -m pipeline run --only $(SHOT)
offline:    ## full pipeline with placeholder assets, no keys needed
	$(PY) -m pipeline --offline run
costs:      ## per-stage measurements from runs.jsonl
	$(PY) -m pipeline costs
showcase:   ## build the static showcase page
	$(PY) -m pipeline showcase
test:
	$(PY) -m pytest -q
