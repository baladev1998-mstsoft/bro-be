-- BRO (Best Rooms Only) — Full Schema SQL for PostgreSQL
-- Single execution script
-- Requires: CREATE EXTENSION pgcrypto; (used here)
-- Run as a single transaction for atomic creation if you like.

BEGIN;

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------------------------
-- ENUMS / TYPES
-- -----------------------------------------------------------------------------
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'booking_status') THEN
    CREATE TYPE booking_status AS ENUM (
      'pending',
      'confirmed',
      'cancelled',
      'checked_in',
      'checked_out',
      'no_show',
      'refunded'
    );
  END IF;
END
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- CORE: users, roles, permissions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  is_builtin boolean DEFAULT false,
  is_deleted boolean DEFAULT false,
  created_by uuid,
  created_at timestamptz DEFAULT now(),
  updated_by uuid,
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS permissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  description text,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS role_permissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id uuid NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id uuid NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE(role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  password_hash text,
  full_name text,
  phone text,
  is_active boolean DEFAULT true,
  is_deleted boolean DEFAULT false,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  created_by uuid,
  updated_at timestamptz DEFAULT now(),
  updated_by uuid
);

CREATE TABLE IF NOT EXISTS user_roles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id uuid NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  scope jsonb DEFAULT '{}'::jsonb,
  assigned_by uuid,
  assigned_at timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now(),
  UNIQUE(user_id, role_id, (scope::text))
);

-- -----------------------------------------------------------------------------
-- DESTINATIONS, SEO, SITE PAGES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seo_metadata (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type text,
  entity_id uuid,
  meta_title text,
  meta_description text,
  meta_keywords text,
  canonical_url text,
  robots text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS destinations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  country text,
  region text,
  latitude numeric(9,6),
  longitude numeric(9,6),
  description text,
  seo_id uuid REFERENCES seo_metadata(id) ON DELETE SET NULL,
  is_published boolean DEFAULT false,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS site_pages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text UNIQUE,
  title text,
  body text,
  blocks jsonb DEFAULT '[]'::jsonb,
  seo_id uuid REFERENCES seo_metadata(id) ON DELETE SET NULL,
  is_published boolean DEFAULT false,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- PROPERTIES & ASSIGNMENTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS properties (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  destination_id uuid REFERENCES destinations(id) ON DELETE SET NULL,
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  property_type text,
  address text,
  contact_email text,
  contact_phone text,
  overview text,
  rating numeric(2,1) DEFAULT 0,
  is_published boolean DEFAULT false,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  created_by uuid,
  updated_at timestamptz DEFAULT now(),
  updated_by uuid
);

CREATE TABLE IF NOT EXISTS property_assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id uuid NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assignment_role text NOT NULL, -- 'property_admin','property_user','manager'
  scope jsonb DEFAULT '{}'::jsonb,
  is_active boolean DEFAULT true,
  assigned_by uuid,
  assigned_at timestamptz DEFAULT now(),
  revoked_by uuid,
  revoked_at timestamptz,
  notes text,
  created_at timestamptz DEFAULT now(),
  UNIQUE(property_id, user_id, assignment_role)
);

-- -----------------------------------------------------------------------------
-- MEDIA — S3-centric media + polymorphic mapping
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL DEFAULT 's3',
  s3_bucket text,
  s3_key text,                -- canonical S3 key
  s3_etag text,
  s3_version_id text,
  url text,                   -- cached public or CDN URL
  cdn_url text,
  file_name text,
  content_type text,
  size_bytes bigint,
  width integer,
  height integer,
  storage_class text,
  acl text,
  meta jsonb DEFAULT '{}'::jsonb,
  checksum text,
  uploaded_by uuid,
  uploaded_at timestamptz DEFAULT now(),
  is_deleted boolean DEFAULT false
);

CREATE TABLE IF NOT EXISTS entity_media (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  media_id uuid NOT NULL REFERENCES media(id) ON DELETE CASCADE,
  entity_type text NOT NULL,   -- 'property','room_type','package','itinerary'
  entity_id uuid NOT NULL,
  role text DEFAULT 'gallery', -- 'hero','thumbnail','gallery','policy_doc'
  alt_text text,
  caption text,
  position integer DEFAULT 0,
  is_primary boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  UNIQUE(media_id, entity_type, entity_id)
);

-- -----------------------------------------------------------------------------
-- ROOM TYPES, ROOMS, INVENTORY, TARIFFS, BLACKOUT
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS room_types (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id uuid NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  name text NOT NULL,
  slug text,
  capacity integer NOT NULL DEFAULT 2,
  base_tariff numeric(12,2) NOT NULL DEFAULT 0,
  description text,
  max_adults integer DEFAULT 2,
  max_children integer DEFAULT 0,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rooms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id uuid NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  room_type_id uuid REFERENCES room_types(id) ON DELETE SET NULL,
  room_number text,
  status text DEFAULT 'available',
  created_at timestamptz DEFAULT now(),
  is_deleted boolean DEFAULT false
);

CREATE TABLE IF NOT EXISTS room_inventories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  room_type_id uuid NOT NULL REFERENCES room_types(id) ON DELETE CASCADE,
  inventory_date date NOT NULL,
  available_count integer NOT NULL DEFAULT 0,
  is_blocked boolean DEFAULT false,
  note text,
  updated_by uuid,
  updated_at timestamptz DEFAULT now(),
  UNIQUE(room_type_id, inventory_date)
);

CREATE TABLE IF NOT EXISTS room_tariffs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  room_type_id uuid NOT NULL REFERENCES room_types(id) ON DELETE CASCADE,
  tariff_date date NOT NULL,
  price numeric(12,2) NOT NULL,
  currency text NOT NULL DEFAULT 'INR',
  min_stay integer DEFAULT 1,
  created_by uuid,
  created_at timestamptz DEFAULT now(),
  UNIQUE(room_type_id, tariff_date)
);

CREATE TABLE IF NOT EXISTS blackout_dates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  room_type_id uuid REFERENCES room_types(id) ON DELETE CASCADE,
  start_date date NOT NULL,
  end_date date NOT NULL,
  reason text,
  created_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- BOOKING, BOOKING ITEMS, PAYMENTS, BOOKING ADDONS (amenities at booking time)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE SET NULL,
  property_id uuid REFERENCES properties(id) ON DELETE SET NULL,
  total_amount numeric(12,2) NOT NULL DEFAULT 0,
  currency text DEFAULT 'INR',
  status booking_status DEFAULT 'pending',
  booking_reference text UNIQUE,
  contact_name text,
  contact_email text,
  contact_phone text,
  meta jsonb DEFAULT '{}'::jsonb,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS booking_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id uuid NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  room_type_id uuid REFERENCES room_types(id) ON DELETE SET NULL,
  check_in date NOT NULL,
  check_out date NOT NULL,
  nights integer NOT NULL,
  qty integer NOT NULL DEFAULT 1,
  price_per_night numeric(12,2) NOT NULL,
  total_price numeric(12,2) NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id uuid REFERENCES bookings(id) ON DELETE SET NULL,
  amount numeric(12,2) NOT NULL,
  currency text NOT NULL DEFAULT 'INR',
  payment_method text,
  payment_provider text,
  status text,
  provider_response jsonb,
  created_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- AMENITIES (catalog), AMENITY OPTIONS, PROPERTY AMENITIES, BOOKING ADDONS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS amenities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  description text,
  category text,
  requires_configuration boolean DEFAULT false,
  is_chargeable boolean DEFAULT false,
  default_price numeric(12,2),
  currency text DEFAULT 'INR',
  meta jsonb DEFAULT '{}'::jsonb,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS amenity_options (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  amenity_id uuid NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
  code text NOT NULL,
  name text NOT NULL,
  description text,
  price numeric(12,2) DEFAULT 0,
  currency text DEFAULT 'INR',
  meta jsonb DEFAULT '{}'::jsonb,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(amenity_id, code)
);

CREATE TABLE IF NOT EXISTS property_amenities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id uuid NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  amenity_id uuid NOT NULL REFERENCES amenities(id) ON DELETE RESTRICT,
  enabled boolean DEFAULT true,
  is_chargeable boolean DEFAULT false,
  price numeric(12,2),
  currency text DEFAULT 'INR',
  apply_on text DEFAULT 'per_stay',
  config jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(property_id, amenity_id)
);

CREATE TABLE IF NOT EXISTS booking_addons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id uuid NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
  amenity_id uuid REFERENCES amenities(id) ON DELETE SET NULL,
  amenity_option_id uuid REFERENCES amenity_options(id) ON DELETE SET NULL,
  property_amenity_id uuid REFERENCES property_amenities(id) ON DELETE SET NULL,
  name text NOT NULL,
  price numeric(12,2) NOT NULL DEFAULT 0,
  currency text DEFAULT 'INR',
  qty integer DEFAULT 1,
  total_price numeric(12,2) NOT NULL DEFAULT 0,
  notes text,
  created_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- POLICIES (catalog) + PROPERTY POLICIES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS policies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  title text NOT NULL,
  description text,
  category text,
  meta jsonb DEFAULT '{}'::jsonb,
  is_deleted boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS property_policies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id uuid NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  policy_id uuid NOT NULL REFERENCES policies(id) ON DELETE RESTRICT,
  content text,
  short_text text,
  effective_from date,
  effective_to date,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(property_id, policy_id)
);

-- -----------------------------------------------------------------------------
-- PACKAGES & ITINERARIES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS packages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  slug text UNIQUE,
  description text,
  base_price numeric(12,2),
  duration_days integer,
  inclusions text,
  exclusions text,
  destination_id uuid REFERENCES destinations(id) ON DELETE SET NULL,
  is_published boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS package_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  package_id uuid NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
  item_type text NOT NULL,
  item_ref uuid,
  day integer DEFAULT 1,
  description text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS itineraries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  slug text UNIQUE,
  duration_days integer,
  description text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS itinerary_days (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  itinerary_id uuid NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
  day integer NOT NULL,
  title text,
  details text,
  created_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- REVIEWS & RATINGS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE SET NULL,
  property_id uuid REFERENCES properties(id) ON DELETE CASCADE,
  booking_id uuid REFERENCES bookings(id) ON DELETE SET NULL,
  rating integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
  title text,
  comment text,
  is_published boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- OFFERS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS offers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  code text UNIQUE,
  description text,
  start_date date,
  end_date date,
  discount jsonb, -- {type:'percent'|'fixed', value:10}
  applicable_to jsonb DEFAULT '{}'::jsonb,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- AUDIT / ACTIVITY LOGS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  entity_type text,
  entity_id uuid,
  action text,
  payload jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS activity_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  ip text,
  user_agent text,
  event text,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- INDEXES
-- -----------------------------------------------------------------------------
-- Core
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Properties & dest
CREATE INDEX IF NOT EXISTS idx_properties_destination ON properties(destination_id);
CREATE INDEX IF NOT EXISTS idx_properties_slug ON properties(slug);

-- Property assignments
CREATE INDEX IF NOT EXISTS idx_property_assignments_property ON property_assignments(property_id);
CREATE INDEX IF NOT EXISTS idx_property_assignments_user ON property_assignments(user_id);

-- Media
CREATE INDEX IF NOT EXISTS idx_media_s3_key ON media(s3_key);
CREATE INDEX IF NOT EXISTS idx_entity_media_entity ON entity_media(entity_type, entity_id, position);

-- Room / inventory
CREATE INDEX IF NOT EXISTS idx_room_inventory_room_date ON room_inventories(room_type_id, inventory_date);
CREATE INDEX IF NOT EXISTS idx_room_tariffs_room_date ON room_tariffs(room_type_id, tariff_date);

-- Bookings
CREATE INDEX IF NOT EXISTS idx_bookings_user_status ON bookings(user_id, status);
CREATE INDEX IF NOT EXISTS idx_bookings_property ON bookings(property_id);

-- Amenities
CREATE INDEX IF NOT EXISTS idx_amenities_code ON amenities(code);
CREATE INDEX IF NOT EXISTS idx_property_amenities_property ON property_amenities(property_id);

-- Policies
CREATE INDEX IF NOT EXISTS idx_policies_code ON policies(code);

-- Reviews
CREATE INDEX IF NOT EXISTS idx_reviews_property ON reviews(property_id);

-- Audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);

-- -----------------------------------------------------------------------------
-- CONSTRAINT / CHECKS (examples)
-- -----------------------------------------------------------------------------
ALTER TABLE room_inventories
  ADD CONSTRAINT chk_room_inventories_non_negative_available CHECK (available_count >= 0);

-- -----------------------------------------------------------------------------
-- FINAL NOTES: triggers, RLS, and further enhancements
-- - Consider writing DB triggers to maintain `updated_at` and write audit_logs on DML.
-- - Consider Row Level Security (RLS) policies for property-scoped access if using Postgres roles.
-- - Add background job to purge soft-deleted rows physically if required.
-- -----------------------------------------------------------------------------

COMMIT;
