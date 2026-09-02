# Інструкція з налаштування Firebase для КОМПУТЕРРА

## Крок 1: Створення проєкту Firebase

1. Перейдіть на https://console.firebase.google.com/
2. Натисніть "Додати проєкт" (Add project)
3. Введіть назву проєкту: `komputerra-solar`
4. Вимкніть Google Analytics (не обов'язково для цього проєкту)
5. Натисніть "Створити проєкт"

## Крок 2: Додавання веб-додатку

1. На головній сторінці проєкту натисніть іконку `</>`  (Web)
2. Введіть назву додатку: `KOMPUTER
RA Website`
3. Натисніть "Зареєструвати додаток"
4. **ЗБЕРЕЖІТЬ** конфігурацію Firebase (firebaseConfig) - вона знадобиться далі

Конфігурація виглядає так:
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "komputerra-solar.firebaseapp.com",
  projectId: "komputerra-solar",
  storageBucket: "komputerra-solar.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc..."
};
```

## Крок 3: Налаштування Firestore Database

1. В меню зліва виберіть "Firestore Database"
2. Натисніть "Створити базу даних" (Create database)
3. Виберіть "Почати в тестовому режимі" (Start in test mode)
4. Виберіть локацію: `europe-west1` (Бельгія) для України
5. Натисніть "Увімкнути"

### Налаштування правил безпеки:

В розділі "Rules" замініть правила на:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Дозволити всім читати та писати замовлення (для demo)
    match /orders/{orderId} {
      allow read, write: if true;
    }
    
    // Для продакшн використовуйте:
    // match /orders/{orderId} {
    //   allow create: if true; // Клієнти можуть створювати
    //   allow read, update, delete: if request.auth != null; // Тільки авторизовані (адміни)
    // }
  }
}
```

**Важливо:** Після тестування змініть правила на продакшн-версію!

## Крок 4: Налаштування Authentication

1. В меню зліва виберіть "Authentication"
2. Натисніть "Почати" (Get started)
3. Виберіть "Email/Password" як метод входу
4. Увімкніть "Email/Password"
5. Натисніть "Зберегти"

### Створення адмін-користувача:

1. Перейдіть на вкладку "Users"
2. Натисніть "Додати користувача" (Add user)
3. Введіть:
   - Email: `admin@komputerra.ua`
   - Пароль: `ваш_надійний_пароль` (мінімум 6 символів)
4. Натисніть "Додати користувача"

## Крок 5: Оновлення коду на сайті

### 5.1. Оновити `cart.html`:

Знайдіть рядок 324 (приблизно):
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  ...
};
```

Замініть на вашу конфігурацію з Кроку 2.

### 5.2. Оновити `admin.html`:

Знайдіть рядок 567 (приблизно):
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  ...
};
```

Замініть на вашу конфігурацію з Кроку 2.

## Крок 6: Тестування

### Тест замовлення (клієнтська частина):

1. Відкрийте `index.html`
2. Додайте товар до кошика
3. Перейдіть до кошика (`cart.html`)
4. Заповніть форму замовлення
5. Натисніть "Підтвердити замовлення"
6. Перевірте, чи з'явилось замовлення у Firebase Console → Firestore Database → orders

### Тест адмін-панелі:

1. Відкрийте `admin.html`
2. Увійдіть з email та паролем створеного користувача
3. Перевірте, чи відображаються замовлення
4. Спробуйте змінити статус замовлення

## Крок 7: Деплой на GitHub Pages

1. Закоммітьте зміни:
```bash
git add cart.html admin.html FIREBASE_SETUP.md
git commit -m "Add cart and admin panel with Firebase integration"
git push origin main
```

2. Файли будуть доступні за адресами:
   - Каталог: `https://pechenij.github.io/solar-catalog/`
   - Кошик: `https://pechenij.github.io/solar-catalog/cart.html`
   - Адмінка: `https://pechenij.github.io/solar-catalog/admin.html`

## Режим Demo (без Firebase)

Якщо Firebase ще не налаштований:

- **Кошик** працює з LocalStorage
- **Адмінка** має demo-режим з тестовими даними
  - Email: `admin@komputerra.ua`
  - Пароль: `admin123`

## Troubleshooting

### Помилка "Firebase: Error (auth/invalid-api-key)"
- Перевірте правильність `apiKey` в конфігурації

### Замовлення не зберігаються
- Перевірте правила Firestore (Крок 3)
- Перевірте консоль браузера (F12) на помилки

### Не вдається увійти в адмін-панель
- Перевірте, чи створено користувача в Authentication
- Перевірте правильність email та паролю
- Спробуйте demo-режим для тестування інтерфейсу

## Додаткові можливості

### Сповіщення на email (опціонально)

Для отримання email-сповіщень про нові замовлення потрібно налаштувати Firebase Cloud Functions:

```bash
firebase init functions
cd functions
npm install nodemailer
```

Створіть тригер на нові документи в колекції `orders`.

### Telegram Bot (альтернатива)

Для швидких сповіщень можна інтегрувати Telegram Bot:
1. Створіть бота через @BotFather
2. Отримайте токен
3. Додайте Cloud Function для відправки повідомлень

## Контакти підтримки

Firebase Documentation: https://firebase.google.com/docs
Firebase Console: https://console.firebase.google.com/
