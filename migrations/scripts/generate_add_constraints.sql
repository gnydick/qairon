SELECT CONCAT('alter table ',conrelid::regclass,
              ' add constraint ', conname,' ',
              pg_get_constraintdef(oid), ';',chr(13))
FROM   pg_constraint
WHERE  contype = 'f'
  AND    connamespace = 'public'::regnamespace
ORDER  BY conrelid::regclass::text, contype DESC;


