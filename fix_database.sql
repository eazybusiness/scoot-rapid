-- Fix for missing qr_code column in rentals table
-- Execute this in Railway Shell

-- Add qr_code column if it doesn't exist
ALTER TABLE rentals ADD COLUMN qr_code VARCHAR(100) UNIQUE;

-- Update existing rentals with qr codes
UPDATE rentals SET qr_code = CONCAT('SR-RENTAL-', id, '-', UNIX_TIMESTAMP(created_at)) WHERE qr_code IS NULL;

-- Verify the column was added
DESCRIBE rentals;
