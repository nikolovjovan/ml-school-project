# Za vise informacija procitati Izvestaj.txt

USE nekretnine;

# Kreiranje tabele za drzavu

DROP TABLE IF EXISTS drzava;

CREATE TABLE drzava (
	id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100)
);

# Dodavanje kolone drzava_id u tabeli nekretnina

ALTER TABLE nekretnina
ADD COLUMN drzava_id INT AFTER cena;

# Dodavanje stranog kljuca drzava_id u tabeli nekretnina

ALTER TABLE nekretnina
ADD CONSTRAINT fk_drzava_id
	FOREIGN KEY (drzava_id)
	REFERENCES drzava (id)
	ON UPDATE RESTRICT ON DELETE CASCADE;

# Ispravka par lose parsiranih oglasa (stranica nije sadrzala drzavu...)

SELECT * FROM drzava;

SELECT *
FROM nekretnina
WHERE drzava_id = (SELECT id FROM drzava WHERE naziv = 'Kalakača') OR
	drzava_id = (SELECT id FROM drzava WHERE naziv = 'Vojvođanska');

UPDATE nekretnina
SET drzava_id = 1
WHERE drzava_id = (SELECT id FROM drzava WHERE naziv = 'Kalakača') OR
	drzava_id = (SELECT id FROM drzava WHERE naziv = 'Vojvođanska');

DELETE FROM drzava
WHERE naziv = 'Kalakača' OR naziv = 'Vojvođanska';

# Filtriranje oglasa koji nisu iz Srbije

SELECT COUNT(*) AS 'Broj oglasa koji nisu iz Srbije'
FROM nekretnina n INNER JOIN drzava d ON n.drzava_id = d.id
WHERE d.naziv != 'Srbija';

SELECT n.id AS 'Id oglasa', d.naziv AS 'Drzava'
FROM nekretnina n INNER JOIN drzava d ON n.drzava_id = d.id
WHERE d.naziv != 'Srbija';

DELETE FROM nekretnina
WHERE drzava_id != (SELECT id FROM drzava WHERE naziv = 'Srbija');