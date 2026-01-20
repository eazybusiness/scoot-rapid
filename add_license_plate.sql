-- Add license_plate column to scooters table
-- Execute this in Railway Shell or run migration

-- Add license_plate column if it doesn't exist
ALTER TABLE scooters ADD COLUMN license_plate VARCHAR(20);

-- Verify the column was added
DESCRIBE scooters;
