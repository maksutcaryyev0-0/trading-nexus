# NEXUS Trading OS
## Деплой через GitHub → Railway + Vercel (бесплатно)

---

## ШАГ 1 — Создай GitHub репозиторий

1. Заходишь на **github.com**
2. Нажимаешь **"New repository"** (зелёная кнопка)
3. Название: `nexus-trading`
4. Выбираешь **Private** (только ты видишь)
5. Нажимаешь **"Create repository"**

### Загрузи файлы:
1. Нажми **"Add file"** → **"Upload files"**
2. Перетащи ВСЕ файлы из архива nexus_v3.zip
3. Внизу нажми **"Commit changes"**

---

## ШАГ 2 — База данных на Railway (бесплатно)

1. Заходишь на **railway.app**
2. Нажимаешь **"Start a New Project"**
3. Выбираешь **"Deploy PostgreSQL"**
   - Railway создаёт PostgreSQL автоматически
   - Копируешь `DATABASE_URL` из вкладки Variables
4. Нажимаешь **"+ New"** → **"Database"** → **"Redis"**
   - Копируешь `REDIS_URL` из вкладки Variables

---

## ШАГ 3 — Backend на Railway

1. В Railway нажми **"+ New"** → **"GitHub Repo"**
2. Выбираешь свой репозиторий `nexus-trading`
3. Railway автоматически видит `railway.json` и деплоит

### Добавь переменные окружения:
Нажми на сервис → вкладка **"Variables"** → кнопка **"Add Variables"**

Вставляй по одной (обязательные):

```
SECRET_KEY=сюда_вставь_любую_длинную_строку_из_букв_и_цифр
MASTER_PASSWORD=твой_мастер_пароль
ENCRYPTION_KEY=ровно_32_символа_здесь123456789
JWT_SECRET=ещё_одна_длинная_случайная_строка
POSTGRES_PASSWORD=твой_пароль_бд
REDIS_PASSWORD=твой_пароль_redis
DATABASE_URL=вставь_из_шага_2
REDIS_URL=вставь_из_шага_2
ENVIRONMENT=production
DEBUG=false
TIMEZONE=Europe/Moscow
ANTHROPIC_API_KEY=sk-ant-твой_ключ_сюда
TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather
TELEGRAM_ADMIN_ID=твой_telegram_id
```

4. Нажми **"Deploy"** — Railway запускает backend
5. Копируешь URL вида `https://nexus-trading-production.up.railway.app`

---

## ШАГ 4 — Frontend на Vercel

1. Заходишь на **vercel.com**
2. Нажимаешь **"Add New Project"**
3. Выбираешь **"Import Git Repository"** → находишь `nexus-trading`
4. В настройках проекта:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Добавляешь переменную окружения:
   ```
   VITE_API_URL=https://nexus-trading-production.up.railway.app
   ```
   (URL из шага 3)
6. Нажимаешь **"Deploy"**
7. Vercel даёт URL вида `https://nexus-trading.vercel.app`

---

## ШАГ 5 — Telegram бот

1. Открываешь Telegram → находишь **@BotFather**
2. Пишешь `/newbot`
3. Называешь бота: `NEXUS Trading Bot`
4. Username: `nexus_trading_yourname_bot`
5. BotFather даёт токен — вставляешь в Railway как `TELEGRAM_BOT_TOKEN`

Узнать свой Telegram ID:
- Пишешь боту **@userinfobot**
- Он отвечает твоим ID — вставляешь как `TELEGRAM_ADMIN_ID`

---

## ШАГ 6 — Проверка

Открываешь в браузере:
- **Dashboard**: `https://nexus-trading.vercel.app`
- **API docs**: `https://nexus-trading-production.up.railway.app/api/docs`
- **Health check**: `https://nexus-trading-production.up.railway.app/health`

Пробуешь войти: `admin` / `nexus2024`

---

## ШАГ 7 — Добавление API ключей

Все ключи добавляются через Railway Variables — не нужно трогать код.

### Бесплатные ключи (регистрируйся по очереди):

| Сервис | Сайт | Переменная |
|--------|------|------------|
| Google Gemini | aistudio.google.com | `GEMINI_API_KEY` |
| Groq | groq.com | `GROQ_API_KEY` |
| TwelveData | twelvedata.com | `TWELVE_DATA_KEY` |
| FRED (макро) | fred.stlouisfed.org/docs/api | `FRED_API_KEY` |
| NewsAPI | newsapi.org | `NEWS_API_KEY` |
| CoinMarketCap | coinmarketcap.com/api | `CMC_API_KEY` |
| Alpha Vantage | alphavantage.co | `ALPHA_VANTAGE_KEY` |
| DeepSeek | platform.deepseek.com | `DEEPSEEK_API_KEY` |
| Mistral | console.mistral.ai | `MISTRAL_API_KEY` |
| HuggingFace | huggingface.co | `HUGGINGFACE_API_KEY` |

---

## Автоматический деплой

После настройки — каждый раз когда ты делаешь изменения в GitHub:
- Railway автоматически обновляет backend
- Vercel автоматически обновляет frontend

Код меняешь → push в GitHub → сайт обновился сам.

---

## Стоимость

| Платформа | Бесплатно |
|-----------|-----------|
| GitHub | ✅ Всегда бесплатно |
| Railway | ✅ $5 кредитов/мес бесплатно |
| Vercel | ✅ Бесплатный план навсегда |
| Anthropic Claude API | ~$10/мес |
| **Итого** | **~$10/мес** |

---

## Если что-то не работает

**Backend не запускается:**
- Проверь Variables в Railway — все обязательные поля заполнены?
- Смотри логи: Railway → твой сервис → вкладка "Logs"

**Frontend не открывается:**
- Проверь `VITE_API_URL` в Vercel — правильный URL Railway?
- Смотри логи: Vercel → твой проект → "Deployments"

**Telegram бот не отвечает:**
- Проверь `TELEGRAM_BOT_TOKEN` в Railway Variables
- Написал ли боту `/start`?

---

## Переход на VPS (когда будешь готов)

Когда захочешь перейти на постоянный сервер:
1. Берёшь Hetzner VPS за €3.79/мес
2. Устанавливаешь Docker
3. Копируешь проект с GitHub
4. `docker compose up -d`
5. Всё работает так же, но быстрее и без ограничений

---

*NEXUS Trading OS — система никогда не торгует без твоего подтверждения.*
