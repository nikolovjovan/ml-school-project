# Kreiranje pomocne tabele za regresiju i klasifikaciju

DROP TABLE IF EXISTS nekretnina_subset;

CREATE TABLE nekretnina_subset (
	id VARCHAR(20) PRIMARY KEY, # id nekretnine (unikatan niz znakova i cifara na sajtu nekretnine.rs cijim se koriscenjem moze rekreirati link)
    cena DOUBLE NOT NULL, # cena [EUR]
    udaljenost DOUBLE NOT NULL, # udaljenost stana od centra Beograda [km]; racunato pomocu geolokacije, ako postoji, odnosno dela grada gde se stan nalazi, ako geolokacija ne postoji
    kvadratura DOUBLE NOT NULL, # kvadratura stana ako postoji, inace 10
    starost INT NOT NULL, # broj godina starosti nekretnine = 2021 - godina_izgradnje, ako godina_izgradnje postoji;
	                      # ako postoji klasa: 10 = novogradnja, 
    broj_soba INT NOT NULL, # broj soba u stanu ako postoji, inace 1
    spratnost INT NOT NULL # sprat na kom se nalazi stan, inace 0 (prizemlje)
);

# Kopiranje podataka u novu tabelu

DROP FUNCTION IF EXISTS `random_integer`;

CREATE FUNCTION random_integer(value_minimum INT, value_maximum INT)
RETURNS INT
DETERMINISTIC
COMMENT 'Gets a random integer between value_minimum and value_maximum, bounds included'
RETURN value_minimum + FLOOR(RAND() * (value_maximum - value_minimum + 1));

DROP FUNCTION IF EXISTS `odredi_starost`;

DELIMITER $$

CREATE FUNCTION `odredi_starost` (godina_izgradnje INT, klasa_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
	DECLARE starost INT DEFAULT 150;
	
    IF godina_izgradnje IS NOT NULL THEN
		SET starost = 2021 - godina_izgradnje;
	END IF;

	# Ako je izgradnja planirana do 10 godina unapred, inace je najverovatnije greska
    IF starost < -10 OR starost >= 150 THEN
		IF starost < -10 THEN
			SET starost = random_integer(-10, 0);
		ELSE
			SET starost = random_integer(1, 150);
		END IF;
	END IF;

	IF godina_izgradnje IS NOT NULL THEN
		RETURN starost;
	END IF;

	IF klasa_id IS NOT NULL THEN
		IF klasa_id = (SELECT id FROM klasa_izgradnje WHERE naziv = 'novogradnja') THEN
			SET starost = random_integer(-5, 10);
		ELSEIF klasa_id IN (SELECT id FROM klasa_izgradnje WHERE naziv = 'u izgradnji' OR naziv = 'u pripremi' OR naziv = 'završena izgradnja') THEN
			SET starost = random_integer(-10, 5);
		ELSEIF klasa_id = (SELECT id FROM klasa_izgradnje WHERE naziv = 'standardna gradnja') THEN
			SET starost = random_integer(0, 50);
		END IF;
	END IF;

	RETURN starost;
END $$

DELIMITER ;

SELECT * FROM klasa_izgradnje;

INSERT INTO nekretnina_subset (id, cena, udaljenost, kvadratura, starost, broj_soba, spratnost)
SELECT id, cena, 0, kvadratura, odredi_starost(godina_izgradnje, klasa_id), COALESCE(broj_soba, 1), COALESCE(sprat, 0)
FROM nekretnina
WHERE grad_id = (SELECT id FROM grad WHERE naziv = 'Beograd') AND prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan')
	AND cena >= 500 AND kvadratura IS NOT NULL AND kvadratura >= 5 AND kvadratura <= 1000;

# Dohvatanje id svih odabranih oglasa za koje treba izracunati distancu od centra Beograda

SELECT id
FROM nekretnina_subset;

# Eliminisanje/ispravljanje losih podataka (los oglas, lose parsiranje, itd.)

DELETE FROM nekretnina_subset
WHERE udaljenost > 20 OR kvadratura > 500;

UPDATE nekretnina_subset
SET broj_soba = 1
WHERE broj_soba = 0; # oglasi vode broj soba kao 0.5 i onda parser to pretvori u int sa vrednoscu 0

UPDATE nekretnina_subset
SET spratnost = 0
WHERE spratnost > 50; # oglasi sa prizemnim stanovima, iz nekog razloga sa ogromnom spratnoscu...

# Ponovno racunanje starosti nekretnine (ispravak greske u funkciji)

SELECT
	(SELECT COUNT(*) FROM nekretnina_subset) AS 'Broj stanova za prodaju u Beogradu',
	(SELECT COUNT(*)
	 FROM nekretnina
	 WHERE grad_id = (SELECT id FROM grad WHERE naziv = 'Beograd') AND prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan')
		 AND cena >= 500 AND kvadratura IS NOT NULL AND kvadratura >= 5 AND kvadratura <= 1000
		 AND godina_izgradnje IS NULL) AS 'Broj stanova za prodaju u Beogradu bez godine izgradnje',
	(SELECT COUNT(*)
	 FROM nekretnina
	 WHERE grad_id = (SELECT id FROM grad WHERE naziv = 'Beograd') AND prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan')
		 AND cena >= 500 AND kvadratura IS NOT NULL AND kvadratura >= 5 AND kvadratura <= 1000
		 AND klasa_id IS NULL) AS 'Broj stanova za prodaju u Beogradu bez klase izgradnje',
	(SELECT COUNT(*)
	 FROM nekretnina
	 WHERE grad_id = (SELECT id FROM grad WHERE naziv = 'Beograd') AND prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan')
		 AND cena >= 500 AND kvadratura IS NOT NULL AND kvadratura >= 5 AND kvadratura <= 1000
		 AND godina_izgradnje IS NULL AND klasa_id IS NULL) AS 'Broj stanova za prodaju u Beogradu bez godine i klase izgradnje';

SELECT ns.id, ns.starost AS 'Prethodna starost', tmp.starost AS 'Nova starost'
FROM nekretnina_subset ns INNER JOIN (
	SELECT id, odredi_starost(godina_izgradnje, klasa_id) AS starost
    FROM nekretnina
) tmp ON ns.id = tmp.id
WHERE ns.starost != tmp.starost;

UPDATE nekretnina_subset ns
INNER JOIN nekretnina n ON ns.id = n.id
SET ns.starost = odredi_starost(n.godina_izgradnje, n.klasa_id);

# Analiza problema sa kvadraturom stana

SELECT id, cena, kvadratura, cena / kvadratura AS cena_po_kvadratu
FROM nekretnina_subset
#WHERE kvadratura < 150
ORDER BY cena_po_kvadratu DESC;

DELETE FROM nekretnina_subset
#SELECT COUNT(*)
#SELECT id, cena, kvadratura, cena / kvadratura AS cena_po_kvadratu
#FROM nekretnina_subset
WHERE cena / kvadratura < 300 OR cena / kvadratura > 10000;

SELECT COUNT(*), AVG(kvadratura), AVG(cena), AVG(cena / kvadratura), AVG(udaljenost), AVG(starost)
FROM nekretnina_subset
WHERE (kvadratura BETWEEN 0 AND 50) AND cena > 250000;

SELECT AVG(kvadratura), AVG(cena), AVG(cena / kvadratura), AVG(udaljenost)
#SELECT COUNT(*)
FROM nekretnina_subset
#WHERE (kvadratura BETWEEN 100 AND 400)
#WHERE (kvadratura BETWEEN 100 AND 250)
WHERE (kvadratura BETWEEN 250 AND 400)
	AND cena > 500000;