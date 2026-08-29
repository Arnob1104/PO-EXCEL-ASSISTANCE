-- Run this in the Supabase SQL editor.

-- One row per customer company (tenant)
create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

-- Links a Supabase auth user to an organization
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  org_id uuid not null references organizations(id) on delete cascade,
  role text not null default 'member', -- 'owner' | 'member', extend as needed
  created_at timestamptz not null default now()
);

-- The actual purchase order rows, scoped per org
create table purchase_orders (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  order_ref text not null,
  buyer text,
  style text,
  order_qty integer,
  ship_date date,
  status text,
  created_at timestamptz not null default now()
);

create index idx_purchase_orders_org_id on purchase_orders(org_id);
create index idx_profiles_org_id on profiles(org_id);

-- Row Level Security: even though the backend uses the service-role key
-- (which bypasses RLS) and manually filters by org_id, RLS is still enabled
-- here as defense-in-depth in case a future feature calls Supabase directly
-- from the frontend with a user's own token.
alter table organizations enable row level security;
alter table profiles enable row level security;
alter table purchase_orders enable row level security;

create policy "Users can see their own org"
  on organizations for select
  using (id in (select org_id from profiles where profiles.id = auth.uid()));

create policy "Users can see their own profile"
  on profiles for select
  using (id = auth.uid());

create policy "Users can see their own org's purchase orders"
  on purchase_orders for select
  using (org_id in (select org_id from profiles where profiles.id = auth.uid()));
