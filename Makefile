.PHONY: sync validate secrets markdown eval

sync:
	python3 scripts/sync.py

validate:
	python3 scripts/sync.py --check
	python3 scripts/validate.py
	python3 scripts/check_secrets.py
	git diff --check

secrets:
	python3 scripts/check_secrets.py

markdown:
	npx --yes markdownlint-cli2

eval:
	python3 scripts/eval.py pending
