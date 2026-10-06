# LLM App (Node.js/TypeScript)

Simple Node.js/TypeScript application để gọi LLM API sử dụng Anthropic Claude.

## Cài đặt

1. Clone repository này
2. Cài đặt dependencies:
   ```bash
   npm install
   # hoặc
   yarn install
   # hoặc
   pnpm install
   ```

3. Tạo file `.env` từ template:
   ```bash
   cp .env.example .env
   ```

4. Cập nhật `.env` với API key của bạn:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key
   ANTHROPIC_API_URL=https://api.anthropic.com
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ```

## Sử dụng

### Development mode (với hot reload)
```bash
npm run dev
```

### Build và chạy production
```bash
npm run build
npm start
```

### Type checking
```bash
npm run typecheck
```

## Cấu trúc

- `src/index.ts`: File chính chứa logic gọi LLM API
- `.env.example`: Template cho environment variables
- `.env`: File chứa API key (không commit vào git)
- `package.json`: Cấu hình project và dependencies
- `tsconfig.json`: Cấu hình TypeScript compiler

## Dependencies

- `@anthropic-ai/sdk`: SDK chính thức của Anthropic để gọi Claude API
- `dotenv`: Load environment variables từ file .env
- `typescript`: TypeScript compiler
- `tsx`: TypeScript execution và watch mode cho development

## Yêu cầu hệ thống

- Node.js >= 18.0.0
- npm/yarn/pnpm

## So sánh với Python version

Phiên bản Node.js/TypeScript này có các tính năng tương đương:

1. **Agent loop** với termination conditions (natural stop, budget stop)
2. **Tool execution** với guardrails (chỉ cho phép read-only commands)
3. **Session state** management với messages array
4. **Error handling** cho tool execution và timeout
5. **JSON formatting** với jq fallback
6. **Type safety** với TypeScript

### Khác biệt chính:

- Sử dụng `async/await` thay vì synchronous code
- Type definitions cho tất cả functions và variables
- ESM modules thay vì CommonJS
- `tsx` cho development hot reload
