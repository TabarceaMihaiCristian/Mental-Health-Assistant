Documentație proiect: Mental Health Assistant

Pagina de titlu

DOCUMENTAȚIE TEHNICĂ DE PROIECT

Platformă software pentru sprijin în sănătate mintală, interacțiune conversațională asistată și coordonarea programărilor la specialiști

Autor: Mihai Tabarcea  
Perioada documentată: starea curentă a proiectului la data de 8 iunie 2026



Termeni explicați și abrevieri

API - Application Programming Interface; interfață prin care componentele software comunică între ele.
CRUD - Create, Read, Update, Delete; operațiile de bază asupra datelor.
CI - Continuous Integration; execuție automată a validărilor la modificarea codului.
CORS - Cross-Origin Resource Sharing; mecanism de control al accesului între origini diferite.
E2E - End-to-End; teste care validează un flux complet din perspectiva utilizatorului.
ERD - Entity-Relationship Diagram; diagramă a entităților și a relațiilor din baza de date.
HTTP - HyperText Transfer Protocol; protocol utilizat pentru comunicarea web.
JSON - JavaScript Object Notation; format standard de schimb de date.
JWT - JSON Web Token; mecanism de autentificare bazat pe token.
ORM - Object-Relational Mapping; tehnică de mapare a obiectelor aplicației la tabele relaționale.
REST - stil arhitectural pentru servicii web bazate pe resurse și metode HTTP.
UI - User Interface; interfața grafică a aplicației.
UX - User Experience; experiența generală a utilizatorului în interacțiunea cu aplicația.

Introducere

Context și motivație

În contextul actual, aplicațiile software orientate către sănătate mintală trebuie să rezolve simultan mai multe tipuri de probleme: suport conversațional, înregistrarea activității utilizatorului, relaționarea cu specialiști umani, coordonarea programărilor și prezentarea într-o formă clară a informațiilor relevante pentru utilizator. În practică, multe soluții tratează aceste componente separat, ceea ce conduce la experiențe fragmentate, la dublarea datelor și la dificultăți în urmărirea istoricului unui utilizator.

Proiectul Mental Health Assistant a fost construit tocmai pentru a reuni aceste fluxuri într-o singură platformă. Aplicația oferă o bază comună pentru utilizatori, specialiști și administratori și urmărește să reducă fragmentarea dintre zona de conversație, zona de monitorizare a stării emoționale și zona de programări.

Scopul aplicației

Scopul principal al aplicației este furnizarea unei platforme centralizate pentru:

susținerea utilizatorilor prin conversații structurate și suport AI;
monitorizarea evoluției emoționale prin sumarizări și rapoarte;
direcționarea utilizatorilor către specialiști atunci când este necesar;
gestionarea programărilor și a disponibilității într-un mod coerent;
administrarea controlată a conturilor de specialist și a activității operaționale.

Starea actuală a proiectului

În starea actuală, proiectul nu mai reprezintă doar o bază de backend cu un frontend parțial. Aplicația conține fluxuri funcționale pentru toate cele trei roluri importante din sistem:

utilizator;
specialist;
administrator.

Backend-ul este structurat, tipizat și validat extensiv, iar frontend-ul este conectat la fluxurile reale de produs și include interfețe dedicate pentru dashboard, chat, programări, notificări, rapoarte și administrare.

Documentația de față reflectă exclusiv starea curentă a aplicației. Partea de deployment nu este inclusă, deoarece proiectul nu mai urmărește documentarea livrării într-un mediu de producție în această etapă.

Obiectivele aplicației

Aplicația urmărește atingerea următoarelor obiective tehnice și funcționale:

furnizarea unui API securizat și clar delimitat pe roluri;
modelarea explicită a fluxurilor de programare, anulare și reprogramare;
integrarea unui asistent conversațional cu analiză emoțională;
generarea de notificări și rapoarte relevante pentru activitatea utilizatorului;
administrarea specialiștilor și a calendarului acestora;
menținerea unei baze solide de validare automată, testare și cur--are pentru datele de test.

Analiza cerințelor

Descriere funcțională generală

Mental Health Assistant este o aplicație full-stack care centralizează mai multe procese specifice unei platforme de sprijin în sănătate mintală:

gestionarea autentificării și a sesiunii;
comunicarea cu un asistent AI;
analizarea mesajelor din perspectivă emoțională și de risc;
interacțiunea cu directorul de specialiști;
gestionarea programărilor din perspectiva utilizatorului și a specialistului;
notificarea și raportarea activității relevante.

Din punct de vedere operațional, aplicația permite unui utilizator să își creeze cont, să converseze cu asistentul, să primească sumarizări și rapoarte pe baza mesajelor sale, să consulte specialiști și să ceară programări. Specialistul poate gestiona programările și disponibilitatea sa, iar administratorul poate administra specialiștii și urmări programările la nivel de supraveghere.

Identificarea utilizatorilor și a rolurilor

Sistemul lucrează cu trei roluri distincte:

Utilizator

Utilizatorul reprezintă persoana care caută suport și care poate:

să își creeze cont prin interfața publică;
să utilizeze chat-ul cu asistentul;
să consulte specialiștii activi;
să facă, anuleze și replanifice programări;
să consulte rapoarte, sumarizări și notificări;
să își administreze setările contului.

Specialist

Specialistul reprezintă profesionistul disponibil în platformă și poate:

să consulte dashboard-ul propriu;
să vizualizeze programările asociate;
să confirme, respingă, reprogrameze sau finalizeze programări;
să își configureze disponibilitatea;
să adauge pauze recurente și intervale de indisponibilitate;
să consulte notificările și să își administreze sesiunea.

Administrator

Administratorul are rol de supraveghere și configurare operațională și poate:

să consulte dashboard-ul administrativ;
să creeze și să gestioneze specialiști;
să activeze sau să dezactiveze profiluri de specialist;
să urmărească și să filtreze programările;
să acceseze notificările comune din platformă.

Observație privind înregistrarea publică

În starea actuală a aplicației:

înregistrarea publică este disponibilă doar pentru utilizatori;
conturile de specialist nu se creează public;
specialiștii sunt creați doar de administratori.

Această regulă este importantă și trebuie reținută atât din punct de vedere funcțional, cât și din punct de vedere al interpretării interfeței.

Cerințe funcționale

1. Autentificare și conturi

Sunt implementate:

înregistrare publică pentru utilizatori;
autentificare locală pe bază de email și parolă;
identificarea utilizatorului curent;
restaurarea sesiunii după refresh;
logout și protecția rutelor;
resetare parolă.

2. Chat și suport conversațional

Aplicația permite:

crearea unei sesiuni noi de chat;
reutilizarea sesiunii deschise;
trimiterea de mesaje către asistent;
închiderea conversațiilor;
arhivarea sesiunilor;
păstrarea istoricului conversațiilor.

3. Analiză emoțională și risc

Pe baza mesajelor utilizatorului, sistemul generează:

analize individuale de mood;
evaluări de intensitate și risc;
sumarizări zilnice ale stării dominante;
evidențierea trigger-elor frecvente;
evenimente de risc atunci când mesajele indică situații sensibile.

4. Programări pentru utilizatori

Din perspectiva utilizatorului sunt implementate:

consultarea directorului de specialiști;
vizualizarea profilului și a sloturilor disponibile;
cererea unei programări;
listarea programărilor proprii;
anularea unei programări;
reprogramarea unei programări;
vizualizarea stărilor relevante pentru fiecare programare.

5. Funcționalități pentru specialiști

Din perspectiva specialistului sunt implementate:

dashboard dedicat;
listarea programărilor asociate;
confirmarea unei programări;
respingerea unei cereri;
reprogramarea unei programări;
marcarea unei programări ca finalizată;
gestionarea disponibilității recurente;
gestionarea pauzelor recurente;
gestionarea intervalelor de indisponibilitate;
consultarea calendarului de lucru.

6. Funcționalități administrative

Din perspectiva administratorului sunt implementate:

dashboard administrativ;
creare conturi și profiluri de specialist;
activare și dezactivare specialist;
actualizare date de profil;
filtrare programări pe stări și intervale;
consultarea programărilor din perspectiva de supraveghere.

7. Notificări și rapoarte

Sunt implementate:

listarea notificărilor;
contor pentru notificările necitite;
marcare citit și necitit;
operații bulk pe notificări;
generarea și afișarea rapoartelor săptămânale și lunare;
listarea sumarizărilor zilnice;
sincronizarea rapoartelor cu datele curente disponibile.

Cerințe non-funcționale

În starea actuală, aplicația acoperă următoarele cerințe non-funcționale:

securitate: autentificare JWT și protecția rutelor sensibile;
modularitate: separare clară între modele, scheme, servicii, straturile de acces la date și routere;
testabilitate: backend testat unitar și prin integrare, frontend validat prin lint -i build și prin fluxuri E2E;
consistență: verificare de tipuri și linting pe ambele componente;
portabilitate locală: rulare locală și în containere Docker pentru dezvoltare și testare;
mentenabilitate: flux de integrare continu- și set de date ini-ial determinist pentru date locale;
igienă a datelor de test: cur--are automat al datelor Playwright după rularea cu succes a testelor E2E.

Specificații tehnice

Backend

Python 3.13
FastAPI
SQLAlchemy
Alembic
PostgreSQL
APScheduler
OpenAI SDK
passlib + bcrypt
python-jose
pydantic-settings
psycopg

Frontend

React 19
TypeScript
Vite
React Router
Lucide React
ESLint

Testare și calitate

Pytest
Ruff
Pyright
ESLint
Playwright

Suport operațional local

Docker
Docker Compose
GitHub Actions

Proiectarea aplicației

Arhitectura generală a aplicației

Aplicația urmează o arhitectură de tip client-server, cu separare clară între componenta de prezentare și componenta de business logic.

Structura generală este împărțită în două componente principale:

frontend, responsabil pentru interfața utilizatorului și navigația pe roluri;
backend, responsabil pentru logica de business, persistență și expunerea API-ului.

Arhitectura backend-ului

Backend-ul este organizat în jurul FastAPI și include următoarele zone principale:

app/api/v1/routers pentru endpoint-uri REST;
app/services pentru logica de business;
app/repositories pentru accesul la date;
app/models pentru modelele ORM;
app/schemas pentru validare și serializare;
app/core pentru configurare, securitate și autorizare;
app/jobs pentru procese programate;
app/scripts pentru seed și cur--are;
app/utils pentru logging și validări auxiliare.

Această structură permite o evoluție controlată a aplicației și reduce dependențele directe între componente.

Arhitectura frontend-ului

Frontend-ul este organizat modular și urmează aceeași separare a responsabilităților:

src/app pentru infrastructura aplicației și furnizorul de autentificare;
src/features pentru funcționalități verticale;
src/components pentru interfa-- reutilizabil-;
src/routes pentru definirea și protejarea rutelor;
src/lib pentru clientul API, configurație și utilitare;
src/types pentru tipurile TypeScript partajate;
src/styles pentru temă și stiluri globale.

În forma actuală, frontend-ul include pagini și fluxuri pentru:

autentificare și resetare parolă;
landing page publică;
dashboard utilizator;
chat AI;
director de specialiști și pagină de detaliu;
programări utilizator;
rapoarte;
notificări;
setări cont;
dashboard specialist;
programări specialist;
calendar și disponibilitate specialist;
dashboard administrator;
administrare specialiști;
supraveghere programări admin.

Persistență și model de date

Baza de date este relațională și folosește PostgreSQL. Modelele acoperă domeniile principale ale aplicației:

utilizatori și identități de autentificare;
sesiuni și mesaje de chat;
analize emoționale și evenimente de risc;
specialiști, recenzii și reguli de disponibilitate;
programări;
notificări;
rapoarte și sumarizări zilnice.

Implementarea backend-ului

Configurare și inițializare

Configurația backend-ului este centralizată și include, între altele:

conexiunea la baza de date;
cheia secretă pentru token-uri;
cheia OpenAI;
setările scheduler-ului;
regulile de booking, anulare și reprogramare;
configurația CORS.

Această abordare permite separarea clară între rularea locală, testare și alte contexte operaționale.

Autentificare și autorizare

Autentificarea este implementată local, pe bază de email și parolă. Autorizarea se face pe roluri:

user
specialist
admin

Fluxul actual include:

înregistrarea conturilor de utilizator;
autentificarea și emiterea token-ului;
rezolvarea utilizatorului curent;
restricționarea explicită a rutelor pentru specialist și administrator.

Domenii funcționale implementate

Chat și interacțiune cu asistentul

Backend-ul permite:

creare sesiuni de chat;
listare sesiuni existente;
recuperarea sesiunii deschise;
adăugare de interacțiuni utilizator-asistent;
închiderea și arhivarea sesiunilor.

Analiză emoțională și risc

Serviciile dedicate se ocupă de:

analiza mesajelor utilizatorului;
generarea rezultatelor de mood;
calcularea riscului;
salvarea sumarizărilor zilnice;
generarea evenimentelor de risc.

Specialiști și disponibilitate

Sistemul oferă:

listare specialiști activi;
profiluri publice detaliate;
recenzii și rating;
reguli de disponibilitate recurente;
pauze recurente;
intervale de time off;
calcularea sloturilor disponibile.

Programări

Fluxul de programări acoperă atât perspectiva utilizatorului, cât și pe cea a specialistului. Sunt implementate reguli legate de:

booking;
confirmare;
respingere;
anulare;
reprogramare;
finalizare;
reminder-e automate;
sugestii de programări în situații critice.

Notificări

Sunt disponibile endpoint-uri pentru:

listare;
număr de notificări necitite;
marcare citit și necitit;
operații bulk;
ștergere individuală și filtrată.

Rapoarte și sumarizări

Backend-ul generează:

sumarizări zilnice de stare;
rapoarte săptămânale;
rapoarte lunare;
rezumate sintetice bazate pe datele emoționale agregate.

Implementarea frontend-ului

Fluxuri publice și autentificare

În interfața publică sunt implementate:

pagina principală;
login;
înregistrare utilizator;
resetare parolă;
protecție pentru rutele guest-only;
restaurarea sesiunii pe refresh.

Înregistrarea publică este limitată intenționat la utilizatorii care caută suport. Conturile de specialist nu se creează prin acest flux.

Zona utilizatorului

Pentru utilizatorul autentificat sunt implementate:

dashboard cu indicatori rapizi;
navigație către chat, specialiști, programări, rapoarte, notificări și setări;
chat AI cu sesiuni multiple;
listarea specialiștilor și rezervarea unei programări;
listarea și gestionarea programărilor proprii;
rapoarte și sumarizări zilnice;
pagina de notificări;
pagina de setări și schimbarea parolei.

Zona specialistului

Pentru specialist sunt implementate:

dashboard dedicat;
listarea programărilor asociate;
confirmare, respingere, reprogramare și finalizare programări;
gestionarea disponibilității;
gestionarea pauzelor și a intervalelor de indisponibilitate;
acces la notificări și setări.

Zona administratorului

Pentru administrator sunt implementate:

dashboard administrativ;
administrarea specialiștilor;
creare și activare/dezactivare specialist;
consultarea și filtrarea programărilor;
acces la notificări și setări.

Seed demo și date de test

Proiectul include un set de date ini-ial determinist pentru rulare locală și demonstrație. Acesta creează:

conturi demo pentru administrator, specialist și utilizator;
specialiști activi și un specialist inactiv;
recenzii și date de rating;
disponibilitate realistă;
programări demonstrative;
suficiente date pentru a popula dashboard-urile.

Pe lângă seed, proiectul include:

creare controlată de date E2E pentru Playwright;
cur--are automat al datelor Playwright după rularea cu succes a suitei E2E;
comandă manuală de cur--are pentru eliminarea datelor de test deja existente.

Testare, calitate și validare

Backend

Backend-ul este validat prin:

Ruff
Pyright
Pytest

În starea curentă, suita backend include:

149 de teste unitare și de integrare care trec cu succes.

Frontend

Frontend-ul este validat prin:

npm run lint
npm run build

Testare end-to-end

Fluxurile reale multi-rol sunt validate cu Playwright. În starea curentă, suita E2E include:

19 teste care validează fluxuri complete pentru utilizator, specialist și administrator.

Acestea acoperă, între altele:

autentificarea pe roluri;
booking, confirmare și filtrare programări;
chat și rapoarte;
notificări;
administrarea specialiștilor;
impactul disponibilității asupra sloturilor publice.

Integrare continuă

Proiectul include pipeline de validare prin GitHub Actions. Validările urmăresc consistența codului și stabilitatea principalelor fluxuri.

Limitări actuale

Limitările reale ale aplicației în starea actuală sunt:

înregistrarea publică este disponibilă doar pentru utilizatori, nu pentru specialiști;
nu există un flux public de aplicare și aprobare pentru specialiști;
validarea completă a backend-ului pe anumite medii Windows poate necesita Docker din cauza particularităților psycopg;
funcțiile de analiză și răspuns conversațional depind de configurarea corectă a cheii OpenAI;

Concluzii

În forma actuală, Mental Health Assistant este o aplicație full-stack coerentă, cu fluxuri implementate pentru toate cele trei roluri importante ale sistemului:

utilizator;
specialist;
administrator.

Punctele forte ale stadiului curent sunt:

backend bine structurat și bine testat;
frontend conectat la fluxurile reale de produs;
acoperire E2E pentru scenarii critice;
seed și cur--are pentru date locale;
separare clară între zonele funcționale și roluri.

Valoarea practică a aplicației, în starea actuală, constă în faptul că aceasta poate fi demonstrată și validată cap-coadă local, fără a depinde de dezvoltări majore suplimentare pentru fluxurile principale deja implementate.

Bibliografie

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
