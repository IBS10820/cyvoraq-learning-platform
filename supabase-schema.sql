-- CYVORAQ Learning Platform schema
-- Run once in Supabase SQL Editor.

create extension if not exists pgcrypto;

create or replace function public.is_master()
returns boolean language sql stable security definer set search_path=public as $$
  select lower(coalesce(auth.jwt()->>'email',''))='tigertechy1@gmail.com';
$$;

create table if not exists public.students(
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid unique,
  roll_number text unique not null,
  full_name text not null,
  email text unique not null,
  phone text,
  preferred_name text,
  status text not null default 'active' check(status in('active','paused','cancelled')),
  progress numeric default 0,
  attempts integer default 0,
  hours numeric default 0,
  cancelled_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists public.fee_accounts(
  id uuid primary key default gen_random_uuid(),
  student_id uuid unique references public.students(id) on delete cascade,
  plan text,
  method text,
  total_fee numeric default 0,
  paid numeric default 0,
  due numeric default 0,
  status text default 'pending' check(status in('paid','pending','failed','blocked','overdue')),
  access_override boolean default false,
  next_due timestamptz,
  voucher_until timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists public.certificates(
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.students(id) on delete cascade,
  module text not null,
  certificate_no text unique not null,
  issued_at timestamptz default now()
);

create table if not exists public.messages(
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.students(id) on delete cascade,
  sender_role text not null check(sender_role in('master','student')),
  body text not null,
  created_at timestamptz default now(),
  read_at timestamptz
);

create table if not exists public.transactions(
  id uuid primary key default gen_random_uuid(),
  date date not null default current_date,
  type text not null check(type in('income','expense','receivable','payable','asset','liability')),
  account text not null,
  amount numeric not null default 0,
  description text,
  created_at timestamptz default now()
);

create table if not exists public.vouchers(
  id uuid primary key default gen_random_uuid(),
  code text unique not null check(length(code)=12),
  months integer not null check(months in(3,6,12)),
  created_at timestamptz default now(),
  expires_at timestamptz,
  redeemed_by uuid references public.students(id),
  redeemed_at timestamptz
);

alter table public.students enable row level security;
alter table public.fee_accounts enable row level security;
alter table public.certificates enable row level security;
alter table public.messages enable row level security;
alter table public.transactions enable row level security;
alter table public.vouchers enable row level security;

drop policy if exists students_master_all on public.students;
create policy students_master_all on public.students for all to authenticated using(public.is_master()) with check(public.is_master());
drop policy if exists students_self_select on public.students;
create policy students_self_select on public.students for select to authenticated using(auth_user_id=auth.uid());
drop policy if exists students_self_update on public.students;
create policy students_self_update on public.students for update to authenticated using(auth_user_id=auth.uid()) with check(auth_user_id=auth.uid());

drop policy if exists fees_master_all on public.fee_accounts;
create policy fees_master_all on public.fee_accounts for all to authenticated using(public.is_master()) with check(public.is_master());
drop policy if exists fees_self_select on public.fee_accounts;
create policy fees_self_select on public.fee_accounts for select to authenticated using(exists(select 1 from public.students s where s.id=student_id and s.auth_user_id=auth.uid()));

drop policy if exists cert_master_all on public.certificates;
create policy cert_master_all on public.certificates for all to authenticated using(public.is_master()) with check(public.is_master());
drop policy if exists cert_self_select on public.certificates;
create policy cert_self_select on public.certificates for select to authenticated using(exists(select 1 from public.students s where s.id=student_id and s.auth_user_id=auth.uid()));

drop policy if exists msg_master_all on public.messages;
create policy msg_master_all on public.messages for all to authenticated using(public.is_master()) with check(public.is_master());
drop policy if exists msg_self_select on public.messages;
create policy msg_self_select on public.messages for select to authenticated using(exists(select 1 from public.students s where s.id=student_id and s.auth_user_id=auth.uid()));
drop policy if exists msg_self_insert on public.messages;
create policy msg_self_insert on public.messages for insert to authenticated with check(sender_role='student' and exists(select 1 from public.students s where s.id=student_id and s.auth_user_id=auth.uid()));

drop policy if exists tx_master_all on public.transactions;
create policy tx_master_all on public.transactions for all to authenticated using(public.is_master()) with check(public.is_master());

drop policy if exists voucher_master_all on public.vouchers;
create policy voucher_master_all on public.vouchers for all to authenticated using(public.is_master()) with check(public.is_master());
drop policy if exists voucher_student_select on public.vouchers;
create policy voucher_student_select on public.vouchers for select to authenticated using(redeemed_by is null or exists(select 1 from public.students s where s.id=redeemed_by and s.auth_user_id=auth.uid()));
drop policy if exists voucher_student_update on public.vouchers;
create policy voucher_student_update on public.vouchers for update to authenticated using(redeemed_by is null) with check(exists(select 1 from public.students s where s.id=redeemed_by and s.auth_user_id=auth.uid()));

alter publication supabase_realtime add table public.messages;

-- Privacy approach:
-- Student personal data is retained only while necessary for learning, safeguarding,
-- contractual or legal purposes. Financial records are separated from learning profiles.
-- Cancelled records should be reviewed and anonymised/deleted according to the documented
-- retention schedule and any overriding UK legal requirement. Do not retain personal data forever.
