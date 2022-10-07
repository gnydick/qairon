SELECT CONCAT('alter table ',conrelid::regclass, ' drop constraint ', conname,';')
FROM   pg_constraint
WHERE  contype = 'f'
  AND    connamespace = 'public'::regnamespace
ORDER  BY conrelid::regclass::text, contype DESC;