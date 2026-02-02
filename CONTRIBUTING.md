# Contributing to VectorForge Open Vectors

Thank you for your interest in contributing to VectorForge Open Vectors.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs, request features, or ask questions
- For bugs, include: spec version, what you expected, what happened, and reproduction steps
- For schema issues, include the failing JSON and the validation error

### Proposing Changes

1. **Open an issue first** to discuss significant changes before implementing
2. Fork the repository
3. Create a feature branch from `main`
4. Make your changes
5. Ensure all test vectors pass
6. Submit a pull request

### What We Accept

- Bug fixes to schemas, reference implementations, or documentation
- New test vectors that improve conformance coverage
- Documentation improvements and clarifications
- Benchmark dataset contributions (must be synthetic or properly licensed)

### What Requires Discussion

- New fields in core schemas (envelope, DIVT, profile)
- New Vector types or record subtypes
- Changes to canonicalization rules
- Changes to fidelity metrics or CBS definitions

### What We Don't Accept

- Proprietary algorithms or compression methods
- Changes that break backward compatibility without a major version bump
- Vendor-specific extensions in core schemas (use `extensions` fields)

## Code Standards

### JSON Schemas

- Use JSON Schema Draft 2020-12
- Include `$id` with versioned URL
- Use `additionalProperties: false` for strict validation
- Document all fields with `description`

### Reference Implementations

- Python: Follow PEP 8, include type hints
- Go: Follow standard Go formatting (`gofmt`)
- Both: Include tests that validate against test vectors

### Documentation

- Use clear, concise language
- Include examples where helpful
- Keep the audience in mind: engineers implementing the spec

## Review Process

1. All PRs require at least one maintainer review
2. Schema changes require conformance test updates
3. Breaking changes require CHANGELOG entry and version bump discussion

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
