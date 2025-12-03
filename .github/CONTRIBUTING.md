# Contributing

We welcome contributions to dfimage! This document provides guidelines
and instructions for contributing to the project.

## Prerequisites

Before you begin, ensure you have the following:

- Git installed on your system
- A GitHub account
- Basic knowledge of Python development

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please review and adhere
to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### 1. Fork the Repository

First, create a fork of the [dfimage](https://github.com/LanikSJ/dfimage/)
repository. Methods to fork a repository can be found in the
[GitHub Documentation](https://docs.github.com/en/get-started/quickstart/fork-a-repo).

### 2. Clone Your Fork

Add your fork as a local project:

```bash
# Choose one of the following methods:

# Using HTTPS
git clone https://github.com/YOUR-USERNAME/dfimage.git

# Using SSH (recommended for contributors who have SSH keys set up)
git clone git@github.com:YOUR-USERNAME/dfimage.git
```

> [Which remote URL should be used?](https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories)

### 3. Navigate to the Project Directory

```bash
cd dfimage
```

### 4. Set Up Git Remotes

Add the original repository as an upstream remote to keep your fork synchronized:

```bash
# Add your fork as origin
git remote add origin https://github.com/YOUR-USERNAME/dfimage.git

# Add the original repository as upstream
git remote add upstream https://github.com/LanikSJ/dfimage.git
```

Verify your remotes are set up correctly:

```bash
git remote -v
```

## Keeping Your Fork Updated

To stay up to date with the main repository:

```bash
# Fetch and merge changes from upstream
git fetch upstream
git merge upstream/main
```

Or more concisely:

```bash
git pull upstream main
```

## Development Workflow

### 1. Choose a Base Branch

Before starting development, ensure you're working from the correct base branch:

| Type of Change     | Base Branch |
|--------------------|-------------|
| Documentation      | `main`      |
| Bug fixes          | `main`      |
| New features       | `main`      |
| Breaking changes   | `main`      |

### 2. Create a Feature Branch

Always create a new branch for your changes:

```bash
# Switch to main and pull latest changes
git checkout main
git pull upstream main

# Create and switch to a new feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes:
git checkout -b fix/issue-number-description
```

Use descriptive branch names following the pattern:

- `feature/description-of-feature`
- `fix/issue-number-description`
- `docs/update-documentation`

### 3. Make Your Changes

- Write clear, concise commit messages
- Follow the existing code style and conventions
- Add tests for new functionality
- Ensure all tests pass before submitting

### 4. Testing

Run the test suite before submitting your changes:

```bash
# Install dependencies if needed
pip install -e .

# Run tests
python -m pytest
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add your feature description"
```

Follow conventional commit format for clear commit messages.

### 6. Push and Create a Pull Request

```bash
# Push your branch to your fork
git push -u origin feature/your-feature-name
```

Then, open a pull request on [the dfimage repository](https://github.com/LanikSJ/dfimage/) using the provided template. Include:

- A clear description of the changes
- Screenshots/videos if applicable
- Tests demonstrating the fix/feature
- Any relevant issue numbers

## Pull Request Guidelines

- Ensure your PR title is descriptive and follows conventional commit format
- Provide a detailed description of what changes were made and why
- Reference any related issues or discussions
- Keep PRs focused on a single change or feature
- Be open to feedback and iterate on your changes

## Need Help?

If you have questions about contributing, please:

1. Check existing [GitHub Issues](https://github.com/LanikSJ/dfimage/issues) and [Discussions](https://github.com/LanikSJ/dfimage/discussions)
2. Review the project's [README](README.md) and [documentation](https://github.com/LanikSJ/dfimage/wiki)
3. Open a new discussion if needed

Thank you for contributing to dfimage! 🎉
