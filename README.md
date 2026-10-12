OpenAPI Validator

A Python-based validator that checks OpenAPI documents against configurable AUTH security rules.

Features

- Validates OpenAPI documents against AUTH-001 through AUTH-012.
- Loads validation rules from "rules.yaml".
- Detects duplicate YAML mapping keys.
- Provides clear validation error messages.
- Runs automated tests using pytest.
- Integrates with GitHub Actions for continuous integration.

Project Structure

openapi-validator/
├── .github/
│   └── workflows/
│       └── validate-openapi.yml
├── README.md
├── validator.py
├── rules.yaml
├── openapi.yaml
├── requirements.txt
└── test_validator.py

Requirements

- Python 3.12 or later
- Dependencies listed in "requirements.txt"

Installation

Clone the repository:

git clone https://github.com/ankajdeoria-pixel/openapi-validator.git
cd openapi-validator

Install dependencies:

python -m pip install -r requirements.txt

Run the Validator

Run the validator against the OpenAPI document:

python validator.py openapi.yaml

Run Tests

Run the automated test suite:

pytest -q

The tests should pass before you consider the project ready for release.

Validation Rules

The validation rules are configured in "rules.yaml".

The project is intended to validate AUTH-001 through AUTH-012. The checks actually performed depend on the rules and implementation present in the repository.

YAML Duplicate-Key Detection

The validator is designed to detect duplicate YAML mapping keys so duplicate entries do not pass silently.

Continuous Integration

GitHub Actions workflow:

.github/workflows/validate-openapi.yml

The workflow checks required files, installs dependencies, runs the validator, and executes automated tests on configured GitHub events.

Repository

GitHub: https://github.com/ankajdeoria-pixel/openapi-validator

Release

Current release: "v1.0.0"

License

No license has been specified yet. Unless a license is added to the repository, reuse and redistribution remain subject to applicable copyright law.
