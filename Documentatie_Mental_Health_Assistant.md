# Documenta?ie proiect: Mental Health Assistant

## Pagina de titlu

**DOCUMENTA?IE TEHNICA DE PROIECT**

**Platforma software pentru asisten?a în sanatate mintala, interac?iune conversa?ionala ?i programari la speciali?ti**

Autor: Mihai Tabarcea  
Perioada documentata: starea curenta a proiectului la data de 4 mai 2026

---

## Introducere

Proiectul **Mental Health Assistant** este o aplica?ie software orientata catre sprijinirea utilizatorilor în gestionarea interac?iunilor legate de sanatatea mintala, oferind atât func?ionalita?i de conversa?ie asistata de inteligen?a artificiala, cât ?i mecanisme de programare la speciali?ti, generare de rapoarte, notificari ?i administrare a disponibilita?ii speciali?tilor.

Solu?ia este dezvoltata pe o arhitectura separata **backend + frontend**, în care componenta back-end este deja matura din punct de vedere func?ional ?i opera?ional, iar componenta front-end se afla într-o etapa de construc?ie incrementala, având deja implementate autentificarea ?i primul flux real de produs: navigarea în directorul de speciali?ti.

Scopul principal al aplica?iei este de a furniza o baza tehnica scalabila pentru urmatoarele scenarii:

- autentificarea ?i autorizarea utilizatorilor pe roluri;
- crearea ?i gestionarea sesiunilor de chat cu asistentul;
- analiza starii emo?ionale ?i detectarea situa?iilor de risc;
- recomandarea de programari catre speciali?ti în situa?ii critice;
- gestionarea disponibilita?ii speciali?tilor ?i a programarilor;
- notificarea utilizatorilor ?i generarea de rapoarte periodice.

Din punct de vedere al stadiului curent, proiectul dispune de un back-end bine testat, cu integrare continua activa, configurare de deployment local ?i production-style, precum ?i de un front-end modern în React, conectat deja la fluxurile de autentificare ?i la directorul de speciali?ti.

## Analiza cerin?elor

### Obiectivele aplica?iei

Aplica?ia urmare?te construirea unei platforme centralizate care sa permita atât suport conversa?ional, cât ?i gestionarea legaturii dintre utilizatori ?i speciali?ti. În forma actuala, obiectivele tehnice ?i func?ionale sunt:

- furnizarea unui API securizat pentru utilizatori, speciali?ti ?i administratori;
- modelarea unui flux de programari cu reguli de business clare;
- integrarea unui asistent conversa?ional ?i a analizelor de tip mood/risk;
- generarea de notificari ?i rapoarte pe baza datelor utilizatorului;
- posibilitatea de administrare a speciali?tilor ?i a programului acestora;
- men?inerea unei baze solide de testare, tipare ?i deployment.

### Cerin?e func?ionale

Pe baza implementarii curente, cerin?ele func?ionale deja acoperite de back-end sunt urmatoarele:

1. **Autentificare ?i profil curent**
- înregistrare utilizator local;
- autentificare locala;
- identificarea utilizatorului autentificat prin endpoint-ul `/auth/me`.

2. **Gestionarea chat-ului**
- creare sesiuni de chat;
- listare sesiuni existente;
- recuperarea sesiunii deschise;
- adaugare mesaje într-o sesiune;
- creare de interac?iuni complete utilizator-asistent.

3. **Programari pentru utilizatori**
- creare programare;
- listare programari proprii;
- vizualizare programare individuala;
- anulare programare;
- reprogramare programare;
- ob?inere sugestii de programari pentru situa?ii critice.

4. **Director ?i activita?i speciali?ti**
- listare speciali?ti activi;
- vizualizare profil specialist;
- consultarea disponibilita?ii pe intervale de timp;
- adaugare ?i actualizare recenzii;
- gestionarea disponibilita?ii recurente;
- gestionarea pauzelor recurente;
- gestionarea intervalelor de time-off;
- vizualizarea calendarului specialistului.

5. **Programari pe partea specialistului**
- listarea programarilor alocate;
- creare programare în numele utilizatorului;
- confirmare, respingere, reprogramare ?i completare programari.

6. **Administrare**
- onboarding ?i administrare speciali?ti;
- modificarea profilului specialistului;
- modificarea statusului specialistului;
- listarea ?i consultarea programarilor din perspectiva administrativa.

7. **Notificari ?i rapoarte**
- listare notificari;
- numar notificari necitite;
- marcare notificari ca citite/necitite;
- opera?ii bulk pe notificari;
- generarea ?i consultarea rapoartelor periodice;
- listarea sumarizarilor zilnice de stare emo?ionala.

### Cerin?e non-func?ionale

Cerin?ele non-func?ionale deja adresate în proiect sunt:

- **securitate**: autentificare pe baza de JWT ?i protec?ia rutelor sensibile;
- **modularitate**: separare clara pe layere pentru modele, scheme, servicii, repository-uri ?i routere;
- **testabilitate**: suita extinsa de teste unitare ?i de integrare;
- **tipare ?i consisten?a**: utilizarea validarii Pydantic, type checking cu Pyright ?i linting cu Ruff/ESLint;
- **portabilitate**: rulare locala ?i în containere Docker;
- **observabilitate minima**: endpoint-uri de health pentru API, baza de date ?i scheduler;
- **mentenabilitate**: flux CI cu validari automate.

### Tehnologii utilizate

#### Back-end
- Python 3.13
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- APScheduler
- OpenAI SDK
- passlib + bcrypt
- python-jose
- pydantic-settings
- psycopg

#### Front-end
- React 19
- TypeScript
- Vite
- React Router
- ESLint

#### Testare ?i calitate
- Pytest
- Ruff
- Pyright
- ESLint

#### Deployment ?i DevOps
- Docker
- Docker Compose
- GitHub Actions

## Arhitectura generala a aplica?iei

Aplica?ia este construita pe o arhitectura de tip client-server, cu separare clara între componenta de prezentare ?i componenta de business logic.

### Arhitectura back-end-ului

Componenta back-end este organizata în jurul framework-ului FastAPI ?i include urmatoarele zone principale:

- `app/api/v1/routers` pentru expunerea endpoint-urilor REST;
- `app/services` pentru logica aplica?iei;
- `app/repositories` pentru accesul la date;
- `app/models` pentru modelarea rela?ionala a entita?ilor;
- `app/schemas` pentru validarea ?i serializarea payload-urilor;
- `app/core` pentru configurare, securitate ?i autorizare;
- `app/jobs` pentru scheduler ?i joburi periodice;
- `app/utils` pentru logging ?i validari auxiliare.

Aceasta organizare reduce cuplajul dintre componente ?i permite evolu?ia independenta a logicii de domeniu, a modelelor ?i a expunerii API.

### Arhitectura front-end-ului

Front-end-ul este organizat modular ?i urmare?te aceea?i separare a responsabilita?ilor:

- `src/app` pentru infrastructura aplica?iei ?i contextul de autentificare;
- `src/features` pentru func?ionalita?i verticale, cum ar fi autentificarea ?i speciali?tii;
- `src/routes` pentru protec?ia ?i definirea rutelor;
- `src/lib` pentru clientul API, configura?ie ?i persistarea sesiunii;
- `src/types` pentru tipurile TypeScript partajate;
- `src/styles` pentru stilizarea globala.

În starea curenta, front-end-ul implementeaza:

- autentificare ?i înregistrare;
- restaurarea sesiunii prin `/auth/me`;
- protec?ia rutelor pentru utilizatorii autentifica?i;
- redirec?ionare pentru rutele guest-only;
- listarea directorului de speciali?ti;
- pagina de detaliu pentru specialist.

### Persisten?a ?i date

Baza de date rela?ionala este PostgreSQL, accesata prin SQLAlchemy ?i gestionata prin migra?ii Alembic. Modelele existente acopera domeniile principale ale aplica?iei:

- utilizatori ?i identita?i de autentificare;
- sesiuni ?i mesaje de chat;
- analize de stare emo?ionala ?i evenimente de risc;
- speciali?ti, recenzii ?i reguli de disponibilitate;
- programari;
- notificari;
- rapoarte ?i sumarizari zilnice.

### Execu?ie ?i deployment

Proiectul include doua moduri de rulare cu Docker Compose:

- **mod de dezvoltare**: cu bind mount ?i `uvicorn --reload`;
- **mod production-style**: fara bind mount, fara reload, cu entrypoint care a?teapta baza de date ?i ruleaza migra?iile.

Containerul back-end utilizeaza un entrypoint dedicat care:

1. a?teapta disponibilitatea bazei de date;
2. ruleaza `alembic upgrade head` când `AUTO_MIGRATE=true`;
3. porne?te serverul aplica?iei.

Aplica?ia expune endpoint-uri de health pentru:

- procesul API;
- conectivitatea la baza de date;
- starea scheduler-ului.

## Implementarea back-end-ului

### Configurare ?i ini?ializare

Aplica?ia FastAPI este ini?ializata printr-un entrypoint central, iar configura?ia este administrata dintr-un modul dedicat. Printre valorile importante de configurare se afla:

- `DATABASE_URL`;
- `SECRET_KEY`;
- `OPENAI_API_KEY`;
- setarile pentru scheduler;
- regulile de booking ?i reschedule;
- configura?ia CORS.

Acest model centralizat face posibila separarea clara între medii de dezvoltare, test ?i produc?ie.

### Autentificare ?i autorizare

Autentificarea este implementata local, pe baza de email ?i parola, iar autorizarea se bazeaza pe roluri. Fluxul actual cuprinde:

- înregistrarea utilizatorilor;
- autentificarea ?i emiterea token-ului;
- rezolvarea utilizatorului curent;
- protec?ia rutelor prin dependen?e FastAPI;
- verificarea explicita a utilizatorilor cu rol de specialist pentru rutele specifice.

Aceasta abordare permite pastrarea unei interfe?e API coerente ?i a unei logici explicite de control al accesului.

### Domeniile func?ionale implementate

Back-end-ul acopera mai multe subdomenii deja opera?ionale:

#### 1. Chat ?i analiza contextuala
Sistemul permite crearea de sesiuni de chat ?i transmiterea mesajelor. Acest strat reprezinta baza pentru integrarea raspunsurilor generate de modelul OpenAI ?i pentru analiza starii emo?ionale a utilizatorului.

#### 2. Analiza de mood ?i risc
Aplica?ia include servicii pentru analiza de mood ?i pentru generarea de evenimente de risc. Acestea sunt folosite drept baza pentru identificarea situa?iilor critice ?i pentru declan?area fluxurilor de recomandare a programarilor.

#### 3. Speciali?ti ?i disponibilitate
Back-end-ul ofera un director de speciali?ti, un model de recenzii ?i o infrastructura completa pentru gestionarea disponibilita?ii recurente, a pauzelor ?i a intervalelor de indisponibilitate. De asemenea, pot fi calculate sloturile disponibile într-o fereastra de timp.

#### 4. Programari
Fluxul de programari include atât perspectiva utilizatorului final, cât ?i perspectiva specialistului. Sunt implementate reguli privind notificarea, confirmarea, respingerea ?i reprogramarea programarilor, precum ?i generarea sugestiilor pentru cazuri critice.

#### 5. Notificari
Aplica?ia ofera endpoint-uri pentru listarea ?i administrarea notificarilor, inclusiv opera?ii bulk ?i contorizarea elementelor necitite.

#### 6. Rapoarte
Sistemul permite generarea ?i consultarea rapoartelor pe perioade ?i a sumarizarilor zilnice. Aceasta componenta pregate?te terenul pentru analize mai bogate asupra activita?ii ?i a evolu?iei starii utilizatorului.

### Testare, calitate ?i validare

Back-end-ul se afla într-o stare buna de maturitate din perspectiva validarii automate. La momentul actual:

- suita completa de teste back-end ruleaza cu succes;
- exista aproximativ **140 de teste** unitare ?i de integrare;
- acoperirea totala raportata a fost de aproximativ **94%**;
- verificarile automate includ **Ruff**, **Pyright** ?i **Pytest**;
- pipeline-ul de CI ruleaza prin GitHub Actions.

Aceasta baza ofera un nivel ridicat de încredere în stabilitatea componentelor deja implementate.

## Implementarea front-end-ului

### Stack ?i structura

Front-end-ul este dezvoltat cu React, TypeScript ?i Vite. Alegerea acestui stack ofera:

- pornire rapida ?i feedback scurt în dezvoltare;
- model componentizat ?i extensibil;
- tipare moderne pentru validarea statica a codului;
- integrare simpla cu API-ul REST al back-end-ului.

### Autentificare ?i gestionarea sesiunii

Primul flux complet implementat în front-end este fluxul de autentificare. Acesta include:

- pagina de login;
- pagina de register;
- context de autentificare ?i hooks dedicate;
- persistarea token-ului în `localStorage`;
- restaurarea sesiunii pe refresh prin endpoint-ul `/auth/me`;
- rute protejate ?i rute disponibile doar pentru utilizatori neautentifica?i.

Fluxul a fost verificat manual ?i func?ioneaza corect pentru:

- înregistrare;
- autentificare;
- logout;
- men?inerea sesiunii dupa refresh;
- redirec?ionare corecta între zone publice ?i protejate.

### Directorul de speciali?ti

Al doilea flux implementat în front-end este directorul de speciali?ti. În starea actuala exista:

- pagina de listare a speciali?tilor activi;
- pagina de detaliu pentru un specialist;
- integrare cu endpoint-urile protejate ale back-end-ului;
- gestionare a starilor de loading, eroare ?i lista goala.

Acest flux este primul exemplu de extindere a front-end-ului dincolo de autentificare ?i reprezinta baza pentru viitoarea implementare a programarilor din interfa?a.

### Validare front-end

Front-end-ul dispune în prezent de:

- validare prin `npm run lint`;
- validare de build prin `npm run build`;
- verificare manuala a fluxurilor de autentificare ?i specialist directory.

Nu exista înca, în starea actuala, o suita de teste automate E2E sau component-level pentru front-end. Aceasta reprezinta una dintre direc?iile naturale de extindere, alaturi de integrarea Playwright.

### Limite ?i stadiul actual al interfe?ei

Documenta?ia trebuie sa reflecte starea reala a proiectului. În acest moment:

- back-end-ul este avansat ?i con?ine majoritatea fluxurilor de domeniu;
- front-end-ul este într-o etapa intermediara de dezvoltare;
- fluxurile de chat, notificari, rapoarte ?i programari nu sunt înca expuse integral în interfa?a;
- directorul de speciali?ti este implementat, dar fluxul de booking din UI urmeaza sa fie realizat.

## Concluzii ?i direc?ii viitoare

Proiectul **Mental Health Assistant** se afla într-o etapa solida din perspectiva infrastructurii, a modelului de date ?i a componentelor back-end. Arhitectura este coerenta, stratificata ?i sus?inuta de testare automata ?i deployment local bine definit.

Cele mai importante rezultate atinse pâna în prezent sunt:

- definirea unei arhitecturi back-end robuste cu FastAPI, SQLAlchemy ?i PostgreSQL;
- implementarea unui domeniu func?ional bogat: autentificare, chat, speciali?ti, programari, notificari, rapoarte ?i joburi programate;
- configurarea unui pipeline CI cu linting, type checking ?i testare automata;
- pregatirea unei baze de deployment cu mod development ?i mod production-style;
- construirea unui front-end modern ?i conectarea lui la fluxurile critice ini?iale.

Direc?iile viitoare de dezvoltare sunt clare:

1. implementarea completa în front-end a fluxului de programari;
2. conectarea interfe?ei la fluxurile de chat ?i asistent AI;
3. expunerea în UI a notificarilor ?i rapoartelor;
4. introducerea testarii E2E cu Playwright;
5. consolidarea documenta?iei opera?ionale ?i a politicilor de deployment;
6. eventuala întarire a strategiei de securitate prin mutarea sesiunii catre cookie-uri `HttpOnly`, daca produsul va necesita acest lucru.

În concluzie, proiectul are deja o funda?ie tehnica matura ?i extensibila. Valoarea imediata a stadiului curent consta în faptul ca infrastructura critica a fost deja stabilizata, iar dezvoltarea ulterioara poate continua concentrat pe fluxurile de produs din interfa?a.

## Bibliografie

[1] FastAPI Documentation. https://fastapi.tiangolo.com/  
[2] SQLAlchemy Documentation. https://docs.sqlalchemy.org/  
[3] Alembic Documentation. https://alembic.sqlalchemy.org/  
[4] PostgreSQL Documentation. https://www.postgresql.org/docs/  
[5] React Documentation. https://react.dev/  
[6] Vite Documentation. https://vite.dev/  
[7] OpenAI Platform Documentation. https://platform.openai.com/docs/  
[8] Pytest Documentation. https://docs.pytest.org/  
[9] Ruff Documentation. https://docs.astral.sh/ruff/  
[10] Pyright Documentation. https://microsoft.github.io/pyright/  
[11] Docker Documentation. https://docs.docker.com/  
[12] GitHub Actions Documentation. https://docs.github.com/actions  
[13] OWASP Top 10. https://owasp.org/www-project-top-ten/

