# 📦 Model bazy danych – Aplikacja fitness

## 🧍 Użytkownicy – `users`
```json
{
  "_id": "ObjectId",
  "username": "ola",
  "email": "ola@example.com",
  "password": "hashed_password",
  "role": "user" | "admin"
}
```

## 📅 Kalendarz ćwiczeń – `calendar`
Każdy dokument reprezentuje 1 dzień i jest powiązany z użytkownikiem.

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "date": "2025-04-20",
  "steps": 8350,
  "maxSteps": 10000,
  "hours": [
    {
      "hour": "08:00",
      "exercises": [
        {
          "exercise_id": "ObjectId",
          "duration_min": 30,
          "numberOfSets": 5,
          "numberOfRepetitions": 3,
          "weight": 2.5,
          "intervalBetween_days": 2,
          "done": "False",
          "notes": "Wolne tempo"
        }
      ]
    }
  ]
}
```

## 🏋️‍♂️ Ćwiczenia – `exercises`
Opis dostępnych ćwiczeń wraz z linkiem do filmu wideo (z MinIO).

```json
{
  "_id": "ObjectId",
  "name": "Plank",
  "description": "Pozycja deski przez 30 sekund",
  "video_url": "https://minio.localhost/bucket/plank.mp4",
  "thumbnail_url": "https://minio.localhost/bucket/plank_thumb.jpg",
  "exerciseType": "core",
  "difficulty": "medium"
}
```

## 🗂️ Relacje

- `calendar.user_id` ➝ `users._id`
- `calendar.hours[].exercises[].exercise_id` ➝ `exercises._id`

## Notatki
Pewien formularz/standard musi zostać stworzony po stronie *Frontendu*.
Wtedy okresowe powtórki mogą być przetworzone przez *API*.

Propozycja:


### Dodawanie ćwiczeń do kalendarza

**RequestBody**

```json
{
  "startDate": "2025-04-20",
  "stopDate": "2025-08-20", 
  "hours": [
    {
      "hour": "08:00",
      "exercises": [
        {
          "exercise_id": "ObjectId",
          "duration_min": 30,
          "numberOfSets": 5,
          "numberOfRepetitions": 3,
          "weight": 2.5,
          "intervalBetween_days": 2,
          "done": "False",
          "notes": "Wolne tempo"
        }
      ]
    },
    {
      "hour": "09:00",
      "exercises": [
        {
          "exercise_id": "ObjectId",
          "duration_min": 20,
          "numberOfSets": 5,
          "numberOfRepetitions": 3,
          "weight": 2,
          "intervalBetween_days": 0,
          "done": "False",
          "notes": "Szybkie tempo"
        }
      ]
    }
  ]
}
```

Utworzy 5 dokumentów na następne 5 dni, usunięcie lub zmiana będzie wymagać tych samych danych co utworzenie.
Dokumenty muszą zostać odszukane i zmienione.

### Usuwanie ćwiczeń z kalendarza
Jeśli chodzi tylko o usunięcie to cały dzień może zostać usunięty.

**RequestBody**

```json
{
  "startDate": "2025-04-20",
  "stopDate": "2025-08-20"
}
```
### Modyfikowanie ćwiczeń z kalendarza
Wymaga podanaia szczegółów odnośnie zmian

**RequestBody**

```json
{
  "startDate": "2025-04-20",
  "stopDate": "2025-08-20", 
  "hours": [
    {
      "hour": "09:00",
      "exercises": [
        {
          "exercise_id": "ObjectId",
          "duration_min": 20,
          "numberOfSets": 5,
          "numberOfRepetitions": 3,
          "weight": 2,
          "intervalBetween_days": 0,
          "done": "False",
          "notes": "Szybkie tempo"
        }
        
      ]
    }
  ]
}

```
Znajdzie i zmieni dokumenty o tych datach, jeśli nic nie ma o tej godzinie to doda, jeśli jest to nadpisze.

