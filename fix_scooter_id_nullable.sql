-- Fix scooter_id column to allow NULL values
-- Execute this in Railway Shell to enable scooter deletion

-- Make scooter_id nullable to allow rentals without scooter reference
ALTER TABLE rentals MODIFY COLUMN scooter_id INT NULL;

-- Verify the change
DESCRIBE rentals;

-- Check current rentals
SELECT id, rental_code, scooter_id, status FROM rentals LIMIT 10;
