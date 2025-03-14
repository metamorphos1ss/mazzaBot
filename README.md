# Гайд по установке и настройке тг бота

## 📌 Зависимости
Убедитесь что у вас есть следующее, перед тем как продолжить:
- Валидный **Токен Телеграмм Тота** (полученный через [@BotFather](https://t.me/BotFather))
- Ваш **Телеграмм ID** для админский привилегий (его можно получить через [@userinfobot](https://t.me/userinfobot))
- Установленный **git, docker, docker-compose**

## 🚀 Установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/metamorphos1ss/mazzaBot
   cd mazzaBot
   ```

2. **Создайте настройки окружения из шаблона**
   ```bash
   cp .env-example .env
   ```

3. **Настройте окружение**
   Откройте `.env` и поместите в него токен и админ id:
   ```ini
   TOKEN=123456789
   ADMIN_ID=123456789
   ```

   - `TOKEN`: Ваш телеграмм токен из [@BotFather](https://t.me/BotFather).
   - `ADMIN_ID`: Ваш админ id для использования рассылки рекламы.

4. **Запуск docker**
   ```bash
   sudo docker-compose up -d
   ```


## 🛠 Функции
- /start для вывода информации в формате markdown v2
- Рассылка рекламы с возможностью добавить ссылку под пост

---
💡 Контакты [Telegram](https://t.me/vnxcmk)

