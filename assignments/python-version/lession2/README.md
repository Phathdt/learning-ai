# LLM App

Simple Python application để gọi LLM API sử dụng Anthropic Claude.

## Cài đặt

1. Clone repository này
2. Cài đặt dependencies:
   ```bash
   uv sync
   ```

3. Tạo file `.env` từ template:
   ```bash
   cp .env.example .env
   ```

4. Cập nhật `.env` với API key của bạn:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key
   ANTHROPIC_API_URL=https://api.anthropic.com
   ```

## Sử dụng

Chạy ứng dụng:
```bash
uv run main.py
```

## Cấu trúc

- `main.py`: File chính chứa logic gọi LLM API
- `.env.example`: Template cho environment variables
- `.env`: File chứa API key (không commit vào git)
- `pyproject.toml`: Cấu hình project và dependencies

## Dependencies

- `anthropic`: SDK chính thức của Anthropic để gọi Claude API
- `python-dotenv`: Load environment variables từ file .env
