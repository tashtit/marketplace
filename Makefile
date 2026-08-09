.PHONY: sync validate install lint-markdown scan-secrets test

install:
	npm ci

sync:
	node scripts/sync.js

lint-markdown:
	@test -x node_modules/.bin/markdownlint-cli2 \
		|| { echo "markdownlint-cli2 is not installed; run 'make install' first."; exit 1; }
	node_modules/.bin/markdownlint-cli2

scan-secrets:
	node scripts/scan-secrets.js

test:
	node --test tests/scripts/

validate:
	node scripts/sync.js --check
	node scripts/validate.js
	$(MAKE) scan-secrets
	$(MAKE) lint-markdown
	git diff --check
