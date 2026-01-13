# Telegram Bot 專案結構說明

## 📁 專案架構

本專案已重構為模組化結構，便於維護和擴展：

```
tg mini app/
├── bot.py              # 主程式入口（精簡版，只負責啟動）
├── config.py           # 配置檔案（Token、地址、URL等）
├── messages.py         # 訊息模板模組（所有訊息內容）
├── keyboards.py        # 鍵盤布局模組（所有按鈕菜單）
├── handlers.py         # 處理器模組（所有業務邏輯）
├── state.py            # 狀態管理模組（用戶菜單狀態）
├── requirements.txt    # 依賴套件
└── README.md          # 本文件
```

## 📝 各模組說明

### 1. `bot.py` - 主程式入口
- **職責**：應用程式啟動和初始化
- **內容**：
  - 配置 Application
  - 註冊處理器
  - 啟動 Bot
- **行數**：約 80 行（從 731 行精簡到 80 行）

### 2. `config.py` - 配置檔案
- **職責**：存放所有配置項
- **內容**：
  - `BOT_TOKEN` - Telegram Bot Token
  - `VERIFICATION_ADDRESS` - 認證地址
  - `VERIFICATION_AMOUNT` - 認證金額
  - `WEBAPP_BASE_URL` - Web App URL
  - 超時配置

### 3. `messages.py` - 訊息模板
- **職責**：所有訊息內容的生成函數
- **函數**：
  - `get_welcome_message()` - 歡迎訊息
  - `get_verify_address_message()` - 認證地址訊息
  - `get_profile_message()` - 個人中心訊息
  - `get_platform_verify_message()` - 平台驗資訊息
  - `get_self_exchange_message()` - 自助兌換訊息
  - `get_rebate_settings_message()` - 返水設置訊息
  - `get_start_game_message()` - 開始遊戲訊息

### 4. `keyboards.py` - 鍵盤布局
- **職責**：所有按鈕菜單的生成函數
- **函數**：
  - `get_home_keyboard()` - 首頁菜單
  - `get_game_level1_keyboard()` - 第一層遊戲菜單
  - `get_game_level2_keyboard()` - 第二層遊戲菜單
  - `get_profile_keyboard()` - 個人中心菜單
  - `get_rebate_settings_keyboard()` - 返水設置菜單

### 5. `handlers.py` - 處理器模組
- **職責**：所有業務邏輯處理
- **函數**：
  - `start_command()` - 處理 /start 命令
  - `show_start_game_info()` - 顯示開始遊戲資訊
  - `handle_inline_buttons()` - 處理 Inline 按鈕點擊
  - `handle_reply_keyboard()` - 處理 Reply Keyboard 按鈕點擊

### 6. `state.py` - 狀態管理
- **職責**：管理用戶的菜單狀態
- **函數**：
  - `get_user_state()` - 獲取用戶狀態
  - `set_user_state()` - 設置用戶狀態
  - `reset_user_state()` - 重置用戶狀態

## 🎯 重構優勢

### ✅ 代碼組織
- **模組化**：每個模組職責單一，易於理解
- **可維護性**：修改訊息只需編輯 `messages.py`
- **可擴展性**：新增功能只需在對應模組添加

### ✅ 維護便利
- **訊息修改**：只需編輯 `messages.py`
- **按鈕調整**：只需編輯 `keyboards.py`
- **邏輯變更**：只需編輯 `handlers.py`
- **配置更新**：只需編輯 `config.py`

### ✅ 代碼量對比
- **重構前**：`bot.py` 731 行（所有功能混在一起）
- **重構後**：
  - `bot.py`：80 行（主入口）
  - `config.py`：23 行
  - `messages.py`：172 行
  - `keyboards.py`：112 行
  - `handlers.py`：378 行
  - `state.py`：24 行

## 🚀 使用方式

### 啟動 Bot
```bash
python bot.py
```

### 修改配置
編輯 `config.py` 文件，修改 Bot Token、地址等配置。

### 修改訊息
編輯 `messages.py` 文件，修改各種訊息內容。

### 修改按鈕
編輯 `keyboards.py` 文件，調整按鈕布局。

### 新增功能
1. 在 `messages.py` 添加新訊息函數
2. 在 `keyboards.py` 添加新鍵盤函數（如需要）
3. 在 `handlers.py` 添加處理邏輯

## 📋 依賴套件

見 `requirements.txt`：
- python-telegram-bot>=20.0

## 🔧 開發建議

1. **訊息內容**：統一在 `messages.py` 管理，便於多語言支持
2. **按鈕布局**：統一在 `keyboards.py` 管理，便於 UI 調整
3. **業務邏輯**：統一在 `handlers.py` 管理，便於功能擴展
4. **配置管理**：統一在 `config.py` 管理，可考慮使用環境變數

## 📌 注意事項

- 所有模組使用相對導入，確保在同一目錄下運行
- 配置中的敏感信息（如 Token）建議使用環境變數
- 狀態管理目前使用內存字典，重啟後會丟失（可考慮持久化）

