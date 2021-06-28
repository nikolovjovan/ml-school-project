USE nekretnine;

-- Zadatak 3.a) 10 najzastupljenijih delova Beograda koji imaju najveci broj nekretnina u ponudi (i prodaja i iznajmljivanje)

SELECT dg.naziv AS 'Deo grada', COUNT(*) AS 'Broj nekretnina u ponudi'
FROM nekretnina AS n INNER JOIN deo_grada AS dg ON n.deo_grada_id = dg.id
WHERE grad_id = (SELECT id
				 FROM grad
                 WHERE naziv = 'Beograd')
GROUP BY deo_grada_id
ORDER BY COUNT(*) DESC
LIMIT 10;

SELECT COUNT(*) AS 'Broj nekretnina u ponudi'
FROM nekretnina AS n INNER JOIN deo_grada AS dg ON n.deo_grada_id = dg.id
WHERE grad_id = (SELECT id
				 FROM grad
                 WHERE naziv = 'Beograd') AND
	deo_grada_id IN (SELECT id
					 FROM deo_grada
					 WHERE naziv LIKE 'Novi Beograd%');

-- Zadatak 3.b) Broj stanova za prodaju prema kvadraturi

DROP FUNCTION IF EXISTS `broj_stanova_sa_kvadraturom_u_opsegu`;

DELIMITER $$

CREATE FUNCTION `broj_stanova_sa_kvadraturom_u_opsegu` (lo FLOAT, hi FLOAT)
RETURNS INT
DETERMINISTIC
BEGIN
	DECLARE result INT;
	IF lo = -1 THEN
		SELECT COUNT(*)
		FROM nekretnina
		WHERE prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan') AND
			kvadratura <= hi
		INTO result;
	ELSEIF hi = -1 THEN
		SELECT COUNT(*)
		FROM nekretnina
		WHERE prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan') AND
			kvadratura > lo
		INTO result;
	ELSE
		SELECT COUNT(*)
		FROM nekretnina
		WHERE prodaja = TRUE AND tip_id = (SELECT id FROM tip_nekretnine WHERE naziv = 'stan') AND
			kvadratura > lo AND kvadratura <= hi
		INTO result;
    END IF;
    RETURN result;
END $$

DELIMITER ;

SELECT
	broj_stanova_sa_kvadraturom_u_opsegu(0, 35) AS '(0, 35] m^2',
	broj_stanova_sa_kvadraturom_u_opsegu(35, 50) AS '(35, 50] m^2',
	broj_stanova_sa_kvadraturom_u_opsegu(50, 65) AS '(50, 65] m^2',
	broj_stanova_sa_kvadraturom_u_opsegu(65, 80) AS '(65, 80] m^2',
	broj_stanova_sa_kvadraturom_u_opsegu(80, 95) AS '(80, 95] m^2',
	broj_stanova_sa_kvadraturom_u_opsegu(95, 110) AS '(95, 110] m^2',
	broj_stanova_sa_kvadraturom_u_opsegu(110, -1) AS '(110, +inf) m^2';

-- Zadatak 3.c) Broj izgradjenih nekretnina po dekadama

DROP FUNCTION IF EXISTS `broj_izgradjenih_nekretnina_po_dekadama`;

DELIMITER $$

CREATE FUNCTION `broj_izgradjenih_nekretnina_po_dekadama` (lo FLOAT, hi FLOAT)
RETURNS INT
DETERMINISTIC
BEGIN
	DECLARE result INT;
	SELECT COUNT(*)
	FROM nekretnina
	WHERE godina_izgradnje BETWEEN lo AND hi
	INTO result;
    RETURN result;
END$$

DELIMITER ;

SELECT
	(SELECT COUNT(*) FROM nekretnina WHERE godina_izgradnje IS NOT NULL) AS 'Broj ponuda sa poznatom godinom izgradnje',
	(SELECT COUNT(*) FROM nekretnina WHERE godina_izgradnje IS NULL) AS 'Broj ponuda sa nepoznatom godinom izgradnje',
	(SELECT COUNT(*) FROM nekretnina WHERE klasa_id IS NOT NULL) AS 'Broj ponuda sa poznatom klasom izgradnje',
	(SELECT COUNT(*) FROM nekretnina WHERE klasa_id IS NULL) AS 'Broj ponuda sa nepoznatom klasom izgradnje';

SELECT
	broj_izgradjenih_nekretnina_po_dekadama(0, 1950) AS '(-inf, 1950]',
	broj_izgradjenih_nekretnina_po_dekadama(1951, 1960) AS '[1951, 1960]',
    broj_izgradjenih_nekretnina_po_dekadama(1961, 1970) AS '[1961, 1970]',
    broj_izgradjenih_nekretnina_po_dekadama(1971, 1980) AS '[1971, 1980]',
    broj_izgradjenih_nekretnina_po_dekadama(1981, 1990) AS '[1981, 1990]',
    broj_izgradjenih_nekretnina_po_dekadama(1991, 2000) AS '[1991, 2000]',
    broj_izgradjenih_nekretnina_po_dekadama(2001, 2010) AS '[2001, 2010]',
    broj_izgradjenih_nekretnina_po_dekadama(2011, 2020) AS '[2011, 2020]',
    broj_izgradjenih_nekretnina_po_dekadama(2021, 2030) AS '[2021, 2030]';

SELECT k.naziv AS 'Klasa', COUNT(*) AS 'Broj nekretnina'
FROM nekretnina n INNER JOIN klasa_izgradnje k ON n.klasa_id = k.id
GROUP BY n.klasa_id;

-- Zadatak 3.d) Broj i procentualni odnos nekretnina koje se prodaju i nekretnina koje se iznajmljuju za prvih 5 gradova sa najvecim brojem nekretnina

DROP PROCEDURE IF EXISTS `odnos_prodaja_iznajmljivanje_za_top_n_gradova`;

DELIMITER $$

CREATE PROCEDURE `odnos_prodaja_iznajmljivanje_za_top_n_gradova` (
	IN broj_gradova INT
)
BEGIN
	DECLARE grad_id INT;
    DECLARE grad_naziv VARCHAR(100);
    DECLARE broj_prodaja INT;
    DECLARE broj_iznajmljivanje INT;

	DECLARE done BOOLEAN DEFAULT FALSE;
    DECLARE grad_cursor CURSOR FOR
		SELECT n.grad_id, g.naziv
		FROM nekretnina n INNER JOIN grad g ON n.grad_id = g.id
		GROUP BY n.grad_id
		ORDER BY COUNT(*) DESC
		LIMIT broj_gradova;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	DROP TEMPORARY TABLE IF EXISTS rezultat;
    CREATE TEMPORARY TABLE rezultat (
		grad_id INT,
        grad_naziv VARCHAR(100),
        broj_oglasa_prodaja INT,
        broj_oglasa_iznajmljivanje INT
    );

	OPEN grad_cursor;

	petlja: LOOP
    
		IF done THEN
			LEAVE petlja;
		END IF;

		FETCH grad_cursor INTO grad_id, grad_naziv;

		IF done THEN
			LEAVE petlja;
		END IF;

		INSERT INTO rezultat (grad_id, grad_naziv, broj_oglasa_prodaja, broj_oglasa_iznajmljivanje) VALUES (
			grad_id,
			grad_naziv,
            (SELECT COUNT(*) FROM nekretnina n WHERE n.grad_id = grad_id AND prodaja = TRUE),
            (SELECT COUNT(*) FROM nekretnina n WHERE n.grad_id = grad_id AND prodaja = FALSE)
		);

	END LOOP petlja;

	CLOSE grad_cursor;

	SELECT
		r.grad_id AS 'Id grada',
		r.grad_naziv AS 'Grad',
        broj_oglasa_prodaja AS 'Broj oglasa za prodaju',
        broj_oglasa_iznajmljivanje AS 'Broj oglasa za iznajmljivanje',
        (broj_oglasa_prodaja / (broj_oglasa_prodaja + broj_oglasa_iznajmljivanje)) * 100 AS 'Udeo oglasa za prodaju [%]',
        (broj_oglasa_iznajmljivanje / (broj_oglasa_prodaja + broj_oglasa_iznajmljivanje)) * 100 AS 'Udeo oglasa za iznajmljivanje [%]'
	FROM rezultat r;
END $$

DELIMITER ;

CALL odnos_prodaja_iznajmljivanje_za_top_n_gradova(5);

-- Zadatak 3.e) Broj i procentualni odnos nekretnina svih nekretnina za prodaju, koje po ceni pripadaju jednom od sledecih opsega:
-- 1. manje od 49 999 EUR
-- 2. izmedju 50 000 i 99 999 EUR
-- 3. izmedju 100 000 i 149 999 EUR
-- 4. izmedju 150 000 i 199 999 EUR
-- 5. 200 000 EUR i vise

DROP FUNCTION IF EXISTS `broj_nekretnina_sa_cenom_u_opsegu`;

DELIMITER $$

CREATE FUNCTION `broj_nekretnina_sa_cenom_u_opsegu` (lo FLOAT, hi FLOAT)
RETURNS INT
DETERMINISTIC
BEGIN
	DECLARE result INT;
	IF lo IS NULL THEN
		SELECT COUNT(*)
		FROM nekretnina
		WHERE prodaja = TRUE AND cena <= hi
		INTO result;
	ELSEIF hi IS NULL THEN
		SELECT COUNT(*)
		FROM nekretnina
		WHERE prodaja = TRUE AND cena > lo
		INTO result;
	ELSE
		SELECT COUNT(*)
		FROM nekretnina
		WHERE prodaja = TRUE AND cena > lo AND cena <= hi
		INTO result;
    END IF;
    RETURN result;
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS `broj_i_udeo_prodaja_po_ceni`;

DELIMITER $$

CREATE PROCEDURE `broj_i_udeo_prodaja_po_ceni` ()
BEGIN
	DECLARE price_1 INT;
    DECLARE price_2 INT;
    DECLARE price_3 INT;
    DECLARE price_4 INT;
    DECLARE price_5 INT;
    DECLARE sum INT;

	SELECT broj_nekretnina_sa_cenom_u_opsegu(NULL, 49999)
    INTO price_1;
    
	SELECT broj_nekretnina_sa_cenom_u_opsegu(49999, 99999)
    INTO price_2;

	SELECT broj_nekretnina_sa_cenom_u_opsegu(99999, 149999)
    INTO price_3;

	SELECT broj_nekretnina_sa_cenom_u_opsegu(149999, 199999)
    INTO price_4;

	SELECT broj_nekretnina_sa_cenom_u_opsegu(199999, NULL)
    INTO price_5;

	SET sum = price_1 + price_2 + price_3 + price_4 + price_5;

	SELECT
		price_1 AS '(0, 49999] EUR',
        (price_1 / sum) * 100 AS 'Udeo [%]',
		price_2 AS '[50000, 99999] EUR',
        (price_2 / sum) * 100 AS 'Udeo [%]',
		price_3 AS '[100000, 149999] EUR',
        (price_3 / sum) * 100 AS 'Udeo [%]',
		price_4 AS '[150000, 199999] EUR',
        (price_4 / sum) * 100 AS 'Udeo [%]',
		price_5 AS '[200000, 249999] EUR',
        (price_5 / sum) * 100 AS 'Udeo [%]';
END $$

DELIMITER ;

CALL broj_i_udeo_prodaja_po_ceni;

-- Zadatak 3.f) Broj nekretnina za prodaju u Beogradu koje imaju parking, u odnosu na ukupan broj nekretnina za prodaju u Beogradu

DROP PROCEDURE IF EXISTS `broj_i_udeo_nekretnina_u_Beogradu_sa_parkingom`;

DELIMITER $$

CREATE PROCEDURE `broj_i_udeo_nekretnina_u_Beogradu_sa_parkingom` ()
BEGIN
	DECLARE broj_nekretnina_sa_parkingom INT;
    DECLARE ukupan_broj_nekretnina INT;

	SELECT COUNT(*)
    FROM nekretnina
    WHERE grad_id = (SELECT id FROM grad WHERE naziv = 'Beograd') AND parking = TRUE
    INTO broj_nekretnina_sa_parkingom;

	SELECT COUNT(*)
    FROM nekretnina
    WHERE grad_id = (SELECT id FROM grad WHERE naziv = 'Beograd')
    INTO ukupan_broj_nekretnina;

	SELECT
		broj_nekretnina_sa_parkingom AS 'Broj nekretnina sa parkingom u Beogradu',
        ukupan_broj_nekretnina AS 'Ukupan broj nekretnina u Beogradu',
        (broj_nekretnina_sa_parkingom / ukupan_broj_nekretnina) * 100 AS 'Udeo [%]';
END $$

DELIMITER ;

CALL broj_i_udeo_nekretnina_u_Beogradu_sa_parkingom;