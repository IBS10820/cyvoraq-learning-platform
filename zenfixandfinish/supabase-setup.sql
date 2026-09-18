-- Zen Fix & Finish dedicated Supabase setup
-- Run once in Supabase SQL Editor for project: bzdvwtikqgmmcjazoeou

create extension if not exists pgcrypto;

create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid(),
  date date,
  type text,
  account text,
  amount numeric default 0,
  description text,
  created_at timestamptz not null default now()
);

alter table public.transactions enable row level security;

create or replace function public.is_zenfix_owner()
returns boolean
language sql
stable
as $$
  select lower(coalesce(auth.jwt()->>'email',''))='zenfixandfinish@gmail.com';
$$;

drop policy if exists zenfix_transactions_owner_all on public.transactions;
create policy zenfix_transactions_owner_all
on public.transactions
for all
to authenticated
using (public.is_zenfix_owner())
with check (public.is_zenfix_owner());

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.transactions to authenticated;
