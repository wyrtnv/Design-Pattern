-- GameHub demo data (categories and products).
-- Users are created by seed.py, because passwords must be hashed by the application.
-- Run:  sqlite3 gamehub.db < database/seed.sql

INSERT OR IGNORE INTO categories (id, name) VALUES
    (1, 'Laptops'),
    (2, 'Keyboards'),
    (3, 'Mice'),
    (4, 'Headsets'),
    (5, 'Monitors');

INSERT OR IGNORE INTO products (id, category_id, name, description, price, stock, icon) VALUES
    (1, 1, 'ASUS ROG Strix G16',      'Intel i7, RTX 4060, 16 GB RAM, 165 Hz display',      749990, 5,  '💻'),
    (2, 1, 'Lenovo Legion 5 Pro',     'Ryzen 7, RTX 4070, 32 GB RAM, 2.5K 240 Hz',           899990, 3,  '💻'),
    (3, 2, 'Logitech G Pro X TKL',    'Tenkeyless mechanical, hot-swap GX switches',          69990, 12, '⌨️'),
    (4, 2, 'Razer BlackWidow V4',     'Full-size mechanical, RGB, media dial',                 89990, 8,  '⌨️'),
    (5, 3, 'Logitech G Pro X Superlight 2', 'Wireless, 60 g, HERO 2 sensor',                  64990, 15, '🖱️'),
    (6, 3, 'Razer DeathAdder V3',     'Ergonomic wired esports mouse, 59 g',                   34990, 20, '🖱️'),
    (7, 4, 'HyperX Cloud III',        'Wired headset, 53 mm drivers, detachable mic',          44990, 10, '🎧'),
    (8, 4, 'SteelSeries Arctis Nova 7','Wireless 2.4 GHz + Bluetooth, 38 h battery',           79990, 6,  '🎧'),
    (9, 5, 'Samsung Odyssey G5 27"',  '27" QHD, 165 Hz, 1 ms, curved VA',                     149990, 4,  '🖥️'),
    (10, 5, 'LG UltraGear 24GS60F',   '24" FHD IPS, 180 Hz, 1 ms',                             79990, 9,  '🖥️');
