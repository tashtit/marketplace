.PHONY: sync validate install lint-markdown scan-secrets test

install:
	npm ci

sync:
	python3 scripts/sync.py

lint-markdown:
	@test -x node_modules/.bin/markdownlint-cli2 \
		|| { echo "markdownlint-cli2 is not installed; run 'make install' first."; exit 1; }
	node_modules/.bin/markdownlint-cli2

scan-secrets:
	python3 scripts/scan_secrets.py

test:
	python3 -m unittest discover -s tests/scripts -b

validate:
	python3 scripts/sync.py --check
	python3 scripts/validate.py
	$(MAKE) scan-secrets
	$(MAKE) lint-markdown
	git diff --check
