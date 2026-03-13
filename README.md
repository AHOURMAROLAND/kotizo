# Kotizo

Application mobile de cotisations collectives et Quick Pay pour le Togo.

## Stack

| Couche | Technologie |
|---|---|
| Mobile | React Native + Expo |
| Backend | Django 5.0 + DRF |
| Auth | JWT (simplejwt) |
| Async | Celery + Redis |
| Base de donnees | PostgreSQL (prod) / SQLite (dev) |
| Paiements | PayDunya (Mixx by Yas + Moov Money) |
| Push | Firebase Cloud Messaging |
| Images | Cloudinary |
| Conteneurs | Docker + Docker Compose |
| Admin web | React.js + Tailwind CSS |
| Agent IA | Google Gemini 2.0 Flash |

## Structure

    kotizo/
    kotizo-backend/        Django API
        config/            Settings, urls, wsgi
        users/             Auth, profils, niveaux
        cotisations/       Cotisations, participations
        paiements/         PayDunya PayIn/PayOut, webhooks
        quickpay/          Quick Pay
        notifications/     FCM, emails
        agent_ia/          Gemini, tickets support
        admin_panel/       API dashboard admin
        core/              Logger, middleware, permissions

    kotizo-mobile/         React Native Expo
        src/
            screens/       Ecrans
            components/    Composants reutilisables
            navigation/    React Navigation
            hooks/         useNetworkStatus, useAuth...
            services/      Appels API axios
            store/         Etat global
            utils/         Helpers

    kotizo-admin/          React Web dashboard
        src/
            pages/         14 sections admin
            components/    Composants UI
            services/      API calls
            hooks/         Hooks custom

## URLs

    kotizo.app             App mobile
    admin.kotizo.app       Dashboard admin
    api.kotizo.app         Backend Django

## Niveaux utilisateurs

| Niveau | Condition | Limite jour |
|---|---|---|
| Basique | Email verifie | 5 cotisations |
| Verifie | Liveness + CNI | 20 cotisations |
| Business | Approbation admin | Illimite |

## Paiements

    PayIn  : PAR Checkout Invoice - 2.5% frais PayDunya
    PayOut : PUSH Disburse - 2% frais PayDunya
    Frais Kotizo : 250 / 500 / 1000 FCFA selon montant
    Webhooks IPN verifie par hash SHA-512

## Variables d environnement

    SECRET_KEY=
    DEBUG=False
    DATABASE_URL=
    REDIS_URL=
    PAYDUNYA_MASTER_KEY=
    PAYDUNYA_PRIVATE_KEY=
    PAYDUNYA_TOKEN=
    CLOUDINARY_URL=
    GEMINI_API_KEY=
    FCM_SERVER_KEY=
    SENTRY_DSN=

## Lancer en dev

    Backend
    cd kotizo-backend
    venv\Scripts\activate
    python manage.py runserver

    Celery
    celery -A config worker -l info
    celery -A config beat -l info

    Mobile
    cd kotizo-mobile
    npx expo start

    Admin
    cd kotizo-admin
    npm start
