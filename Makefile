.PHONY: sync validate

sync:
	python3 scripts/sync_marketplaces.py

validate:
	python3 scripts/sync_marketplaces.py --check
	python3 scripts/validate.py
	git diff --check
