# SENetworkAppManager
Network System of speech extraction .Net+Python based on manual TCP realization (System.Net.Sockets)
Setup instructions. In PowerSHell:

git clone https://github.com/guranik/SENetworkAppManager

cd SENetworkAppManager

PowerShell -ExecutionPolicy Bypass -File setup_senetworkappmanager.ps1

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

venv\Scripts\activate

python split_audio.py


sequenceDiagram
    autonumber
    participant C1 as Клиент 1 (User A)
    participant C2 as Клиент 2 (User B)
    participant M as Менеджер (Центральный узел)
    participant W1 as Воркер 1
    participant W2 as Воркер 2

    Note over C1, W2: Фаза 1: Инициализация и поддержание соединений

    par Подключение участников
        C1->>M: Установка TCP соединения (Логин: User A)
        C2->>M: Установка TCP соединения (Логин: User B)
        W1->>M: Установка постоянного TCP соединения (Регистрация воркера)
        W2->>M: Установка постоянного TCP соединения (Регистрация воркера)
    end

    loop Heartbeat (Фоновый процесс)
        Note right of W2: Воркеры периодически сообщают о своем состоянии
        W1-->>M: Heartbeat (ID: W1, Status: Free)
        W2-->>M: Heartbeat (ID: W2, Status: Free)
        Note left of M: Менеджер обновляет таблицу состояния ресурсов
    end

    Note over C1, W2: Фаза 2: Полный цикл обработки задачи от Клиента 1

    rect rgb(240, 248, 255)
    note right of C1: Клиент 1 начинает работу
    C1->>>M: Загрузка исходного аудиофайла (Задача 1)
    activate M
    Note left of M: Создание директорий: user_A/{input, segments, output}<br/>Сохранение файла в user_A/input

    note right of M: Этап Сегментации
    M->>W1: Команда на сегментацию (Файл, параметры: max_segment_size)
    activate W1
    Note right of W1: Выполнение split_audio.py<br/>Генерация файлов segment.N.time
    W1-->>M: Передача файлов-сегментов (N штук)
    deactivate W1
    Note left of M: Сохранение в user_A/segments<br/>Добавление сегментов в очередь задач

    note right of M: Этап Транскрипции (Распределение по воркерам)
    
    par Параллельная обработка сегментов
        rect rgb(230, 230, 250)
        note right of W2: Воркер 2 свободен
        W2->>M: Запрос задачи (Я свободен)
        M->>W2: Отправка Сегмента 1 (из очереди)
        activate W2
        Note right of W2: Сохранение локально<br/>Запуск transcribe_audio.py (Whisper small)
        W2-->>M: Отправка результата транскрипции (.txt)
        Note right of W2: Удаление локальных файлов сегмента
        deactivate W2
        M->>M: Сохранение в user_A/output
        end

        rect rgb(230, 230, 250)
        note right of W1: Воркер 1 освободился после сегментации
        W1->>M: Запрос задачи (Я свободен)
        M->>W1: Отправка Сегмента 2 (из очереди)
        activate W1
        Note right of W1: Запуск transcribe_audio.py
        W1-->>M: Отправка результата транскрипции (.txt)
        deactivate W1
        M->>M: Сохранение в user_A/output
        end
    end
    
    Note left of M: Очередь сегментов пуста.<br/>Все результаты собраны в user_A/output

    note right of M: Завершение
    M->>C1: Передача итоговых текстовых транскриптов
    deactivate M
    note right of C1: Клиент получает результат
    end

    Note over C1, W2: Фаза 3: Завершение сессии

    C1->>M: Отключение / Завершение сессии
    Note left of M: Удаление рабочей директории user_A со всеми временными данными

    Note right of C2: Клиент 2 может начать аналогичный процесс параллельно,<br/>менеджер будет распределять его сегменты между W1 и W2 по мере их освобождения.
