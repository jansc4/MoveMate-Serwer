# Backend aplikacji mobilnej MoveMate

Ten projekt stanowi backend dla aplikacji mobilnej MoveMate, opartej na zestawie kontenerów Docker zdefiniowanych w pliku `docker-compose.yaml`. Aplikacja pełni rolę serwera, oferując następujące funkcjonalności:

* **Autentykacja użytkowników:** Zabezpieczony system logowania i rejestracji.
* **Przechowywanie danych:** Bezpieczne i wydajne przechowywanie danych aplikacji w bazie danych MongoDB.
* **Zarządzanie wideo:** Wgrywanie, przechowywanie i strumieniowe przesyłanie filmów za pomocą MinIO.

## Architektura

Backend MoveMate opiera się na mikrousługowej architekturze, wykorzystującej następujące technologie:

* **FastAPI (Python 3.12):** Wysokowydajny framework internetowy, zapewniający łatwe tworzenie API REST.
* **MongoDB:** NoSQL baza danych, idealna do przechowywania danych aplikacji.
* **MinIO:** Rozwiązanie do obiektowego przechowywania danych, umożliwiające wydajne wgrywanie, przechowywanie i strumieniowanie wideo.
* **Docker:** Platforma do konteneryzacji, zapewniająca spójność i przenośność środowiska.
* **Docker Compose:** Narzędzie do definiowania i zarządzania wieloma kontenerami Docker.

## Uruchamianie aplikacji

1. **Upewnij się, że masz zainstalowane Docker i Docker Compose.**
2. **Sklonuj repozytorium:** `git clone <adres_repozytorium>`
3. **Przejdź do katalogu projektu:** `cd <nazwa_katalogu>`
4. **Uruchom kontenery:** `docker-compose up -d`

## Dostęp do aplikacji

Po uruchomieniu kontenerów, aplikacja będzie dostępna pod adresem: `<adres_IP>:<port>`. Dokładny adres IP i port będą zależeć od konfiguracji.

## Dostęp do bazy danych (Mongo Express)

Aby uzyskać dostęp do interfejsu administracyjnego MongoDB, przejdź pod adres: `<adres_IP>:<port_MongoExpress>`. Domyślnie login i hasło to `admin` / `admin`.

## Konfiguracja

Konfiguracja aplikacji jest zdefiniowana w pliku `.env`. Pamiętaj o utworzeniu tego pliku i wypełnieniu go odpowiednimi wartościami.

## Testy

Testy jednostkowe i integracyjne znajdują się w folderze `tests`. Możesz je uruchomić za pomocą komendy: `pytest`

## Licencja

Ten projekt jest udostępniony na licencji [<nazwa_licencji>](<link_do_licencji>).

## Wkład

Zachęcamy do wkładu w ten projekt! Proszę zapoznać się z [CONTRIBUTING.md](CONTRIBUTING.md) aby dowiedzieć się więcej.