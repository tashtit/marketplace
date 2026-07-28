.PHONY: sync validate

sync:
	python3 scripts/sync.py

validate:
	python3 scripts/sync.py --check
	python3 scripts/validate.py
	git diff --check
