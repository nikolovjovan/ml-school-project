# Kreiranje baze

DROP DATABASE IF EXISTS nekretnine;

CREATE DATABASE nekretnine;

USE nekretnine;

# Kreiranje tipa nekretnine

DROP TABLE IF EXISTS tip_nekretnine;

CREATE TABLE tip_nekretnine (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(20)
);

INSERT INTO tip_nekretnine (naziv) VALUES
('stan'),
('kuca');

-- SELECT * FROM tip_nekretnine;

# Kreiranje tabele za drzavu, grad i deo grada

DROP TABLE IF EXISTS drzava;

CREATE TABLE drzava (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100)
);

DROP TABLE IF EXISTS grad;

CREATE TABLE grad (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100)
);

DROP TABLE IF EXISTS deo_grada;

CREATE TABLE deo_grada (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100)
);

# Kreiranje tabele za klasu izgradnje

DROP TABLE IF EXISTS klasa_izgradnje;

CREATE TABLE klasa_izgradnje (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(30)
);

-- SELECT * FROM klasa_izgradnje;

# Kreiranje tabele za tip grejanja

DROP TABLE IF EXISTS tip_grejanja;

CREATE TABLE tip_grejanja (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(200)
);

# Kreiranje glavne tabele za nekretnine

DROP TABLE IF EXISTS nekretnina;

CREATE TABLE nekretnina (
	id VARCHAR(20) PRIMARY KEY, # id nekretnine (unikatan niz znakova i cifara na sajtu nekretnine.rs cijim se koriscenjem moze rekreirati link)
    tip_id INT NOT NULL, # id tipa nekretnine -> 1 ili 2 u zavisnosti od toga da li je stan ili kuca u pitanju
    prodaja BOOL NOT NULL, # true ako je prodaja, false ako je iznajmljivanje
    cena DOUBLE NOT NULL, # cena izrazena u EUR
    drzava_id INT NULL, # id drzave
	grad_id INT NULL, # id grada
    deo_grada_id INT NULL, # id dela grada
    kvadratura DOUBLE NULL,
    godina_izgradnje INT NULL,
    klasa_id INT NULL, # id klase izgradnje
    povrsina_zemljista DOUBLE NULL, # samo za kuce (jedinica: ar [1 ar = 100 m^2])
    ukupna_spratnost INT NULL,
    sprat INT NULL, # samo za stanove
	uknjizenost BOOL NULL, # true ako je uknjizen, false ako nije uknjizen
    tip_grejanja_id INT NULL, # id tipa grejanja
    broj_soba INT NULL,
    broj_kupatila INT NULL,
    parking BOOL NULL, # true ako ima parking/garazu, false ako nema
    lift BOOL NULL, # true ako ima lift, false ako nema
    terasa BOOL NULL, # true ako ima terasu/lodju/balkon, false ako nema
	FOREIGN KEY (tip_id)
		REFERENCES tip_nekretnine (id)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    FOREIGN KEY (drzava_id)
		REFERENCES drzava (id)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    FOREIGN KEY (grad_id)
		REFERENCES grad (id)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    FOREIGN KEY (deo_grada_id)
		REFERENCES deo_grada (id)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    FOREIGN KEY (klasa_id)
		REFERENCES klasa_izgradnje (id)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    FOREIGN KEY (tip_grejanja_id)
		REFERENCES tip_grejanja (id)
        ON UPDATE RESTRICT ON DELETE CASCADE
);