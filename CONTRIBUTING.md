# Contributing to VoiceBot Enterprise

Thank you for your interest in contributing to the AI-powered Two-Wheeler Sales VoiceBot! This document provides guidelines for contributing to the project.

## 🚀 Quick Start for Contributors

1. **Fork the Repository**

   ```bash
   git clone https://github.com/rMohamedIbrahim/AI-Sales-Assistant-Chatbot.git
   cd AI-Sales-Assistant-Chatbot
   ```

2. **Set Up Development Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   uvicorn main_simple:app --reload
   ```

## 🎯 How to Contribute

### Types of Contributions We Welcome

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new functionality
- 📖 **Documentation**: Improve guides and API docs
- 🌍 **Translations**: Add support for new languages
- 🔧 **Code Improvements**: Optimize performance and add features
- 🧪 **Testing**: Write and improve test coverage

### Before You Start

1. Check existing [Issues](https://github.com/rMohamedIbrahim/AI-Sales-Assistant-Chatbot/issues)
2. Look at [Pull Requests](https://github.com/rMohamedIbrahim/AI-Sales-Assistant-Chatbot/pulls)
3. Read our [Code of Conduct](CODE_OF_CONDUCT.md)

## 📝 Development Guidelines

### Code Style

- Follow **PEP 8** for Python code
- Use **meaningful variable names** and **comprehensive comments**
- Add **type hints** for all function parameters and returns
- Include **docstrings** for all classes and functions

### Example Code Style:

```python
def generate_intelligent_response(message: str, language: str = "en") -> dict:
    """
    Generate AI-powered response for user queries

    Args:
        message (str): User input message
        language (str): Language code (default: "en")

    Returns:
        dict: Response with message, intent, and confidence
    """
    # Implementation here
    pass
```

### Commit Message Format

Use clear, descriptive commit messages:

```
type(scope): brief description

feat(chat): add multilingual support for Hindi and Tamil
fix(api): resolve response timeout issues
docs(readme): update installation instructions
test(voice): add unit tests for speech recognition
```

### Branch Naming Convention

- `feature/feature-name` - For new features
- `fix/bug-description` - For bug fixes
- `docs/documentation-update` - For documentation
- `test/test-description` - For testing improvements

## 🔧 Technical Requirements

### For AI/NLP Contributions:

- Experience with **FastAPI**, **Python 3.9+**
- Knowledge of **NLP libraries** (transformers, spaCy)
- Understanding of **multilingual text processing**

### For Frontend Contributions:

- **JavaScript/HTML/CSS** proficiency
- **Chart.js** for data visualization
- **Speech Recognition API** experience

### For Backend Contributions:

- **FastAPI** and **async programming**
- **Database design** (MongoDB experience preferred)
- **RESTful API** development

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_chat.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

- Write tests for all new features
- Include edge cases and error scenarios
- Test multilingual functionality
- Add integration tests for API endpoints

## 🌍 Adding Language Support

To add a new language:

1. **Add language code** to `languages` dictionary in `script.js`
2. **Create translation mappings** for UI elements
3. **Update AI response generation** to handle new language
4. **Add test cases** for the new language
5. **Update documentation**

Example:

```python
# In main_simple.py
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
    'ta': 'தமிழ்',
    'your_lang': 'Your Language'  # Add here
}
```

## 📊 Performance Guidelines

- **Response Time**: Keep API responses under 1.5 seconds
- **Memory Usage**: Optimize for efficient memory consumption
- **Scalability**: Design for handling multiple concurrent users
- **Error Handling**: Implement comprehensive error catching

## 🚀 Feature Development Process

1. **Create an Issue**: Describe the feature with use cases
2. **Get Feedback**: Discuss implementation approach
3. **Create Branch**: Use proper naming convention
4. **Implement**: Follow coding standards
5. **Add Tests**: Ensure adequate test coverage
6. **Update Docs**: Include documentation updates
7. **Submit PR**: Provide detailed description

## 📋 Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits
- [ ] Screenshots for UI changes
- [ ] Performance impact considered

## 🎯 Specific Contribution Areas

### High Priority

- **Electric Vehicle Database**: Expand EV model information
- **Regional Language Support**: Add local Indian languages
- **Voice Recognition**: Improve speech-to-text accuracy
- **Analytics Dashboard**: Enhanced business metrics

### Medium Priority

- **CRM Integration**: Connect with popular CRM systems
- **Mobile Responsiveness**: Optimize for mobile devices
- **Caching System**: Implement response caching
- **Security Enhancements**: Add authentication features

## 💬 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and brainstorming
- **Email**: contact@example.com for private matters
- **Documentation**: Check existing docs first

## 🏆 Recognition

Contributors will be:

- Listed in project README
- Mentioned in release notes
- Invited to join core team (for significant contributions)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Happy Contributing! 🚀**

Let's build the best AI-powered sales assistant together!
