# Contributing to Money Review

Thank you for your interest in contributing to Money Review! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with a clear title and description
3. **Include details**:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, database version)
   - Relevant logs or error messages

### Suggesting Enhancements

For feature requests or enhancements:

1. **Open an issue** describing the feature
2. **Explain the use case** and why it would be valuable
3. **Provide examples** of how it would work
4. **Consider alternatives** you've thought about

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MoneyChecking.git
   cd MoneyChecking
   ```
3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your `.env` file**:
   ```env
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Set up the database**:
   ```bash
   psql -d money_stuff -f data_base_code/database.sql
   ```

#### Making Changes

1. **Write clean, readable code**
   - Follow PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Keep functions focused and single-purpose

2. **Test your changes**
   - Test with sample data (never commit real financial data)
   - Ensure existing functionality still works
   - Test edge cases

3. **Update documentation**
   - Update README.md if you add features
   - Update CLAUDE.md if you change architecture
   - Add comments for complex logic

#### Code Style

- Use meaningful variable and function names
- Follow existing code patterns in the project
- Keep lines under 100 characters where possible
- Use type hints where appropriate

Example:
```python
def process_transaction(amount: float, merchant: str) -> Dict[str, Any]:
    """
    Process a single transaction.

    Args:
        amount: Transaction amount in dollars
        merchant: Merchant name

    Returns:
        Dictionary containing processed transaction data
    """
    # Implementation
    pass
```

#### Security Considerations

- **Never commit sensitive data**:
  - API keys, passwords, or credentials
  - Real transaction data (use fake data for examples)
  - Personal information

- **Use environment variables** for all secrets
- **Validate inputs** to prevent injection attacks
- **Use parameterized queries** for database operations

#### Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template with:
     - Description of changes
     - Related issue numbers
     - Testing performed
     - Screenshots (if applicable)

#### Pull Request Guidelines

- **One feature per PR** - Keep PRs focused
- **Update tests** if you change functionality
- **Update documentation** for new features
- **Respond to feedback** promptly
- **Keep PRs small** - Easier to review

### Adding New Card Types

To add support for a new credit card:

1. **Create a new processor class** inheriting from `AddTransactions`
2. **Implement required methods**:
   - `read_files()` - Parse the card's file format
   - `clean_data()` - Standardize the data
3. **Update main.py** to include the new processor
4. **Update README.md** with the new card support
5. **Add sample data format** to documentation

Example:
```python
class NewCardTransactions(AddTransactions):
    def __init__(self, db_config: dict, person: str):
        super().__init__(db_config, person)
        self.account_type = 'New Card'

    def read_files(self, file_paths: List[str]) -> pd.DataFrame:
        # Implementation
        pass

    def clean_data(self) -> pd.DataFrame:
        # Implementation
        pass
```

### Code of Conduct

- **Be respectful** and constructive in discussions
- **Welcome newcomers** and help them get started
- **Focus on the code**, not the person
- **Accept constructive criticism** gracefully
- **Give credit** where credit is due

### Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Open a new issue with the `question` label
3. Be specific about what you need help with

## Recognition

Contributors will be recognized in the project README. Thank you for helping improve Money Review!

## License

By contributing to Money Review, you agree that your contributions will be licensed under the MIT License.
