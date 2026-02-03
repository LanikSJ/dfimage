# Security Policy

## Supported Versions

| OS     | Version | Supported          |
| ------ | ------- | ------------------ |
| Alpine | 3.x.x   | :white_check_mark: |
| Alpine | 2.x.x   | :x:                |

## Reporting a Vulnerability

We take security seriously and appreciate your efforts to responsibly disclose your findings.

### How to Report

**Do NOT open a public issue** for security vulnerabilities. Instead, please report security issues through
one of these channels:

1. **GitHub Security Advisories** (Preferred):
   [Report via GitHub](https://github.com/LanikSJ/dfimage/security/advisories/new)
2. **Email**: Send details to [security@lanik.us](mailto:security@lanik.us)
3. **Security Discussions**: Open a discussion in our
   [GitHub Discussions](https://github.com/LanikSJ/dfimage/discussions/categories/security)
4. **Security Issues**: Create a
   [Security Advisory](https://github.com/LanikSJ/dfimage/security/advisories/new) on GitHub

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear explanation of the security issue
- **Steps to Reproduce**: Detailed steps to reproduce the vulnerability
- **Impact Assessment**: Potential impact and affected components
- **Proof of Concept**: If applicable, a minimal reproduction case
- **Suggested Fix**: If you have ideas for a fix (optional)

### Response Timeline

We are committed to responding to security reports in a timely manner:

- **Initial Response**: Within 48 hours of receiving the report
- **Status Update**: Within 5 business days with assessment
- **Resolution**: We will work diligently to fix critical vulnerabilities as quickly as possible

### Responsible Disclosure

We ask that you:

- Give us reasonable time to investigate and fix the issue before public disclosure
- Do not access, modify, or delete user data
- Do not perform attacks that could harm the availability of our services
- Do not publicly disclose the vulnerability until we have had a chance to address it

## Security Considerations

### Project-Specific Security

This project extracts Docker images to tar files. Security considerations include:

- **File System Access**: Limited to specified directories and files
- **Docker API Security**: Uses Docker API with appropriate permissions
- **Input Validation**: All inputs are validated to prevent path traversal

## Security Best Practices

### For Users

- **Run as Non-root**: Use non-root user when possible
- **Validate Images**: Only extract trusted Docker images
- **Monitor Output**: Monitor extracted files for suspicious content

### For Developers

When contributing to the project:

- **Validate Paths**: Ensure all file paths are properly validated
- **Test Security**: Include security testing in development
- **Review Changes**: Have security reviews for new features

## Security Resources

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [GitHub Security Documentation](https://docs.github.com/en/code-security/getting-started)

## Contact

For general security questions or concerns, you can:

- Open a discussion in our [GitHub Discussions](https://github.com/LanikSJ/dfimage/discussions)
- Contact the maintainers through the security email above for sensitive matters

Thank you for helping keep dfimage secure!
