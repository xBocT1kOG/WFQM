# RU:
# 🌦️ Odessa AI Weather Bot & Analytics

**Автоматизированный ETL-пайплайн для сбора, анализа и прогнозирования погоды с использованием AI.**

Этот проект — не просто погодный бот. Это полноценная система мониторинга, которая собирает исторические данные, оценивает точность собственных прогнозов и генерирует отчеты с уникальной личностью ("Одесский колорит") благодаря Google Gemini.

---

## 🚀 Задачи проекта

1.  **Сбор данных (ETL):** Ежечасный сбор реальных данных и прогнозов с OpenWeatherMap.
2.  **Хранение:** Надежное сохранение очищенных данных в облачную базу данных (Supabase/PostgreSQL).
3.  **Аналитика:** Сравнение "Обещаний" (прогноза) с "Реальностью" (фактической погодой) за последние 3 дня.
4.  **AI-Репортинг:** Генерация ежедневных утренних сводок на естественном языке с использованием LLM.
5.  **Автоматизация:** Полный CI/CD цикл на GitHub Actions (работает по расписанию без сервера 24/7).

---

## 🛠️ Инструменты и Стек

Проект построен на современном стеке Data Engineering:

* **Язык:** `Python 3.10` (Pandas, Requests)
* **AI & LLM:** `Google Gemini 2.0 Flash` (via `google-genai` SDK) — генерация текста и анализ контекста.
* **База данных:** `Supabase` (PostgreSQL) — хранение временных рядов (Time Series data).
* **API Погоды:** `OpenWeatherMap` — источник сырых данных.
* **Оркестрация:** `GitHub Actions` — запуск скриптов по Cron-расписанию (сбор данных каждый час, отчет утром).
* **Уведомления:** `Telegram Bot API` — доставка контента пользователю.

---

## ⚙️ Как это работает

1.  **Data Miner:** Скрипт запускается каждый час, запрашивает текущую погоду и прогноз на 5 дней. Данные очищаются от мусора (`NaN`), типизируются и загружаются в Supabase (с защитой от дублей через `.upsert`).
2.  **Morning Briefing:** Каждое утро запускается аналитический скрипт:
    * Берет свежий прогноз на сегодня.
    * Выгружает из базы прогноз, который давался *вчера* на *сегодня*, и реальную погоду.
    * Скармливает всё это нейросети Gemini с системным промптом "Саркастичный одесский метеоролог".
3.  **Cleanup:** Автоматическая очистка базы от записей старше 30 дней для экономии места.

---

## 💬 Пример результата работы

Бот не просто пишет цифры, он "общается". Вот реальный пример утреннего сообщения:

> "Ой, ну здрасьте! Явились, не запылились за своим прогнозом.
>
> **Утром** будет **+3...+4** градуса, без осадков.
> **Днем** потеплеет до **+5** градусов, тоже без дождя.
> **Вечером** температура опустится до **+4...+5** градусов, сухо.
>
> Что сказать за завтра? Нас ждет еще один день из серии "одесская зима, ты пьяна, иди домой". Утром, где-то в 8:00, столбик термометра покажет +4°C, ощущаться будет как -1°C из-за влажности 95% и ветра 7 м/с с порывами до 13 м/с. Днем, часам к 14:00, будет до +5°C, но ощущаться +1°C, при порывистом ветре до 15 м/с.
>
> С неба, как видите, ничего не падает – никаких дождей, только сплошные облака. Температура, заметьте, явно выше, чем принято в феврале – обычно мы мерзнем сильнее.
>
> Если судить по прошлому, прогноз этот – почти как моя тетя Роза: на 90% правду говорит. Так что да, доверять можно.
>
> Ну, вот вам и вся метеорология. Бывайте!"

---

# EN:
# 🌦️ Odessa AI Weather Bot & Analytics

**Automated ETL pipeline for weather data collection, analysis, and AI-driven forecasting.**

This project is not just a simple weather bot. It is a full-cycle monitoring system that collects historical data, evaluates the accuracy of its own predictions, and generates daily reports with a unique personality ("Odesa humor") using Google Gemini AI.

---

## 🚀 Key Features

1.  **Data Collection (ETL):** Hourly fetching of real-time weather and 5-day forecasts from OpenWeatherMap.
2.  **Storage:** Secure storage of cleaned time-series data in a cloud database (Supabase/PostgreSQL).
3.  **Analytics:** Automated comparison of "Promises" (yesterday's forecast) vs. "Reality" (actual weather) for the last 3 days.
4.  **AI Reporting:** Generation of daily morning briefings in natural language using LLM (Gemini).
5.  **Automation:** Fully automated CI/CD cycle via GitHub Actions (serverless cron jobs).

---

## 🛠️ Tech Stack

The project is built on a modern Data Engineering stack:

* **Language:** `Python 3.10` (Pandas, Requests)
* **AI & LLM:** `Google Gemini 2.0 Flash` (via `google-genai` SDK) — context analysis and text generation.
* **Database:** `Supabase` (PostgreSQL) — storage for historical and forecast data.
* **Weather API:** `OpenWeatherMap` — raw data source.
* **Orchestration:** `GitHub Actions` — scheduled cron jobs (hourly mining, daily reporting).
* **Notifications:** `Telegram Bot API` — content delivery.

---

## ⚙️ How It Works

1.  **Data Miner:** A script runs every hour to fetch current weather and forecasts. Data is cleaned (handling `NaN` values), typed, and uploaded to Supabase (using `.upsert` to prevent duplicates).
2.  **Morning Briefing:** An analytical script runs every morning:
    * Retrieves fresh forecasts for today.
    * Extracts *yesterday's* forecast for *today* and compares it with *actual* recorded weather.
    * Feeds this context into the Gemini neural network with a "Sarcastic Odesa Meteorologist" system prompt.
3.  **Cleanup:** Automatic data retention policy removes records older than 30 days to optimize storage.

---

## 💬 Example Output

The bot doesn't just output numbers; it "talks." Here is an example of a generated morning report:

> "Oh, look who decided to show up for the forecast! Finally.
>
> **Morning:** Expect **+3...+4°C**, no precipitation.
> **Day:** Warming up to **+5°C**, still no rain.
> **Evening:** Dropping back to **+4...+5°C**, dry.
>
> So, what about tomorrow? We are looking at another episode of 'Odesa winter, go home, you're drunk.' around 8:00 AM, the thermometer will show +4°C, but it will feel like -1°C thanks to our lovely 95% humidity and wind gusts up to 13 m/s. By 2:00 PM, it hits +5°C, feeling like +1°C, with wind trying to blow your hat off at 15 m/s.
>
> As you can see, nothing is falling from the sky – no rain, just endless clouds. Note that the temperature is suspiciously high for February; usually, we freeze more than this.
>
> Judging by past performance, this forecast is like my Aunt Rosa: telling the truth 90% of the time. So yes, you can trust it.
>
> Well, that's all the meteorology for today. Be well!"

---