# LLMgine (Work in Progress)

LLMgine aims to be a comprehensive framework for building and managing interactions with Large Language Models (LLMs).
This project is under active development, focused on creating a unified and extensible system for LLM applications.

## Vision

The goal of LLMgine is to provide a complete framework that simplifies and standardizes how developers work with LLMs.
Key objectives include:

- **Universal LLM Integration**: A unified interface for working with any LLM provider
- **Flexible Architecture**: Support for different conversation patterns and interaction modes
- **Robust Tool System**: Standardized way to give LLMs access to external tools and functions
- **Application Framework**: Complete foundation for building LLM-powered applications

## Current State

The framework is in active development with several core components in place:

### Implemented Features

- Multi-provider support (OpenAI, Anthropic, Google Gemini, OpenRouter)
- Basic conversation engines
- Tool integration system
- CLI and Streamlit interfaces
- Example tools (file operations, calculator, Notion integration)

### Under Development

- Enhanced agent capabilities
- More sophisticated conversation management
- Additional provider integrations
- Expanded tool ecosystem
- Improved documentation and examples

## Project Structure

The project follows a modular architecture:

```
📁 src
├── 📁 framework          # Core framework components
│   ├── 📁 clients       # LLM provider integrations
│   ├── 📁 core          # Core engines and logic
│   ├── 📁 tool_calling  # Tool integration system
│   └── 📁 types        # Type definitions and models
├── 📁 interfaces        # User interfaces
└── 📁 programs          # Example implementations
```

## Getting Started

Note: This project is in development. APIs and interfaces may change.

### Basic Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Running Examples

Try the CLI interface:

```python
python src/programs/cli_chat.py
```

Or the web interface:

```python
streamlit run src/programs/streamlit_chat_app.py
```

## Contributing

This project is in active development and contributions are welcome. Areas that need work:

- Additional LLM provider integrations
- New conversation management patterns
- Tool development
- Documentation improvements
- Testing infrastructure
- Example applications

## License

MIT License

## Development Status

⚠️ **Note**: This is a work in progress. Expect frequent changes and updates.

The framework is being actively developed with a focus on:

1. Core architecture refinement
2. API stability
3. Documentation
4. Testing
5. Example implementations

Check back regularly for updates or watch the repository for changes.
