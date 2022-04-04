# Marketplace 
<h5> Calcan Elena-Claudia <br/>
331CA</h5>  

### Synopsis 
--------------------

- Programul reprezinta simularea unui marketplace care se bazeaza pe problema Producer-Consumer. 

### Flow-ul programului
------------------------------------------------ 

 * Implementarea marketplace-ului este realizata in fisierele marketplace.py, producer.py si consumer.py 
  
  
 #### 1. Marketplace
 -----------------------------
 * reprezinta elementul intermediar intre producatori si consumatori
 * pentru a stoca producatorii cu produsele sale s-a folosit un dictionar care face o mapare
 intre id-ul producatorului si o lista de produse disponibile 
 * cosurile consumatorilor cu produsele dorite sunt salvate intr-un fictionar care face mapare
 intre id-ul cosului si o list de tupluri format din produsul dorit si id-ul producatorului 
 * un producator adauga in lista sa un numar fix de produse, acestea fiind disponibile consumatorilor 
 * la adaugarea unui produs in cosul de cumparaturi, se cauta primul producator ce are disponibil produsul
 dorit, se construieste tuplul si adaugat in lista de produse a cosului respectiv, produsul achizitionat
 urmand sa fie sters din lista producatorului, marcand astfel indisponibilitatea lui 
 * cand un consumator doreste sa elimine un produs din cos, se cauta primul tuplu din lista ce contine
 produsul, se sterge si se adauga inapoi in lista producatorului respectiv, devenind astfel disponibil
 pentru ceilalti clienti 
 * pentru a delimita zonele critice din cod, s-au folosit cinci lock-uri, cate unul pentru fiecare operatie 
 ce are loc in marketplace 
 
 #### 2. Producer
 ----------------------------
 * implementeaza logica producatorului
 * insereaza o anumita cantitate pentru fiecare produs in buffer 
 * cand buffer-ul sau devine plin, producatorul nu mai poate publica produse, urmand sa se blocheze 
 
 #### 3. Consumer 
 ------------------------------- 
 * implementeaza logica consumatorului 
 * consumatorul poate sa adauge sau sa stearga o  anumita cantitate de produse in buffer 
 * cand nu poate efectua una din aceste doua operatii, consumatorul se blocheaza 
 
 ### Unittesting 
 ----------------------------------
 * clasa de testare este implementata in fisierul marketplace.py 
 * in functia de setUp() s-a creat o instanta a marketplace-ului si s-au initializat 
 doua variabile cu care s-a testat comportamentul functiilor din clasa Marketplace 
 
 ### Logging 
 ---------------------------------- 
 * s-a folosit nivelul info() pentru a inregistra informatiile de intrare si rezultatul fiecarei 
 functii din Marketplace
 
 ### Bibliografie 
 ---------------------------
 * https://ocw.cs.pub.ro/courses/asc/laboratoare/01
 * https://ocw.cs.pub.ro/courses/asc/laboratoare/02
 * https://ocw.cs.pub.ro/courses/apd/laboratoare/05 
 * https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler 
 * https://www.youtube.com/watch?v=6tNS--WetLI&t=1967s&ab_channel=CoreySchafer 
 * https://www.youtube.com/watch?v=-ARI4Cz-awo&t=777s&ab_channel=CoreySchafer 
 * https://docs.python.org/3/library/unittest.html#organizing-test-code
 
 ### Git 
 ------------------------- 
 * https://github.com/elenacalcan26/Marketplace.git
