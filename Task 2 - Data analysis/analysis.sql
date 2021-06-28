USE nekretnine;

-- Zadatak 2.a) Broj nekretnina za prodaju i iznjamljivanje

SELECT
	(SELECT COUNT(*)
     FROM nekretnina
     WHERE prodaja = TRUE) AS BrojNekretninaZaProdaju,
    (SELECT COUNT(*)
     FROM nekretnina
     WHERE prodaja = FALSE) AS BrojNekretninaZaIznajmljivanje;

-- Zadatak 2.b) Broj nekretnina za prodaju u svakom od gradova

SELECT g.naziv AS Grad, COUNT(*) AS BrojNekretninaZaProdaju
FROM nekretnina AS n INNER JOIN grad AS g ON n.grad_id = g.id
WHERE prodaja = TRUE
GROUP BY n.grad_id;

-- Zadatak 2.c) Broj uknjizenih i neuknjizenih kuca tj. stanova

SELECT
	(SELECT COUNT(*)
	 FROM nekretnina
	 WHERE tip_id = (SELECT id
					 FROM tip_nekretnine
                     WHERE naziv = 'kuca') AND uknjizenost = TRUE) AS BrojUknjizenihKuca,
	(SELECT COUNT(*)
	 FROM nekretnina
	 WHERE tip_id = (SELECT id
					 FROM tip_nekretnine
					 WHERE naziv = 'kuca') AND uknjizenost = FALSE) AS BrojNeuknjizenihKuca,
    (SELECT COUNT(*)
	 FROM nekretnina
	 WHERE tip_id = (SELECT id
					 FROM tip_nekretnine
					 WHERE naziv = 'stan') AND uknjizenost = TRUE) AS BrojUknjizenihStanova,
    (SELECT COUNT(*)
	 FROM nekretnina
	 WHERE tip_id = (SELECT id
					 FROM tip_nekretnine
					 WHERE naziv = 'stan') AND uknjizenost = FALSE) AS BrojNeuknjizenihStanova;

-- Zadatak 2.d) Rang lista prvih 30 najskupljih kuca tj. stanova za prodaju u Srbiji

SELECT id as Identifikator, cena as Cena
FROM nekretnina
WHERE tip_id = (SELECT id
				FROM tip_nekretnine
				WHERE naziv = 'kuca')
ORDER BY cena DESC
LIMIT 30;

SELECT id as Identifikator, cena as Cena
FROM nekretnina
WHERE tip_id = (SELECT id
				FROM tip_nekretnine
				WHERE naziv = 'stan')
ORDER BY cena DESC
LIMIT 30;

-- Zadatak 2.e) Rang lista prvih 100 najvecih kuca tj. stanova u Srbiji

SELECT id as Identifikator, kvadratura as 'Povrsina [m^2]'
FROM nekretnina
WHERE tip_id = (SELECT id
				FROM tip_nekretnine
				WHERE naziv = 'kuca')
ORDER BY kvadratura DESC
LIMIT 100;

SELECT id as Identifikator, kvadratura as 'Povrsina [m^2]'
FROM nekretnina
WHERE tip_id = (SELECT id
				FROM tip_nekretnine
				WHERE naziv = 'stan')
ORDER BY kvadratura DESC
LIMIT 100;

-- Zadatak 2.f) Rang lista svih nekretnina izgradjenih u 2020. godini prema ceni prodaje/iznajamljivanja opadajuce

-- Samo prodaja
SELECT id AS Identifikator, cena AS 'Cena prodaje'
FROM nekretnina
WHERE godina_izgradnje = 2020 AND prodaja = TRUE
ORDER BY cena DESC;

-- Samo iznajmljivanje
SELECT id AS Identifikator, cena AS 'Cena iznajmljivanja'
FROM nekretnina
WHERE godina_izgradnje = 2020 AND prodaja = FALSE
ORDER BY cena DESC;

-- Zajedno
DROP FUNCTION IF EXISTS `tip_transakcije`;

DELIMITER $$

CREATE FUNCTION `tip_transakcije` (prodaja BOOL)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
	DECLARE naziv_tipa VARCHAR(20);

    IF prodaja THEN
		SET naziv_tipa = 'Prodaja';
	ELSE
		SET naziv_tipa = 'Iznajmljivanje';
    END IF;

    RETURN (naziv_tipa);
END $$

DELIMITER ;

SELECT id AS Identifikator, tip_transakcije(prodaja) AS 'Tip transakcije', cena AS 'Cena'
FROM nekretnina
WHERE godina_izgradnje = 2020 AND cena != -1
ORDER BY cena DESC;

-- Zadatak 2.g) Top 30 nekretnina koje imaju:
-- 1. najveci broj soba unutar nekretnine
-- 2. najvecu kvadraturu (samo za stanove)
-- 3. najvecu povrsinu zemljista (samo za kuce)

SELECT id as Identifikator, broj_soba as 'Broj soba'
FROM nekretnina
ORDER BY broj_soba DESC
LIMIT 30;

SELECT id as Identifikator, kvadratura as 'Povrsina stana [m^2]'
FROM nekretnina
WHERE tip_id = (SELECT id
				FROM tip_nekretnine
				WHERE naziv = 'stan')
ORDER BY kvadratura DESC
LIMIT 30;

SELECT id as Identifikator, povrsina_zemljista as 'Povrsina zemljista [ar]'
FROM nekretnina
WHERE tip_id = (SELECT id
				FROM tip_nekretnine
				WHERE naziv = 'kuca')
ORDER BY povrsina_zemljista DESC
LIMIT 30;
