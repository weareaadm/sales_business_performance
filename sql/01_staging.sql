-- ============================================================================
-- SCRIPT: 01_staging.sql (Carga de dimensiones estáticas)
-- ============================================================================

PRINT 'Iniciando carga de dimensiones estáticas en Staging...';

-- 1. Carga de stg_demo1.regions
TRUNCATE TABLE stg_demo1.regions;
INSERT INTO stg_demo1.regions (region_id, region_name, country) VALUES
(1, 'Lima Norte', 'Peru'),
(2, 'Lima Sur', 'Peru'),
(3, 'Lima Este', 'Peru'),
(4, 'Lima Centro', 'Peru'),
(5, 'Lima Moderna', 'Peru'),
(6, 'Callao', 'Peru'),
(7, 'Lima Balnearios', 'Peru'),
(8, 'Lima Periurbana', 'Peru');

-- 2. Carga de stg_demo1.warehouses
TRUNCATE TABLE stg_demo1.warehouses;
INSERT INTO stg_demo1.warehouses (warehouse_id, warehouse_name, region_id) VALUES
(1, 'WH-LimaNorte-01', 1),
(2, 'WH-LimaSur-01', 2),
(3, 'WH-LimaEste-01', 3),
(4, 'WH-LimaCentro-01', 4),
(5, 'WH-LimaModerna-01', 5),
(6, 'WH-Callao-01', 6), 
(7, 'WH-Balnearios-01', 7),
(8, 'WH-Periurbana-01', 8);

PRINT '✓ Dimensiones estáticas cargadas exitosamente.';
GO