# 🍲 Foodgram Project

## Описание проекта

Проект представляет собой сервис, с помощью которого пользователи могут делиться своими любимыми рецептами,
сохранять понравившиеся рецепты в избранное, а также выгружать список необходимых ингредиентов для приготовления выбранных блюд. 

## Проект разработан с использованием следующих технологий и инструментов:

## 🛠️ Technologies & Tools

**Backend:**

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django Rest Framework](https://img.shields.io/badge/Django%20REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

**Frontend:**

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**Инфраструктура:**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

**Языки программирования:**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## Основные возможности проекта

1. **Аутентификация и авторизация**
   - Поддержка JWT токенов для безопасной аутентификации пользователей.
   - Регистрация, вход, выход и восстановление пароля.

2. **Управление данными**
   - CRUD операции для управления данными (создание, чтение, обновление, удаление).
   - Оптимизация запросов к базе данных с использованием Django ORM и PostgreSQL.

3. **Интерфейс пользователя**
   - Современный и отзывчивый интерфейс на базе React.
   - Поддержка многопользовательского режима работы с данными.

4. **DevOps и развертывание**
   - Упаковка и развёртывание приложения с использованием Docker и Docker Compose.
   - Настройка обратного прокси-сервера с использованием Nginx.
   - Автоматическое тестирование и деплой с использованием GitHub Actions.

## Установка и запуск проекта

1. **Клонирование репозитория:**

   ```bash
   git clone https://github.com/slavalyub/repository.git
   cd foodgram
   ```
2. **Запуск проекта локально с помощью Docker Compose:**
    ```bash
   sudo docker compose up --build
    ```
3. **Миграции базы данных**
    ```
    docker compose exec backend python manage.py migrate
   ```
4. **Создание суперпользователя:**
    ```
   docker-compose exec web python manage.py createsuperuser
   ```
5. **Приложение будет доступно по адресу:**
    ```
   https://localhost:8003
   ```
6. **Дополнительные ресурсы**
   - Документация API доступна по адресу: http://localhost:8003/docs/
   - Контакты: https://slavalyub.ru
   - Разработчик: Любченко Вячеслав
   - Контактная информация: v.lyub4enko@mail.ru
7. **Адрес Проекта**
   - https://foodgram.lyub4enko.ru i_cloud
   - https://yagram.lyubchenko.ru Я.Облако
8. **Доступ в админ зону**
   - ```I_cloud```
   - Логин: ```test```
   - Пароль: ```123```
   - ```Я.Облако```
   - Эл. Почта: ```admin@mail.ru```
   - Имя пользователя: ```admin```
   - Имя: ```admin```
   - Фамилия: ```admin```
   - Password: ```123```
